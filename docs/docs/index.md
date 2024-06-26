# Droppii
- [github](https://github.com/samule-i/droppii)
- [PyPi](https://pypi.org/project/droppii)

## About
Droppii is a python module to process data from an AWS (S3) bucket and anonymize personally identifiable information **non-recursively**, returning data in the same format as provided.

Droppii intends to remove values from **top-level** columns only, any nested objects or string representations of objects will **not** be processed.

example with "email" as key:

|_id|email|contacts|
|---|---|---|
|1|***|{name: "Sue", email:exposed@email.com}|
|2|***|{name: "Alan, email:pii@email.com}|

## CLI usage
`droppii` can be used from the commandline by invoking the python module directly:  
`python -m droppii -i s3 uri -k key1 key2 ... > output_file`
```
options:
  -h, --help            show this help message and exit
  -i s3 uri, --input s3 uri
                        s3 uri of file to be converted
  -k KEYS [KEYS ...], --keys KEYS [KEYS ...]
                        Keys to censor
```
**example:**
```sh
python -m droppii -i s3://bucket/test_file.json -k email_address name
```
```
>> [
    {
        "_id":98,
        "name":"***",
        "age":38,
        "email":"***",
        ...
    },
    {
        "_id":99,
        "name":"***",
        "age":21,
        "email":"***",
        ...
    }
]
```

## Quickstart
Install droppii from PyPi  
```sh
pip install droppii
```

Most users will only need to use `droppii.censor`, which takes a JSON string in the format of `{s3_uri:"s3://...", private_keys:["key1", "key2"]}` and returns a file-like bytes in the same format as file at the s3 location provided.

Currently supports csv, json or parquet file format as input.
```python
import droppii
import json
import boto3

json_params = json.dumps({
    "s3_uri" = "s3://your-bucket/your_file.csv",
	"keys" = ["name", "address", "email_address"]
})
anonymized_bytes = droppii.censor(json_params)

s3client = boto3.Client("s3")
s3client.put_object(
  Bucket = "your-destination-bucket",
  Key = "anonymized_file.csv",
  Body = anonymized_bytes
)
```

## Performance
Using AWS lambda as a benchmark where the lambda calls `droppii.censor` as simply as possible with the near worst case of modifying all but one key.
```
get s3 file body
result = droppii.censor(s3 file body)
return DataFrame(result)
```

Using ~1mb sample files

| |records|keys|keys processed|file size|execution time|
|---|---|---|---|---|---|
|CSV|20,120|7|6|1.1mb|0.6s|
|JSON|10,427|7|6|1.3mb|2.7s|
|Parquet|60,000|7|6|1.1mb|2.5s|
