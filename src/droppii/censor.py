import json
from os import path

from ._replace_bytes_values import _replace_bytes_values
from .s3_get import s3_get


def censor(json_string: str) -> bytes:
    """Replaces values in a file hosted on S3 based on keys present
    in ``private_keys``.
    returning bytes that can be passed to ``put_object``.

    ``json_string`` must contains the keys ``s3_uri`` & ``private_keys``.

    ``s3_uri`` must be a string containing the s3 uri for the file
    to be modified, and the file MUST be a valid csv file.

    ``private_keys`` must be a list containing the keys to be replaced
    """
    params = json.loads(json_string)
    s3_uri: str = params["s3_uri"]
    private_keys: list[str] = params["private_keys"]
    data = s3_get(s3_uri)

    file_format = path.splitext(s3_uri)[1][1:].lower()
    if file_format not in ["csv", "json", "parquet"]:
        raise ValueError(f"Can't handle file format: {file_format}")

    privatized_bytes = _replace_bytes_values(data, private_keys, file_format)
    return privatized_bytes
