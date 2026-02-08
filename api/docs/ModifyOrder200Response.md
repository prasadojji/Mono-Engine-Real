# ModifyOrder200Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**s** | **str** |  | [optional] 
**d** | [**ModifyOrderData**](ModifyOrderData.md) |  | [optional] 
**msg** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.modify_order200_response import ModifyOrder200Response

# TODO update the JSON string below
json = "{}"
# create an instance of ModifyOrder200Response from a JSON string
modify_order200_response_instance = ModifyOrder200Response.from_json(json)
# print the JSON string representation of the object
print ModifyOrder200Response.to_json()

# convert the object into a dict
modify_order200_response_dict = modify_order200_response_instance.to_dict()
# create an instance of ModifyOrder200Response from a dict
modify_order200_response_form_dict = modify_order200_response.from_dict(modify_order200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


