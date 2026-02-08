# PendingGTTOrders200Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**s** | **str** |  | [optional] 
**d** | [**List[PendingGTTOrderData]**](PendingGTTOrderData.md) |  | [optional] 
**msg** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.pending_gtt_orders200_response import PendingGTTOrders200Response

# TODO update the JSON string below
json = "{}"
# create an instance of PendingGTTOrders200Response from a JSON string
pending_gtt_orders200_response_instance = PendingGTTOrders200Response.from_json(json)
# print the JSON string representation of the object
print PendingGTTOrders200Response.to_json()

# convert the object into a dict
pending_gtt_orders200_response_dict = pending_gtt_orders200_response_instance.to_dict()
# create an instance of PendingGTTOrders200Response from a dict
pending_gtt_orders200_response_form_dict = pending_gtt_orders200_response.from_dict(pending_gtt_orders200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


