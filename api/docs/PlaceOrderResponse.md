# PlaceOrderResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**s** | **str** |  | [optional] 
**d** | [**PlaceOrderData**](PlaceOrderData.md) |  | [optional] 

## Example

```python
from openapi_client.models.place_order_response import PlaceOrderResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PlaceOrderResponse from a JSON string
place_order_response_instance = PlaceOrderResponse.from_json(json)
# print the JSON string representation of the object
print PlaceOrderResponse.to_json()

# convert the object into a dict
place_order_response_dict = place_order_response_instance.to_dict()
# create an instance of PlaceOrderResponse from a dict
place_order_response_form_dict = place_order_response.from_dict(place_order_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


