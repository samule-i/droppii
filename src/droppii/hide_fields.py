import json
from io import BytesIO

import polars as pl

from .replace_df_fields import replace_df_fields
from .s3_get import s3_get


def hide_fields(json_string: str) -> bytes:
    '''Replaces values in a file hosted on S3 based on keys present
    in ``private_keys``.
    returning bytes that can be passed to ``put_object``.

    ``json_string`` must contains the keys ``s3_uri`` & ``private_keys``.

    ``s3_uri`` must be a string containing the s3 uri for the file
    to be modified, and the file MUST be a valid csv file.

    ``private_keys`` must be a list containing the keys to be replaced
    '''
    privatized_file: BytesIO = BytesIO()
    params = json.loads(json_string)
    s3_uri: str = params['s3_uri']
    private_keys: list[str] = params["private_keys"]
    data = s3_get(s3_uri)
    if s3_uri.endswith(".csv"):
        df = pl.read_csv(data)
        df = replace_df_fields(df, private_keys)
        df.write_csv(privatized_file)
    elif s3_uri.endswith(".json"):
        pass
    elif s3_uri.endswith(".parquet"):
        pass
    else:
        raise ValueError(
            f'Unexpected file format supplied in s3_uri: {s3_uri}')
    privatized_file.seek(0)
    privatized_bytes = privatized_file.read()
    return privatized_bytes
