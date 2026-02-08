# ModifyOrderResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**s** | **str** |  | [optional] 
**d** | [**ModifyOrderData**](ModifyOrderData.md) |  | [optional] 

## Example

```python
from openapi_client.models.modify_order_response import ModifyOrderResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ModifyOrderResponse from a JSON string
modify_order_response_instance = ModifyOrderResponse.from_json(json)
# print the JSON string representation of the object
print ModifyOrderResponse.to_json()

# convert the object into a dict
modify_order_response_dict = modify_order_response_instance.to_dict()
# create an instance of ModifyOrderResponse from a dict
modify_order_response_form_dict = modify_order_response.from_dict(modify_order_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


