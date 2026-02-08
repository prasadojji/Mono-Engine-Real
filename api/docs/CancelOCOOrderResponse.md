# CancelOCOOrderResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**s** | **str** |  | [optional] 
**d** | [**CancelOCOOrderData**](CancelOCOOrderData.md) |  | [optional] 

## Example

```python
from openapi_client.models.cancel_oco_order_response import CancelOCOOrderResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CancelOCOOrderResponse from a JSON string
cancel_oco_order_response_instance = CancelOCOOrderResponse.from_json(json)
# print the JSON string representation of the object
print CancelOCOOrderResponse.to_json()

# convert the object into a dict
cancel_oco_order_response_dict = cancel_oco_order_response_instance.to_dict()
# create an instance of CancelOCOOrderResponse from a dict
cancel_oco_order_response_form_dict = cancel_oco_order_response.from_dict(cancel_oco_order_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


