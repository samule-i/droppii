import pytest
from moto import mock_aws
import boto3
import os

files_path = os.path.abspath('./test/sample_files')


@pytest.fixture(scope='function')
def populated_s3():
    bucket = 'test'
    key = 'test.csv'
    csv_data = open(f'{files_path}/small.csv', 'rb')
    with mock_aws():
        s3client = boto3.client(service_name='s3', region_name='us-east-1')
        s3client.create_bucket(Bucket=bucket)
        s3client.put_object(Bucket=bucket, Key=key, Body=csv_data)
        s3client.upload_file(f'{files_path}/small.json',
                             Bucket=bucket, Key='small.json')
        yield s3client
