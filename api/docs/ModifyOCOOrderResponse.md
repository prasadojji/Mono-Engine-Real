# ModifyOCOOrderResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**s** | **str** |  | [optional] 
**d** | [**ModifyOCOOrderData**](ModifyOCOOrderData.md) |  | [optional] 

## Example

```python
from openapi_client.models.modify_oco_order_response import ModifyOCOOrderResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ModifyOCOOrderResponse from a JSON string
modify_oco_order_response_instance = ModifyOCOOrderResponse.from_json(json)
# print the JSON string representation of the object
print ModifyOCOOrderResponse.to_json()

# convert the object into a dict
modify_oco_order_response_dict = modify_oco_order_response_instance.to_dict()
# create an instance of ModifyOCOOrderResponse from a dict
modify_oco_order_response_form_dict = modify_oco_order_response.from_dict(modify_oco_order_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


