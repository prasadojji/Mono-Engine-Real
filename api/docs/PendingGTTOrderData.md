# PendingGTTOrderData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sym_id** | **str** |  | [optional] 
**exchange** | **str** |  | [optional] 
**order_id** | **str** |  | [optional] 
**side** | **str** |  | [optional] 
**trigger_type** | **str** |  | [optional] 
**single** | [**PlaceOrderParamsData**](PlaceOrderParamsData.md) |  | [optional] 
**stop_loss** | [**PlaceOrderParamsData**](PlaceOrderParamsData.md) |  | [optional] 
**target** | [**PlaceOrderParamsData**](PlaceOrderParamsData.md) |  | [optional] 

## Example

```python
from openapi_client.models.pending_gtt_order_data import PendingGTTOrderData

# TODO update the JSON string below
json = "{}"
# create an instance of PendingGTTOrderData from a JSON string
pending_gtt_order_data_instance = PendingGTTOrderData.from_json(json)
# print the JSON string representation of the object
print PendingGTTOrderData.to_json()

# convert the object into a dict
pending_gtt_order_data_dict = pending_gtt_order_data_instance.to_dict()
# create an instance of PendingGTTOrderData from a dict
pending_gtt_order_data_form_dict = pending_gtt_order_data.from_dict(pending_gtt_order_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


