# CancelOCOOrderData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**msg** | **str** |  | [optional] 
**order_id** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.cancel_oco_order_data import CancelOCOOrderData

# TODO update the JSON string below
json = "{}"
# create an instance of CancelOCOOrderData from a JSON string
cancel_oco_order_data_instance = CancelOCOOrderData.from_json(json)
# print the JSON string representation of the object
print CancelOCOOrderData.to_json()

# convert the object into a dict
cancel_oco_order_data_dict = cancel_oco_order_data_instance.to_dict()
# create an instance of CancelOCOOrderData from a dict
cancel_oco_order_data_form_dict = cancel_oco_order_data.from_dict(cancel_oco_order_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


