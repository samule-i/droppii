import json
from unittest.mock import patch

import polars as pl
import polars.testing as pl_testing
import pytest

from droppii import _replace_bytes_values


def test_values_are_replaced(fake_csv_bytes):
    """All values for all keys specified should be replaced in returned data"""
    private_keys = ["age", "email"]
    privatized_csv = _replace_bytes_values(
        fake_csv_bytes, private_keys, "csv")
    df = pl.read_csv(privatized_csv)
    for key in private_keys:
        assert all([k == "***" for k in df[key]])


def test_values_are_unmodified(fake_csv_bytes,
                               fake_json_bytes,
                               fake_parquet_bytes):
    """All values for all keys not specified should be unmodified
    in returned data"""
    private_keys = ["age", "email"]
    original = pl.read_csv(fake_csv_bytes)
    unmodified_keys = [k for k in original.columns if k not in private_keys]
    returned_csv = _replace_bytes_values(fake_csv_bytes, private_keys, "csv")
    returned_json = _replace_bytes_values(
        fake_json_bytes, private_keys, "json")
    returned_parquet = _replace_bytes_values(
        fake_parquet_bytes, private_keys, "parquet")

    new_csv_df = pl.read_csv(returned_csv)
    new_json_df = pl.read_json(returned_json)
    new_parquet_df = pl.read_parquet(returned_parquet)
    for key in unmodified_keys:
        pl_testing.assert_series_equal(new_csv_df[key], original[key])
        pl_testing.assert_series_equal(new_json_df[key], original[key])
        pl_testing.assert_series_equal(new_parquet_df[key], original[key])


def test_returns_bytes(fake_csv_bytes, fake_json_bytes, fake_parquet_bytes):
    """Should return bytes object"""
    returned_csv = _replace_bytes_values(fake_csv_bytes, [], "csv")
    returned_json = _replace_bytes_values(fake_json_bytes, [], "json")
    returned_parquet = _replace_bytes_values(fake_parquet_bytes, [], "parquet")
    assert isinstance(returned_csv, bytes)
    assert isinstance(returned_json, bytes)
    assert isinstance(returned_parquet, bytes)


def test_raises_on_incompatible_file_type(fake_csv_bytes):
    """Should raise an error if not passed an expected file format"""
    with pytest.raises(TypeError):
        _replace_bytes_values(fake_csv_bytes, [], "pdf")


def test_raises_on_column_mismatch(fake_csv_bytes,
                                   fake_json_bytes,
                                   fake_parquet_bytes):
    """Should raise an error if columns do not match after transformation"""
    fake_df = pl.DataFrame({
        "c1": ["a", "b", "c"],
        "c2": ["1", "2", "3"]
    })
    with patch("droppii._replace_bytes_values.replace_df_fields",
               return_values=fake_df):
        with pytest.raises(RuntimeError):
            _replace_bytes_values(fake_csv_bytes, [], "csv")
        with pytest.raises(RuntimeError):
            _replace_bytes_values(fake_json_bytes, [], "json")
        with pytest.raises(RuntimeError):
            _replace_bytes_values(fake_parquet_bytes, [], "parquet")


def test_raises_on_parsing_incorrectly_as_json(fake_csv_bytes):
    """Program should raise if polars is unable to parse data as json"""
    with pytest.raises(ValueError):
        _replace_bytes_values(fake_csv_bytes, [], "json")


def test_raises_on_parsing_incorrectly_as_parquet(fake_csv_bytes):
    """Program should raise if polars is unable to parse data as parquet"""
    with pytest.raises(ValueError):
        _replace_bytes_values(fake_csv_bytes, [], "parquet")


def test_json_returned_in_multiline_format():
    data = [
        {
            "name": "David",
            "age":98
        }
    ]
    json_bytes = json.dumps(data, indent=4).encode()
    result = _replace_bytes_values(json_bytes, [], "json")
    assert result == json_bytes
