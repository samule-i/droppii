import json

import boto3


def anonymize_fields(json_string: str) -> bytes:
    args = json.loads(json_string)
    s3_parts: list[str] = args['s3_path'].replace('s3://', '').split('/')

    bucket = s3_parts.pop(0)
    file_path = '/'.join(s3_parts)
    s3_client = boto3.client(service_name='s3')

    response = s3_client.get_object(Bucket=bucket, Key=file_path)

    data = response['Body'].read()
    return data
