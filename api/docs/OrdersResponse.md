# OrdersResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**s** | **str** |  | [optional] 
**d** | [**List[OrderRecord]**](OrderRecord.md) |  | [optional] 

## Example

```python
from openapi_client.models.orders_response import OrdersResponse

# TODO update the JSON string below
json = "{}"
# create an instance of OrdersResponse from a JSON string
orders_response_instance = OrdersResponse.from_json(json)
# print the JSON string representation of the object
print OrdersResponse.to_json()

# convert the object into a dict
orders_response_dict = orders_response_instance.to_dict()
# create an instance of OrdersResponse from a dict
orders_response_form_dict = orders_response.from_dict(orders_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


