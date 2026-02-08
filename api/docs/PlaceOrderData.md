# PlaceOrderData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**msg** | **str** |  | [optional] 
**order_id** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.place_order_data import PlaceOrderData

# TODO update the JSON string below
json = "{}"
# create an instance of PlaceOrderData from a JSON string
place_order_data_instance = PlaceOrderData.from_json(json)
# print the JSON string representation of the object
print PlaceOrderData.to_json()

# convert the object into a dict
place_order_data_dict = place_order_data_instance.to_dict()
# create an instance of PlaceOrderData from a dict
place_order_data_form_dict = place_order_data.from_dict(place_order_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


