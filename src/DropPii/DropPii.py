import json

from .s3_get import s3_get


def anonymize_fields(json_string: str) -> bytes:
    params = json.loads(json_string)
    s3_uri = params['s3_uri']
    data = s3_get.s3_get(s3_uri)
    return data
