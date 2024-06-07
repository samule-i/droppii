# droppii
Python module to process data from an AWS (S3) bucket and anonymize personally identifiable information, returning data in the same format as provided.
- [PyPi-repository](https://pypi.org/project/droppii)  
- [Further-Documentation](https://samule-i.github.io/droppii)
___
# Quickstart
Install droppii from PyPi
```sh
pip install droppii
```

Most users will only need to use `droppii.censor`, which takes a JSON string in the format of `{s3_uri:"s3://...", private_keys:["key1", "key2"]}` and returns a file-like bytes in the same format as file at the s3 location provided.

Currently supports csv, json or parquet file format as input.
### usage example
```python
import json

import droppii
import boto3

json_params = json.dumps({
  "s3_uri" = "s3://your-bucket/your_file.csv",
	"private_keys" = ["name", "address", "email_address"]
})
anonymized_bytes = droppii.censor(json_params)

s3client = boto3.Client("s3")
s3client.put_object(
  Bucket = "your-destination-bucket",
  Key = "anonymized_file.csv",
  Body = anonymized_bytes
)
``` 