# OrderHistoryData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**order_id** | **str** |  | [optional] 
**status** | **str** |  | [optional] 
**reason** | **str** |  | [optional] 
**avg_price** | **float** |  | [optional] 
**total_fill_qty** | **float** |  | [optional] 
**remarks** | **str** | Remarks added while placing an order. | [optional] 
**history** | [**List[OrderLog]**](OrderLog.md) |  | [optional] 

## Example

```python
from openapi_client.models.order_history_data import OrderHistoryData

# TODO update the JSON string below
json = "{}"
# create an instance of OrderHistoryData from a JSON string
order_history_data_instance = OrderHistoryData.from_json(json)
# print the JSON string representation of the object
print OrderHistoryData.to_json()

# convert the object into a dict
order_history_data_dict = order_history_data_instance.to_dict()
# create an instance of OrderHistoryData from a dict
order_history_data_form_dict = order_history_data.from_dict(order_history_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


