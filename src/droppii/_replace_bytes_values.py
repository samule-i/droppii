from io import BytesIO

import polars as pl

from .replace_df_fields import replace_df_fields


def _replace_bytes_values(data: bytes,
                          private_keys: list[str],
                          data_format: str) -> bytes:
    """Replace all values for all keys listed in `private_keys`

    `data` must be a file-like object representing a csv file."""
    buf = BytesIO()
    if data_format == "csv":
        df = pl.read_csv(data)
    elif data_format == "json":
        try:
            df = pl.read_json(data)
        except RuntimeError:
            raise ValueError("Invalid json file")
    elif data_format == "parquet":
        try:
            df = pl.read_parquet(data)
        except pl.exceptions.ComputeError:
            raise ValueError("Invalid Parquet file")
    else:
        raise TypeError("Invalid file provided")

    new_df = replace_df_fields(df, private_keys)
    if new_df.columns != df.columns:
        raise RuntimeError(
            "DataFrame column mismatch in transformed data found")

    if data_format == "csv":
        new_df.write_csv(buf)
    elif data_format == "json":
        new_df.write_json(buf, row_oriented=True)
    elif data_format == "parquet":
        new_df.write_parquet(buf)
    else:
        raise TypeError("Invalid file provided")

    buf.seek(0)
    privatized_bytes = buf.read()
    return privatized_bytes
