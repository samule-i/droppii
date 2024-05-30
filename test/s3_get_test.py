import pytest
from moto import mock_aws

from droppii.s3_get import s3_get


@mock_aws
def test_fails_if_missing_file(populated_s3):
    with pytest.raises(Exception):
        s3_get.s3_get("s3://test/missing_file")
    with pytest.raises(Exception):
        s3_get.s3_get("s3://missing_bucket/test.csv")
