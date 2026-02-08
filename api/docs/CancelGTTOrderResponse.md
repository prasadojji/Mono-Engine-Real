# CancelGTTOrderResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**s** | **str** |  | [optional] 
**d** | [**CancelGTTOrderData**](CancelGTTOrderData.md) |  | [optional] 

## Example

```python
from openapi_client.models.cancel_gtt_order_response import CancelGTTOrderResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CancelGTTOrderResponse from a JSON string
cancel_gtt_order_response_instance = CancelGTTOrderResponse.from_json(json)
# print the JSON string representation of the object
print CancelGTTOrderResponse.to_json()

# convert the object into a dict
cancel_gtt_order_response_dict = cancel_gtt_order_response_instance.to_dict()
# create an instance of CancelGTTOrderResponse from a dict
cancel_gtt_order_response_form_dict = cancel_gtt_order_response.from_dict(cancel_gtt_order_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


