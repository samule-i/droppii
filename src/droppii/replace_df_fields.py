import polars as pl


def replace_df_fields(
        df: pl.DataFrame, private_keys: list[str]) -> pl.DataFrame:
    """Return a dataframe with all columns listed in `private_keys`
    replaced with '***'"""
    if not isinstance(df, pl.DataFrame):
        raise TypeError("Not a polars DataFrame")
    for key in private_keys:
        df = df.with_columns(pl.col(key).map_batches(lambda x: "***"))
    return df
