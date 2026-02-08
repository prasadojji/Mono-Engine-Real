# PlaceOrder200Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**s** | **str** |  | [optional] 
**d** | [**PlaceOrderData**](PlaceOrderData.md) |  | [optional] 
**msg** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.place_order200_response import PlaceOrder200Response

# TODO update the JSON string below
json = "{}"
# create an instance of PlaceOrder200Response from a JSON string
place_order200_response_instance = PlaceOrder200Response.from_json(json)
# print the JSON string representation of the object
print PlaceOrder200Response.to_json()

# convert the object into a dict
place_order200_response_dict = place_order200_response_instance.to_dict()
# create an instance of PlaceOrder200Response from a dict
place_order200_response_form_dict = place_order200_response.from_dict(place_order200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


