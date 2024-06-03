# Usage
## droppii.censor
```
droppii.censor(
    json_params:str
) -> bytes
```
### arguments

`censor` takes a JSON string as it's only argument.
The JSON string **must** contain the keys:

- s3_uri: A string to the s3 file to be anonymized
    - Provided AWS (S3) file **must** be in csv, json or parquet format.
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
anonymized_bytes = droppii.censor(json_params)

s3client = boto3.Client("s3")
s3client.put_object(
Bucket = "your-destination-bucket",
Key = "anonymized_file.csv",
Body = anonymized_bytes
)
```
## droppii.s3_get()
```
droppii.s3_get(s3_uri: str) -> bytes 
```

### Arguments
`s3_uri` is a string leading to a file hosted on s3, eg. `s3://your_bucket/file_key.csv`

### Return
Returns unmodified file bytes from the file hosted on s3

### Example
```python
import droppii

file_bytes = droppii.s3_get('s3://bucket/file.csv')
```

## replace_df_fields
Return a dataframe with all columns listed in `private_keys` replaced with "***"

```
droppii.replace_df_fields(df: polars.DataFrame, private_keys: list[str]) -> polars.Dataframe
```

### Arguments

- `df` is a polars.DataFrame
- `private_keys` is a list of keys to be anonymized

### Return
Returns a modified polars DataFrame with obfuscated values

### Example
```python
import polars

import droppii

df = polars.DataFrame({
    "A":["1","2","3"],
    "B":["1","2","3"]
})

new_df = droppii.replace_df_fields(df, ["B"])
```
```
┌─────┬─────┐
│ A   ┆ B   │
│ --- ┆ --- │
│ str ┆ str │
╞═════╪═════╡
│ 1   ┆ *** │
│ 2   ┆ *** │
│ 3   ┆ *** │
└─────┴─────┘
```