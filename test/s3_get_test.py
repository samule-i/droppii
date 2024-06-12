import boto3
import pytest
from moto import mock_aws

from droppii import s3_get


@mock_aws
def test_fails_if_missing_file(populated_s3):
    """Check function raises if s3 uri file doesn't exist
    or can't be accessed"""
    with pytest.raises(Exception):
        s3_get.s3_get("s3://test/missing_file")
    with pytest.raises(Exception):
        s3_get.s3_get("s3://missing_bucket/test.csv")


@mock_aws
def test_returns_body_of_s3_file():
    """Check function returns the contents of the file instead
    of the AWS response"""
    test_data = "ABC123"
    client = boto3.client(service_name="s3", region_name="us-east-1")
    client.create_bucket(Bucket="test")
    client.put_object(Bucket="test", Key="test", Body=test_data)

    retrieved_data = s3_get("s3://test/test")
    assert retrieved_data.decode() == test_data
