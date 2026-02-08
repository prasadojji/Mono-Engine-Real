# PendingGTTOrderResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**s** | **str** |  | [optional] 
**d** | [**List[PendingGTTOrderData]**](PendingGTTOrderData.md) |  | [optional] 

## Example

```python
from openapi_client.models.pending_gtt_order_response import PendingGTTOrderResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PendingGTTOrderResponse from a JSON string
pending_gtt_order_response_instance = PendingGTTOrderResponse.from_json(json)
# print the JSON string representation of the object
print PendingGTTOrderResponse.to_json()

# convert the object into a dict
pending_gtt_order_response_dict = pending_gtt_order_response_instance.to_dict()
# create an instance of PendingGTTOrderResponse from a dict
pending_gtt_order_response_form_dict = pending_gtt_order_response.from_dict(pending_gtt_order_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


