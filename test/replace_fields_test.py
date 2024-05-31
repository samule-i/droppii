import polars as pl
import polars.testing as pl_testing
import pytest

from droppii import replace_df_fields


def test_replaces_all_values_for_fields(small_fake_data):
    '''Every value under keys specified in `private_keys` should be replaced'''
    original_df = pl.DataFrame(small_fake_data)
    result_df = replace_df_fields(original_df, ["age", "email"])
    assert all([value == "***" for value in result_df["age"]])
    assert all([value == "***" for value in result_df["email"]])


def test_doesnt_modify_other_field_values(small_fake_data):
    '''Any value under a key NOT specified in `private_keys`
    should be untouched'''
    original_df = pl.DataFrame(small_fake_data)
    result_df = replace_df_fields(original_df, ["age", "email"])
    fake_keys = [k for k in small_fake_data[0].keys()]
    unmodified_keys = [k for k in fake_keys if k not in ["age", "email"]]
    for key in unmodified_keys:
        pl_testing.assert_series_equal(result_df[key], original_df[key])
    pl_testing.assert_series_not_equal(result_df["age"], original_df["age"])


def test_raises_if_key_doesnt_exist(small_fake_data):
    '''If key does not exist in dataset, raise an error'''
    original_df = pl.DataFrame(small_fake_data)
    with pytest.raises(pl.ColumnNotFoundError):
        replace_df_fields(original_df, ["no_key"])


def test_raises_if_not_passed_dataframe():
    '''Error on invalid df argument'''
    not_df = ["a", "b"]
    with pytest.raises(TypeError):
        replace_df_fields(not_df, ["keys"])  # type: ignore
