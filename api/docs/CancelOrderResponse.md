# CancelOrderResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**s** | **str** |  | [optional] 
**d** | [**CancelOrderData**](CancelOrderData.md) |  | [optional] 

## Example

```python
from openapi_client.models.cancel_order_response import CancelOrderResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CancelOrderResponse from a JSON string
cancel_order_response_instance = CancelOrderResponse.from_json(json)
# print the JSON string representation of the object
print CancelOrderResponse.to_json()

# convert the object into a dict
cancel_order_response_dict = cancel_order_response_instance.to_dict()
# create an instance of CancelOrderResponse from a dict
cancel_order_response_form_dict = cancel_order_response.from_dict(cancel_order_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


