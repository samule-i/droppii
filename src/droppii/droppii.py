import json

import polars as pl

from . import s3_get


def _csv_replace_fields():
    pass


def replace_fields(df: pl.DataFrame, private_keys: list[str]) -> pl.DataFrame:
    '''Return a dataframe with all columns listed in `private_keys`
    replaced with "***"'''
    for key in private_keys:
        df = df.with_columns(pl.col(key).map_batches(lambda x: "***"))
    return df


def anonymize_fields(json_string: str) -> bytes:
    '''Replaces values in a file hosted on S3 based on keys present
    in ``pii_fields``.
    returning bytes that can be passed to ``put_object``.

    ``json_string`` must contains the keys ``s3_uri`` & ``pii_fields``.

    ``s3_uri`` must be a string containing the s3 uri for the file
    to be modified, and the file MUST be a valid csv file.

    ``pii_fields`` must be a list containing the keys to be replaced
    '''
    params = json.loads(json_string)
    s3_uri: str = params['s3_uri']
    data = s3_get.s3_get(s3_uri)
    if s3_uri.endswith(".csv"):
        _csv_replace_fields()
    return data
