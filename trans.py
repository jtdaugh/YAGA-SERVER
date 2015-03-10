#!/usr/bin/env python
import boto.sns
import boto.sqs
import boto.elastictranscoder

AWS_REGION = 'us-west-1'
AWS_ACCESS_KEY_ID = 'AKIAJ3BOSZSPPD7EX7KA'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'yaga-dev'

OUTPUT_FRAME_RATE = 15
PIPELINE_NAME = 'yaga-dev-pipeline'
JOB_COMPLETE_TOPIC = 'sns_complete'
JOB_ERROR_TOPIC = 'sns_error'
JOB_COMPLETE_QUEUE = 'sqs_complete'
JOB_ERROR_QUEUE = 'sqs_error'
TRANSCODING_ROLE_ARN = 'arn:aws:iam::609367773239:role/transcoding-role'


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
            break

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

    if pipeline is not None:
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

    print pipeline

if __name__ == '__main__':
    main()
