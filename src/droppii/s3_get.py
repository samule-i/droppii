import boto3


def s3_get(s3_uri: str) -> bytes:
    """downloads a file from an S3 uri and returns the contents."""
    s3_parts: list[str] = s3_uri.replace("s3://", "").split("/")
    bucket = s3_parts.pop(0)
    file_path = "/".join(s3_parts)
    s3_client = boto3.client(service_name="s3")

    response = s3_client.get_object(Bucket=bucket, Key=file_path)

    data = response["Body"].read()
    return data
