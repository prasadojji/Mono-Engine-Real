# ExitOrderResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**s** | **str** |  | [optional] 
**d** | [**ExitSnoData**](ExitSnoData.md) |  | [optional] 

## Example

```python
from openapi_client.models.exit_order_response import ExitOrderResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ExitOrderResponse from a JSON string
exit_order_response_instance = ExitOrderResponse.from_json(json)
# print the JSON string representation of the object
print ExitOrderResponse.to_json()

# convert the object into a dict
exit_order_response_dict = exit_order_response_instance.to_dict()
# create an instance of ExitOrderResponse from a dict
exit_order_response_form_dict = exit_order_response.from_dict(exit_order_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


