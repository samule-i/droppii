# Arguments
	- `hide_values` takes a JSON string as it's only argument.
		- The JSON string **must** contain the keys:
			- s3_uri: A string to the s3 file to be anonymized
				- Provided AWS (S3) file **must** be in CSV format.
			- keys: `[]` A list of strings containing the keys to be anonymized
			- example:
				- `````
				  {
				  	s3_uri: "s3://bucket/file.csv",
				      keys: ["name", "address"]
				  }
				  ```
- # Return Value
	- `hide_values` returns a bytestream representation of a **new** file
		- The values of the corresponding keys will have been removed and replaced with non-identifiable data
	- The return value will be compatible with AWS (S3) [put_object](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/put_object.html)
- # Basic Usage
  id:: 6650f108-1100-4748-b638-b6d5a5801309
	- ```
	  droppii.hide_values(
	      json_params:str
	  ) -> bytes
	  ```
	- id:: 665101a2-769b-41d7-8fe0-83bec29fd206
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
-