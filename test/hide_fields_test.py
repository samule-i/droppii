import csv
import json
import time
from io import StringIO
from unittest.mock import patch

import polars as pl
import polars.testing as pl_testing
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
def test_correct_parser_called_for_csv_file(populated_s3):
    ''' Check that the correct field remover is called for CSV files.
    '''

    csv_string = """
        {
            "s3_uri": "s3://test/small.csv",
            "private_keys": []
        }
    """
    json_string = """
        {
            "s3_uri": "s3://test/small.json",
            "private_keys": []
        }
    """
    parquet_string = """
        {
            "s3_uri": "s3://test/small.parquet",
            "private_keys": []
        }
    """
    fake_df = pl.DataFrame({"_": ["_"]})
    with patch("polars.read_csv", return_value=fake_df) as mock:
        hide_fields(json_string)
        hide_fields(parquet_string)
    mock.assert_not_called()

    with patch("polars.read_csv", return_value=fake_df) as mock:
        hide_fields(csv_string)
    mock.assert_called_once()


@mock_aws
def test_csv_values_are_replaced(populated_s3):
    '''All values for all keys specified should be replaced in returned data'''
    argument = {
        "s3_uri": "s3://test/small.csv",
        "private_keys": ["age", "email"]
    }
    new_csv = hide_fields(json.dumps(argument))
    df = pl.read_csv(new_csv)
    for key in argument["private_keys"]:
        assert all(k == "***" for k in df[key])


@mock_aws
def test_csv_values_are_unmodified(populated_s3):
    '''All values for all keys not specified should be unmodified
    in returned data'''
    argument = {
        "s3_uri": "s3://test/small.csv",
        "private_keys": ["age", "email"]
    }
    s3_file_bytes = populated_s3.get_object(
        Bucket="test",
        Key="small.csv")["Body"].read()
    old_df = pl.read_csv(s3_file_bytes)
    unmodified_keys = [
        k for k in old_df.columns if k not in argument["private_keys"]]
    new_csv = hide_fields(json.dumps(argument))
    new_df = pl.read_csv(new_csv)
    for key in unmodified_keys:
        pl_testing.assert_series_equal(new_df[key], old_df[key])


@mock_aws
def test_correct_parser_called_for_json_file(populated_s3):
    ''' Check that the correct field remover is called for JSON files.
    '''
    csv_string = """
        {
            "s3_uri": "s3://test/small.csv",
            "private_keys": []
        }
    """
    json_string = """
        {
            "s3_uri": "s3://test/small.json",
            "private_keys": []
        }
    """
    parquet_string = """
        {
            "s3_uri": "s3://test/small.parquet",
            "private_keys": []
        }
    """
    fake_df = pl.DataFrame({"_": ["_"]})
    with patch("polars.read_json", return_value=fake_df) as mock:
        hide_fields(csv_string)
        hide_fields(parquet_string)
    mock.assert_not_called()

    with patch("polars.read_json", return_value=fake_df) as mock:
        hide_fields(json_string)
    mock.assert_called_once()


@mock_aws
def test_json_values_are_replaced(populated_s3):
    '''All values for all keys specified should be replaced in returned data'''
    argument = {
        "s3_uri": "s3://test/small.json",
        "private_keys": ["age", "email"]
    }
    new_json = hide_fields(json.dumps(argument))
    df = pl.read_json(new_json)
    for key in argument["private_keys"]:
        assert all(k == "***" for k in df[key])


@mock_aws
def test_json_values_are_unmodified(populated_s3):
    '''All values for all keys not specified should be unmodified
    in returned data'''
    argument = {
        "s3_uri": "s3://test/small.json",
        "private_keys": ["age", "email"]
    }
    s3_file_bytes = populated_s3.get_object(
        Bucket="test",
        Key="small.json")["Body"].read()
    old_df = pl.read_json(s3_file_bytes)
    unmodified_keys = [
        k for k in old_df.columns if k not in argument["private_keys"]]
    new_json = hide_fields(json.dumps(argument))
    new_df = pl.read_json(new_json)
    for key in unmodified_keys:
        pl_testing.assert_series_equal(new_df[key], old_df[key])


@mock_aws
def test_raises_on_invalid_file_type(populated_s3):
    '''Should raise an error if not passed an expected file format'''
    populated_s3.put_object(Bucket='test', Key='small.pdf', Body='_')
    argument = '{"s3_uri":"s3://test/small.pdf", "private_keys":[]}'
    with pytest.raises(ValueError):
        hide_fields(argument)
