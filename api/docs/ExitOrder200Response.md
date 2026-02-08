# ExitOrder200Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**s** | **str** |  | [optional] 
**d** | [**ExitSnoData**](ExitSnoData.md) |  | [optional] 
**msg** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.exit_order200_response import ExitOrder200Response

# TODO update the JSON string below
json = "{}"
# create an instance of ExitOrder200Response from a JSON string
exit_order200_response_instance = ExitOrder200Response.from_json(json)
# print the JSON string representation of the object
print ExitOrder200Response.to_json()

# convert the object into a dict
exit_order200_response_dict = exit_order200_response_instance.to_dict()
# create an instance of ExitOrder200Response from a dict
exit_order200_response_form_dict = exit_order200_response.from_dict(exit_order200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


