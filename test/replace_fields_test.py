import polars as pl
import polars.testing as pl_testing

from droppii.droppii import replace_fields


def test_replaces_all_values_for_fields(small_fake_data):
    '''Every value under keys specified in `private_keys` should be replaced'''
    original_df = pl.DataFrame(small_fake_data)
    result_df = replace_fields(original_df, ["age", "email"])
    assert all([value == "***" for value in result_df["age"]])
    assert all([value == "***" for value in result_df["email"]])


def test_doesnt_modify_other_field_values(small_fake_data):
    '''Any value under a key NOT specified in `private_keys`
    should be untouched'''
    original_df = pl.DataFrame(small_fake_data)
    result_df = replace_fields(original_df, ["age", "email"])
    fake_keys = [k for k in small_fake_data[0].keys()]
    unmodified_keys = [k for k in fake_keys if k not in ["age", "email"]]
    for key in unmodified_keys:
        pl_testing.assert_series_equal(result_df[key], original_df[key])
    pl_testing.assert_series_not_equal(result_df["age"], original_df["age"])
