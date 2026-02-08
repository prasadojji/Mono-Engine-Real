# ClientDetailsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**s** | **str** |  | [optional] 
**d** | [**ClientDetailsData**](ClientDetailsData.md) |  | [optional] 

## Example

```python
from openapi_client.models.client_details_response import ClientDetailsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ClientDetailsResponse from a JSON string
client_details_response_instance = ClientDetailsResponse.from_json(json)
# print the JSON string representation of the object
print ClientDetailsResponse.to_json()

# convert the object into a dict
client_details_response_dict = client_details_response_instance.to_dict()
# create an instance of ClientDetailsResponse from a dict
client_details_response_form_dict = client_details_response.from_dict(client_details_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


