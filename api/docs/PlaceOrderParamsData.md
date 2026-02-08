# PlaceOrderParamsData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**remarks** | **str** | Any message entered during order entry | [optional] 
**trig_price** | **float** | Trigger price with respect to LTP | [optional] 
**product** | **str** | Product type of an order. &#39;delivery&#39; is applicable for equities. &#39;normal&#39; is applicable for derivatives. &#39;intraday&#39; is applicable for both equity and derivatives | [optional] 
**type** | **str** |  | [optional] 
**qty** | **float** |  | [optional] 
**price** | **float** |  | [optional] 

## Example

```python
from openapi_client.models.place_order_params_data import PlaceOrderParamsData

# TODO update the JSON string below
json = "{}"
# create an instance of PlaceOrderParamsData from a JSON string
place_order_params_data_instance = PlaceOrderParamsData.from_json(json)
# print the JSON string representation of the object
print PlaceOrderParamsData.to_json()

# convert the object into a dict
place_order_params_data_dict = place_order_params_data_instance.to_dict()
# create an instance of PlaceOrderParamsData from a dict
place_order_params_data_form_dict = place_order_params_data.from_dict(place_order_params_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


