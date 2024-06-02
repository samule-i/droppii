import csv
import json
import time
from io import StringIO
from unittest.mock import patch

import pytest
from moto import mock_aws

from droppii import hide_fields


@mock_aws
def test_return_value_is_compatable_with_s3(populated_s3):
    args = {"s3_uri": 's3://test/small.csv', "private_keys": []}
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
def test_uses_replace_bytes_values(populated_s3):
    '''_replace_bytes_values should be called for any compatable file'''
    argument = {
        "s3_uri": "s3://test/small.csv",
        "private_keys": ["age", "email"]
    }
    with patch("droppii.hide_fields._replace_bytes_values") as mock:
        hide_fields(json.dumps(argument))
    mock.assert_called_once()


@mock_aws
def test_returns_value_from_replace_bytes(populated_s3):
    '''value from _replace_bytes_values should be returned'''
    argument = {
        "s3_uri": "s3://test/small.csv",
        "private_keys": ["age", "email"]
    }
    expected = b'faked data'
    with patch("droppii.hide_fields._replace_bytes_values",
               return_value=expected):
        returned = hide_fields(json.dumps(argument))

    assert expected is returned


@mock_aws
def test_not_returns_original_file(populated_s3):
    '''value returned should not be the original data'''
    argument = {
        "s3_uri": "s3://test/small.csv",
        "private_keys": ["age", "email"]
    }
    s3_file = populated_s3.get_object(
        Bucket="test", Key="small.csv")["Body"].read()
    returned = hide_fields(json.dumps(argument))

    assert returned is not s3_file


@mock_aws
def test_raises_on_no_file_ext(populated_s3):
    populated_s3.put_object(Bucket='test', Key='small', Body='_')
    argument = {
        "s3_uri": "s3://test/small",
        "private_keys": ["age", "email"]
    }
    with pytest.raises(ValueError):
        hide_fields(json.dumps(argument))


def test_doesnt_error_on_mixed_case_filename(populated_s3, fake_csv_bytes):
    populated_s3.put_object(
        Bucket='test',
        Key='SmALl.CsV',
        Body=fake_csv_bytes)
    argument = {
        "s3_uri": "s3://test/SmALl.CsV",
        "private_keys": ["age", "email"]
    }
    hide_fields(json.dumps(argument))
