import csv
import json
import random
import time
from io import BytesIO, StringIO

import boto3
import polars
import pytest
from moto import mock_aws

from DropPii.DropPii import anonymize_fields


@mock_aws
def test_return_value_is_compatable_with_s3():
    region = 'us-east-1'
    bucket = 'test-bucket'
    key = 'test-key.csv'

    args = {"s3_uri": f's3://{bucket}/{key}', "pii_fields": []}
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
    csv_string = '{"s3_uri": "s3://test/test.csv", "pii_fields": []}'
    csv_result = anonymize_fields(csv_string).decode()
    bytes_reader = csv.reader(StringIO(csv_result))
    bytes_keys = [row for row in bytes_reader][0]
    assert bytes_keys == original_keys


@mock_aws
def test_processes_1mb_csv_per_minute(populated_s3, faker):
    '''Generate a large dataset and checks runtime for anonymize_fields'''
    csv_row_size = 25_000
    csv_string = '{"s3_uri": "s3://test/1mb.csv", "pii_fields": ["pii_1", "pii_2"]}'

    random.seed(0)

    fake_data = []
    for _ in range(csv_row_size):
        row = {
            "name": faker.name(),
            "age": random.randint(18, 80),
            "email": faker.email(),
            "score": random.randint(0, 100),
            "owner": random.randint(0, 1),
            "favourite_colour": faker.color()
        }
        fake_data.append(row)
    df = polars.DataFrame(fake_data)
    csv_buf = BytesIO()
    df.write_csv(csv_buf)
    csv_buf.seek(0)
    populated_s3.put_object(Bucket='test', Key='1mb.csv', Body=csv_buf)

    start = time.perf_counter()
    anonymize_fields(csv_string)
    stop = time.perf_counter()
    elapsed = stop - start
    if elapsed > 60:
        pytest.fail('Execution took too long')
