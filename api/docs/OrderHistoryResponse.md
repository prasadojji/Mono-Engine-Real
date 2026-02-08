# OrderHistoryResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**s** | **str** |  | [optional] 
**d** | [**OrderHistoryData**](OrderHistoryData.md) |  | [optional] 

## Example

```python
from openapi_client.models.order_history_response import OrderHistoryResponse

# TODO update the JSON string below
json = "{}"
# create an instance of OrderHistoryResponse from a JSON string
order_history_response_instance = OrderHistoryResponse.from_json(json)
# print the JSON string representation of the object
print OrderHistoryResponse.to_json()

# convert the object into a dict
order_history_response_dict = order_history_response_instance.to_dict()
# create an instance of OrderHistoryResponse from a dict
order_history_response_form_dict = order_history_response.from_dict(order_history_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


