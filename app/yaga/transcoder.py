from __future__ import absolute_import, division, unicode_literals

# (C)2015 Yaga Mobile, Inc -- file created by dlg 2/4/2015

import logging

import boto
from boto.s3.connection import S3Connection
from boto.s3.connection import Location
import boto.sns
import boto.sqs
import boto.elastictranscoder
import boto.exception

logger = logging.getLogger(__name__)

# Role has transcoding and S3 perms.
TRANSCODING_ROLE_ARN = 'arn:aws:iam::609367773239:role/transcoding-role'
INPUT_BUCKET_NAME = 'test-yaga-video-input-bucket'
OUTPUT_BUCKET_NAME = 'test-yaga-video-output-bucket'
INPUT_BASE_PATH = 'media/posts/'
JOB_TOPIC_NAME ='test-yaga-transcode-job-status-topic'
JOB_ERROR_TOPIC_NAME ='test-yaga-transcode-job-error-topic'
JOB_QUEUE_NAME = 'test-yaga-transcode-job-status-queue'
PIPELINE_NAME = 'test-yaga-transcode-pipeline'
YAGA_PRESET_PREFIX = 'Yaga'

# ElasticTranscoder only allows: auto, 10, 15, 23.97, 24, 25, 29.97, 30, 50, 60
OUTPUT_FRAME_RATE = 15 # iOS default 30

# Note: boto will normally pick up credentials from .boto.  But can override with env vars
#   AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY.
#  If AWS_CREDENTIAL_FILE if will use that.

#debug
# Turn on for detailed debugging of boto layer
# boto.set_stream_logger('boto')

# configures S3.  Should be called once per account
# XXX we should make it check each step is done/correct so it can automatically check on deploy
def setup_transcoder():
    setup_s3()
    complete_topic_arn, error_topic_arn = setup_queues()
    setup_cloudfront()
    setup_pipeline(complete_topic_arn, error_topic_arn)
    setup_presets()

PRESETS = []
def get_presets():
    del PRESETS[:]
    transcode = boto.elastictranscoder.connect_to_region('us-west-2')
    l = transcode.list_presets(ascending='false')  # reverse-chron order.  *Assume first page contains all relevant formats
    for preset in l['Presets']:
        if preset['Description'].startswith(YAGA_PRESET_PREFIX):
            PRESETS.append((preset['Name'], preset['Id']))
    logger.debug('Found %d presets.  Currently should be 3.' % len(PRESETS))
    return PRESETS

def get_pipeline():
    toret = None
    transcode = boto.elastictranscoder.connect_to_region('us-west-2')
    pipelines = transcode.list_pipelines()  # assume 1 page
    for pipeline in pipelines['Pipelines']:
        if pipeline['Name']==PIPELINE_NAME:
            toret = pipeline
    return toret

def build_key(group_id, video_id, is_input, format=None, extension=''):
    if is_input:
        return '%s%s/%s%s' % (INPUT_BASE_PATH, group_id, video_id, extension)
    else:
        return '%s/%s_%s%s' % (group_id, video_id, format, extension)

#PIPELINE_ID = get_pipeline()['Id']

def start_job(group_id, video_id):
    transcode = boto.elastictranscoder.connect_to_region('us-west-2')

    input_object = {
        'Key' : build_key(group_id, video_id, True),
        'Container' : 'auto',
        'FrameRate': 'auto',
        'Resolution': 'auto',
        'AspectRatio': 'auto'
    }

    output_objects = []
    for preset_data in PRESETS:
        format = preset_data[0]
        preset = preset_data[1]
        output_objects.append({
            'Key': build_key(group_id, video_id, False, format),
            'PresetId' : preset,
        })

    job = transcode.create_job(PIPELINE_ID, input_name=input_object, outputs=output_objects)
    if not job:
        logger.error('Failed to create job')
    return job

def setup_s3():
    logger.debug('Setting up S3 for transcoder')

    s3_conn = S3Connection()

    # Create input video bucket
    # XXX check if exists or trap S3CreateError(409)
    try:
        input_bucket = s3_conn.create_bucket(INPUT_BUCKET_NAME, location=Location.USWest2)
    # ??? set up perms
    except boto.exception.S3CreateError as e:
        if e.status==409 and e.code=='BucketAlreadyOwnedByYou':
            logger.debug('Bucket %s already exists, skipping' % e.bucket)
        else:
            raise

    # Create output video bucket
    try:
        output_bucket = s3_conn.create_bucket(OUTPUT_BUCKET_NAME, location=Location.USWest2)
    except boto.exception.S3CreateError as e:
        if e.status==409 and e.code=='BucketAlreadyOwnedByYou':
            logger.debug('Bucket %s already exists, skipping' % e.bucket)
        else:
            raise

    if output_bucket:
        output_bucket.set_acl('public-read')  # XXX maybe make readable only by cloud front
    else:
        logger.debug('No output bucket, not setting ACL')

def setup_queues():
    logger.debug('Setting up SNS/SQS for transcoder')

    # Create SNS topic for job status
    sns_conn = boto.sns.connect_to_region('us-west-2')
    job_complete_topic = sns_conn.create_topic(JOB_TOPIC_NAME)
    # And one for errors
    job_error_topic = sns_conn.create_topic(JOB_ERROR_TOPIC_NAME)

    # Create SQS queue for job complete
    sqs_conn = boto.sqs.connect_to_region('us-west-2')
    job_complete_queue = sqs_conn.create_queue(JOB_QUEUE_NAME)
    # if exists and purge
    # job_complete_queue.purge()

    # Subscribe sqs queue to sns topic
    #job_complete_topic.subscribe_sqs_queue(job_complete_queue)
    complete_topic_arn = job_complete_topic['CreateTopicResponse']['CreateTopicResult']['TopicArn']
    error_topic_arn = job_error_topic['CreateTopicResponse']['CreateTopicResult']['TopicArn']
    subscription = sns_conn.subscribe_sqs_queue(complete_topic_arn, job_complete_queue)

    return complete_topic_arn, error_topic_arn

def setup_cloudfront():
    logger.debug('Setting up CloudFront for transcoder')

    # Set up CloudFront
    cf = boto.connect_cloudfront()
    # Create OAI
    try:
        oai = cf.create_origin_access_identity(comment='OAI for serving videos')
    except boto.cloudfront.exception.CloudFrontServerError as e:
        if e.status==403 and e.error_code=='AccessDenied':
            logger.error('IAM role can not create OAI')
        else:
            logger.exception('Problem trying to create CF OAI')

    # Create distribution
    from boto.cloudfront.distribution import DistributionConfig
    from boto.cloudfront.exception import CloudFrontServerError

    # XXX use/check OAI
    origin = boto.cloudfront.origin.S3Origin(OUTPUT_BUCKET_NAME)
    try:
        distro = oai.connection.create_distribution(origin=origin, enabled=True, comment='Video serving Distribution') # ??? cnames
    except boto.cloudfront.exception.CloudFrontServerError as e:
        if e.status==403 and e.error_code=='AccessDenied':
            logger.error('OAI can not create Distribution')
        else:
            logger.exception('Problem trying to create CloudFront distribution from OAI')

def setup_pipeline(complete_topic_arn, error_topic_arn):
    logger.debug('Setting up Pipeline for transcoder')

    # Create pipeline
    transcode = boto.elastictranscoder.connect_to_region('us-west-2')
    pipeline = transcode.create_pipeline(PIPELINE_NAME, INPUT_BUCKET_NAME, OUTPUT_BUCKET_NAME, TRANSCODING_ROLE_ARN, {'Progressing':'', 'Completed': complete_topic_arn, 'Warning':'', 'Error':error_topic_arn})
    if not pipeline:
        logger.error('Failed to create pipeline')

PRESET_VIDEO_BASE = {
        'Codec':'H.264',
        'Profile': 'baseline',
        'BitRate': 'auto',
        'FrameRate': str(OUTPUT_FRAME_RATE),
        'SizingPolicy': 'ShrinkToFill',
        'FixedGOP': 'false',
        'KeyframesMaxDist': '90',
        'CodecOptions': {'MaxReferenceFrames':'3', 'Profile':'baseline', 'Level':'3.1'},
        'DisplayAspectRatio': 'auto',
        'PaddingPolicy': 'NoPad',
    }

PRESET_THUMBNAILS_BASE = {
        'Format': 'jpg',
        'Interval': '1',
        'MaxWidth': '32',
        'MaxHeight': '32',
        'PaddingPolicy': 'NoPad',
        'SizingPolicy': 'ShrinkToFill'
    }

PRESET_AUDIO_BASE = {
        'Codec': 'AAC',
        'Channels': '0',  # Suppress audio output
        'SampleRate': '44100',
        'BitRate': '128',
    }

def build_preset(name, max_width, max_height, description=None):
    video = PRESET_VIDEO_BASE.copy()
    video['MaxWidth'] = str(max_width)
    video['MaxHeight'] = str(max_height)
    audio = PRESET_AUDIO_BASE.copy()
    return transcode.create_preset(name, description, 'mp4', video, audio, PRESET_THUMBNAILS_BASE)

PRESETS = [('372x330', 372, 330, 'iPhone 6'),  # 750x1334 screen; 2px grid borders -> 373x331 round to even
    ('538x478', 538, 478, 'iPhone 6+'),  # 1080x1920; 2px grid borders
    ('318x478', 538, 282, 'iPhone 5')  # 640x1136; 2px grid borders
]

def setup_presets():
    logger.debug('Setting up Presets for transcoder')

    transcode = boto.elastictranscoder.connect_to_region('us-west-2')

    # XXX maybe check if they already exist?
    preset_list = []
    for p in PRESETS:
        name = '%s %s' % (YAGA_PRESET_PREFIX, p[3])
        preset = build_preset(p[0], p[1], p[2], name)
        preset_list.append((p[0], preset))


