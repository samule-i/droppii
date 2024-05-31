import csv
import json
import time
from io import StringIO
from unittest.mock import patch

import boto3
import pytest
from moto import mock_aws

from droppii.droppii import hide_fields


@mock_aws
def test_return_value_is_compatable_with_s3(populated_s3):
    args = {"s3_uri": f's3://test/small.csv', "private_keys": []}
    json_string = json.dumps(args)

    file_bytes = hide_fields(json_string)
    response = populated_s3.put_object(
        Bucket='test', Key='new.csv', Body=file_bytes)
    assert len(response) > 0


@mock_aws
def test_csv_returns_csv(populated_s3):
    original_file = populated_s3.get_object(Bucket="test", Key="small.csv")
    original_data = original_file["Body"].read().decode()
    original_reader = csv.reader(StringIO(original_data))
    original_keys = [row for row in original_reader][0]
    csv_string = '{"s3_uri": "s3://test/small.csv", "private_keys": []}'
    csv_result = hide_fields(csv_string).decode()
    bytes_reader = csv.reader(StringIO(csv_result))
    bytes_keys = [row for row in bytes_reader][0]
    assert bytes_keys == original_keys


@pytest.mark.slow
@mock_aws
def test_processes_1mb_csv_per_minute(populated_s3):
    '''Generate a large dataset and checks runtime for anonymize_fields'''
    csv_string = """
        {
            "s3_uri": "s3://test/large.csv",
            "private_keys": ["name", "age", "email"]
        }
    """

    start = time.perf_counter()
    hide_fields(csv_string)
    stop = time.perf_counter()
    elapsed = stop - start
    if elapsed > 60:
        pytest.fail('Execution took too long')


@mock_aws
def test_correct_parser_called_for_csv_file(populated_s3):
    ''' Check that the correct field remover is called for CSV files.
    '''

    csv_string = """
        {
            "s3_uri": "s3://test/small.csv",
            "private_keys": ["name", "age", "email"]
        }
    """
    json_string = """
        {
            "s3_uri": "s3://test/small.json",
            "private_keys": ["name", "age", "email"]
        }
    """
    parquet_string = """
        {
            "s3_uri": "s3://test/small.parquet",
            "private_keys": ["name", "age", "email"]
        }
    """

    with patch("polars.read_csv") as mock:
        hide_fields(json_string)
        hide_fields(parquet_string)
    mock.assert_not_called()

    with patch("polars.read_csv") as mock:
        hide_fields(csv_string)
    mock.assert_called_once()
