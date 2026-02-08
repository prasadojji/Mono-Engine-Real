# SecretData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**key** | **str** |  | [optional] 
**algo** | **str** |  | 
**totp_url** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.secret_data import SecretData

# TODO update the JSON string below
json = "{}"
# create an instance of SecretData from a JSON string
secret_data_instance = SecretData.from_json(json)
# print the JSON string representation of the object
print SecretData.to_json()

# convert the object into a dict
secret_data_dict = secret_data_instance.to_dict()
# create an instance of SecretData from a dict
secret_data_form_dict = secret_data.from_dict(secret_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


