# Usage
## droppii.hide_values
```
droppii.hide_values(
    json_params:str
) -> bytes
```
### arguments

`hide_values` takes a JSON string as it's only argument.
The JSON string **must** contain the keys:

- s3_uri: A string to the s3 file to be anonymized
    - Provided AWS (S3) file **must** be in CSV format.
- private_keys: `[]` A list of strings containing the keys to be anonymized

### Return value
Returns a bytestream representation of a **new** file

- The values of the corresponding keys will have been removed and replaced with non-identifiable data

The return value will be compatible with AWS (S3) [put_object](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/put_object.html)

### Example
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