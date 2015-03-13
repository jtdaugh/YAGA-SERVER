#!/usr/bin/env python
import boto.sns
import boto.sqs
import boto.elastictranscoder
from boto.s3.connection import S3Connection

AWS_REGION = 'eu-west-1'
AWS_ACCESS_KEY_ID = 'AKIAJX5RPG57OST42XWQ'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'yaga-in'

PRESET_PREFIX = 'Yaga'
OUTPUT_FRAME_RATE = 15

PIPELINE_NAME = 'yaga_pipeline'
JOB_COMPLETE_TOPIC = 'yaga_sns_complete'
JOB_COMPLETE_QUEUE = 'yaga_sqs_complete'
JOB_ERROR_TOPIC = 'yaga_sns_error'
JOB_ERROR_QUEUE = 'yaga_sqs_error'
TRANSCODING_ROLE_ARN = 'arn:aws:elastictranscoder:eu-west-1:679876760017:pipeline/1426173645597-1led78'

PRESET_VIDEO = {
    'Codec': 'H.264',
    'Profile': 'baseline',
    'BitRate': 'auto',
    'FrameRate': str(OUTPUT_FRAME_RATE),
    'SizingPolicy': 'ShrinkToFill',
    'FixedGOP': 'false',
    'KeyframesMaxDist': '90',
    'CodecOptions': {
        'MaxReferenceFrames': '3',
        'Profile': 'baseline',
        'Level': '3.1'
    },
    'DisplayAspectRatio': 'auto',
    'PaddingPolicy': 'NoPad'
}

PRESET_AUDIO = {
    'Codec': 'AAC',
    'Channels': '0',  # Suppress audio output
    'SampleRate': '44100',
    'BitRate': '128',
}

PRESET_THUMBNAILS = {
    'Format': 'jpg',
    'Interval': '1',
    'MaxWidth': '320',
    'MaxHeight': '240',
    'PaddingPolicy': 'NoPad',
    'SizingPolicy': 'ShrinkToFill'
}

PRESETS = [
    {
        'name': '372x330',
        'width': 372,
        'height': 330,
        'description': 'iPhone 6'
    },
    {
        'name': '538x478',
        'width': 538,
        'height': 478,
        'description': 'iPhone 6+'
    }
]


def main():
    transcoder = boto.elastictranscoder.connect_to_region(
        AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    pipeline = None

    pipelines = transcoder.list_pipelines()

    for pipeline in pipelines['Pipelines']:
        if pipeline['Name'] == PIPELINE_NAME:
            # transcoder.delete_pipeline(pipeline['Id'])
            # pipeline = None
            break

    if pipeline is None:
        sns = boto.sns.connect_to_region(
            AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )

        job_complete_topic = sns.create_topic(JOB_COMPLETE_TOPIC)
        job_error_topic = sns.create_topic(JOB_ERROR_TOPIC)

        sqs = boto.sqs.connect_to_region(
            AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )

        job_complete_queue = sqs.create_queue(JOB_COMPLETE_QUEUE)
        job_error_queue = sqs.create_queue(JOB_ERROR_QUEUE)

        job_complete_topic_arn = job_complete_topic['CreateTopicResponse']['CreateTopicResult']['TopicArn']
        job_error_topic_arn = job_error_topic['CreateTopicResponse']['CreateTopicResult']['TopicArn']

        sns.subscribe_sqs_queue(job_complete_topic_arn, job_complete_queue)
        sns.subscribe_sqs_queue(job_error_topic_arn, job_error_queue)

        pipeline = transcoder.create_pipeline(
            PIPELINE_NAME,
            AWS_STORAGE_BUCKET_NAME,
            AWS_STORAGE_BUCKET_NAME,
            TRANSCODING_ROLE_ARN,
            {
                'Progressing': '',
                'Completed': job_complete_topic_arn,
                'Warning': '',
                'Error': job_error_topic_arn
            }
        )

        pipeline = pipeline['Pipeline']

    transcoder = boto.elastictranscoder.connect_to_region(
        AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    aws_presets = transcoder.list_presets()['Presets']

    presets = []

    for preset in PRESETS:
        aws_found = False

        for aws_preset in aws_presets:
            if aws_preset['Name'] == preset['name']:
                presets.append(aws_preset)
                aws_found = True

        if not aws_found:
            video = PRESET_VIDEO.copy()
            video['MaxWidth'] = str(preset['width'])
            video['MaxHeight'] = str(preset['height'])
            audio = PRESET_AUDIO.copy()

            presets.append(transcoder.create_preset(
                preset['name'],
                preset['description'],
                'mp4',
                video,
                audio,
                PRESET_THUMBNAILS
            ))

    s3 = S3Connection(
        AWS_ACCESS_KEY_ID,
        AWS_SECRET_ACCESS_KEY
    )

    bucket = s3.get_bucket(AWS_STORAGE_BUCKET_NAME)

    for key in bucket.list():
        if 'zip' in key.name:
            continue

        input_name = {
            'Key': key.name,
            'Container': 'auto',
            'FrameRate': 'auto',
            'Resolution': 'auto',
            'AspectRatio': 'auto'
        }

        outputs = []

        for preset in presets:
            outputs.append({
                'Key': '%s/%s' % (preset['Name'], key.name),
                'PresetId': preset['Id']
            })

        job = transcoder.create_job(
            pipeline['Id'],
            input_name=input_name,
            outputs=outputs
        )

        print job

    for job in transcoder.list_jobs_by_pipeline(pipeline['Id'])['Jobs']:
        print job
        print '=============='


if __name__ == '__main__':
    main()
