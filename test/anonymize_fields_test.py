import csv
import json
from io import StringIO

import boto3
import pytest
from _csv import Error as csv_Error
from moto import mock_aws

from DropPii.DropPii import anonymize_fields


@mock_aws
def test_return_value_is_compatable_with_s3():
    region = 'us-east-1'
    bucket = 'test-bucket'
    key = 'test-key.csv'

    args = {"s3_path": f's3://{bucket}/{key}', "pii_fields": []}
    json_string = json.dumps(args)

    s3client = boto3.client(service_name='s3', region_name=region)
    s3client.create_bucket(Bucket=bucket)
    s3client.put_object(Bucket=bucket, Key=key, Body='')

    file_bytes = anonymize_fields(json_string)
    response = s3client.put_object(Bucket=bucket, Key=key, Body=file_bytes)
    assert len(response) > 0


@mock_aws
def test_csv_returns_csv(populated_s3):
    with open('./test/sample_files/small.csv', 'r') as csv_file:
        file_reader = csv.reader(csv_file)
        original_keys = [row for row in file_reader][0]
    csv_string = '{"s3_path": "s3://test/test.csv", "pii_fields": []}'
    csv_result = anonymize_fields(csv_string).decode()
    bytes_reader = csv.reader(StringIO(csv_result))
    bytes_keys = [row for row in bytes_reader][0]
    assert bytes_keys == original_keys
