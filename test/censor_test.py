import csv
import json
import time
from io import StringIO
from unittest.mock import patch

import pytest
from moto import mock_aws

from droppii import censor


@mock_aws
def test_return_value_is_compatable_with_s3(populated_s3):
    args = {"s3_uri": 's3://test/small.csv', "private_keys": []}
    json_string = json.dumps(args)

    file_bytes = censor(json_string)
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
    csv_result = censor(csv_string).decode()
    bytes_reader = csv.reader(StringIO(csv_result))
    bytes_keys = [row for row in bytes_reader][0]
    assert bytes_keys == original_keys


@pytest.mark.slow
@mock_aws
def test_processes_1mb_per_minute(populated_s3, small_fake_data):
    '''Generate a large dataset and checks runtime for anonymize_fields'''
    pkeys = [key for key in small_fake_data[0].keys()]
    large_s3_keys = ["large.csv",
                     "large.json",
                     "large.parquet"]
    for key in large_s3_keys:
        argument = f'''{{"s3_uri":"s3://test/{key}",
            "private_keys":{json.dumps(pkeys)}}}'''

        s3_file = populated_s3.get_object(Bucket='test', Key=key)
        s3_size_in_MB = s3_file["ContentLength"] / 1_000
        assert s3_size_in_MB >= 1

        start = time.perf_counter()
        censor(argument)
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
    with patch("droppii.censor._replace_bytes_values") as mock:
        censor(json.dumps(argument))
    mock.assert_called_once()


@mock_aws
def test_returns_value_from_replace_bytes(populated_s3):
    '''value from _replace_bytes_values should be returned'''
    argument = {
        "s3_uri": "s3://test/small.csv",
        "private_keys": ["age", "email"]
    }
    expected = b'faked data'
    with patch("droppii.censor._replace_bytes_values",
               return_value=expected):
        returned = censor(json.dumps(argument))

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
    returned = censor(json.dumps(argument))

    assert returned is not s3_file


@mock_aws
def test_raises_on_no_file_ext(populated_s3):
    populated_s3.put_object(Bucket='test', Key='small', Body='_')
    argument = {
        "s3_uri": "s3://test/small",
        "private_keys": ["age", "email"]
    }
    with pytest.raises(ValueError):
        censor(json.dumps(argument))


def test_doesnt_error_on_mixed_case_filename(populated_s3, fake_csv_bytes):
    populated_s3.put_object(
        Bucket='test',
        Key='SmALl.CsV',
        Body=fake_csv_bytes)
    argument = {
        "s3_uri": "s3://test/SmALl.CsV",
        "private_keys": ["age", "email"]
    }
    censor(json.dumps(argument))
