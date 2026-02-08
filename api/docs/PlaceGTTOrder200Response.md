# PlaceGTTOrder200Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**s** | **str** |  | [optional] 
**d** | [**PlaceGTTOrderData**](PlaceGTTOrderData.md) |  | [optional] 
**msg** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.place_gtt_order200_response import PlaceGTTOrder200Response

# TODO update the JSON string below
json = "{}"
# create an instance of PlaceGTTOrder200Response from a JSON string
place_gtt_order200_response_instance = PlaceGTTOrder200Response.from_json(json)
# print the JSON string representation of the object
print PlaceGTTOrder200Response.to_json()

# convert the object into a dict
place_gtt_order200_response_dict = place_gtt_order200_response_instance.to_dict()
# create an instance of PlaceGTTOrder200Response from a dict
place_gtt_order200_response_form_dict = place_gtt_order200_response.from_dict(place_gtt_order200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


