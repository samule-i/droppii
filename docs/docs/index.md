# Droppii
- [github](https://github.com/samule-i/droppii)
- [PyPi](https://pypi.org/project/droppii)

## About
Droppii is a python module to process data from an AWS (S3) bucket and anonymize personally identifiable information, returning data in the same format as provided.

## Quickstart
Most users will only need to access the `hide_values` function.
```python
import droppii
import json
import boto3

json_params = json.dumps({
    "s3_uri" = "s3://your-bucket/your_file.csv",
	"keys" = ["name", "address", "email_address"]
})
anonymized_bytes = droppii.hide_values(json_params)

s3client = boto3.Client("s3")
s3client.put_object(
  Bucket = "your-destination-bucket",
  Key = "anonymized_file.csv",
  Body = anonymized_bytes
)
```