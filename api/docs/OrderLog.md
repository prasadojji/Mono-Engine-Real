# OrderLog


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**msg** | **str** |  | [optional] 
**fill_id** | **str** |  | [optional] 
**fill_price** | **float** |  | [optional] 
**fill_qty** | **float** |  | [optional] 
**time** | **str** | Order log time in the format &#39;dd-MM-yyyy HH:mm:ss&#39; | [optional] 

## Example

```python
from openapi_client.models.order_log import OrderLog

# TODO update the JSON string below
json = "{}"
# create an instance of OrderLog from a JSON string
order_log_instance = OrderLog.from_json(json)
# print the JSON string representation of the object
print OrderLog.to_json()

# convert the object into a dict
order_log_dict = order_log_instance.to_dict()
# create an instance of OrderLog from a dict
order_log_form_dict = order_log.from_dict(order_log_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


