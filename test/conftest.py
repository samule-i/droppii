import os
import random
from io import BytesIO

import boto3
import polars as pl
import pytest
from faker import Faker
from moto import mock_aws

files_path = os.path.abspath('./test/sample_files')


def generate_fake_data(rows):
    faker = Faker(['en_GB'])
    fake_data = [
        {
            "name": faker.name(),
            "age": random.randint(18, 80),
            "email": faker.email(),
            "score": random.randint(0, 100),
            "owner": random.randint(0, 1),
            "favourite_colour": faker.color()
        } for _ in range(rows)
    ]
    return fake_data


def write_csv_as_bytes(data: pl.DataFrame) -> BytesIO:
    buf = BytesIO()
    data.write_csv(buf)
    buf.seek(0)
    return buf


def json_bytes(data: pl.DataFrame) -> BytesIO:
    buf = BytesIO()
    data.write_json(buf)
    buf.seek(0)
    return buf


def parquet_bytes(data: pl.DataFrame) -> BytesIO:
    buf = BytesIO()
    data.write_parquet(buf)
    buf.seek(0)
    return buf


@pytest.fixture(scope='session')
def small_fake_data():
    random.seed(0)
    fake_data = generate_fake_data(100)
    return fake_data


@pytest.fixture(scope='session')
def large_fake_data():
    random.seed(0)
    fake_data = generate_fake_data(25_000)
    return fake_data


@pytest.fixture(scope='function')
def populated_s3(small_fake_data, large_fake_data):
    bucket = 'test'
    small_df = pl.DataFrame(small_fake_data)
    large_df = pl.DataFrame(large_fake_data)

    small_csv_buf = write_csv_as_bytes(small_df)
    large_csv_buf = write_csv_as_bytes(large_df)
    small_json = json_bytes(small_df)
    large_json = json_bytes(large_df)
    small_pq = parquet_bytes(small_df)
    large_pq = parquet_bytes(large_df)
    with mock_aws():
        s3client = boto3.client(service_name='s3', region_name='us-east-1')
        s3client.create_bucket(Bucket=bucket)
        s3client.put_object(Bucket=bucket, Key="small.csv", Body=small_csv_buf)
        s3client.put_object(Bucket=bucket, Key="large.csv", Body=large_csv_buf)
        s3client.put_object(Bucket=bucket, Key="small.json", Body=small_json)
        s3client.put_object(Bucket=bucket, Key="small.json", Body=large_json)
        s3client.put_object(Bucket=bucket, Key="small.parquet", Body=small_pq)
        s3client.put_object(Bucket=bucket, Key="small.parquet", Body=large_pq)
        yield s3client
