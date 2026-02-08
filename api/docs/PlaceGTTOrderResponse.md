# PlaceGTTOrderResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**s** | **str** |  | [optional] 
**d** | [**PlaceGTTOrderData**](PlaceGTTOrderData.md) |  | [optional] 

## Example

```python
from openapi_client.models.place_gtt_order_response import PlaceGTTOrderResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PlaceGTTOrderResponse from a JSON string
place_gtt_order_response_instance = PlaceGTTOrderResponse.from_json(json)
# print the JSON string representation of the object
print PlaceGTTOrderResponse.to_json()

# convert the object into a dict
place_gtt_order_response_dict = place_gtt_order_response_instance.to_dict()
# create an instance of PlaceGTTOrderResponse from a dict
place_gtt_order_response_form_dict = place_gtt_order_response.from_dict(place_gtt_order_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


