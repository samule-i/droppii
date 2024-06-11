- [PyPi-repository](https://pypi.org/project/droppii)  
- [Further-Documentation](https://samule-i.github.io/droppii)

# droppii
Droppii is a python module to process data from an AWS (S3) bucket and anonymize personally identifiable information **non-recursively**, returning data in the same format as provided.

Droppii intends to remove values from **top-level** columns only, any nested objects or string representations of objects will **not** be processed.

example with "email" as key:

|_id|email|contacts|
|---|---|---|
|1|***|{name: "Sue", email:exposed@email.com}|
|2|***|{name: "Alan, email:pii@email.com}|
___

# CLI usage
`droppii` can be used from the commandline by invoking the python module directly:  
`python -m droppii -i s3 uri -k key1 key2 ... >> output_file`
```
options:
  -h, --help            show this help message and exit
  -i s3 uri, --input s3 uri
                        s3 uri of file to be converted
  -k KEYS [KEYS ...], --keys KEYS [KEYS ...]
                        Keys to censor
```

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