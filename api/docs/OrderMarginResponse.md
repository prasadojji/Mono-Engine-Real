# OrderMarginResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**s** | **str** |  | [optional] 
**d** | [**OrderMarginData**](OrderMarginData.md) |  | [optional] 

## Example

```python
from openapi_client.models.order_margin_response import OrderMarginResponse

# TODO update the JSON string below
json = "{}"
# create an instance of OrderMarginResponse from a JSON string
order_margin_response_instance = OrderMarginResponse.from_json(json)
# print the JSON string representation of the object
print OrderMarginResponse.to_json()

# convert the object into a dict
order_margin_response_dict = order_margin_response_instance.to_dict()
# create an instance of OrderMarginResponse from a dict
order_margin_response_form_dict = order_margin_response.from_dict(order_margin_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


