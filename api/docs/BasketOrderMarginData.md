# BasketOrderMarginData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**required_margin** | **float** | Required margin | [optional] 
**final_margin** | **float** | Final margin | [optional] 
**existing_margin_used** | **float** | Existing margin used | [optional] 
**combined_required_margin** | **float** | Combined required margin is a combination of required margin of an order and margin used | [optional] 
**combined_final_margin** | **float** | Combined Final margin is a combination of final margin of an order and margin used | [optional] 
**available_margin** | **float** | Available margin to trade | [optional] 

## Example

```python
from openapi_client.models.basket_order_margin_data import BasketOrderMarginData

# TODO update the JSON string below
json = "{}"
# create an instance of BasketOrderMarginData from a JSON string
basket_order_margin_data_instance = BasketOrderMarginData.from_json(json)
# print the JSON string representation of the object
print BasketOrderMarginData.to_json()

# convert the object into a dict
basket_order_margin_data_dict = basket_order_margin_data_instance.to_dict()
# create an instance of BasketOrderMarginData from a dict
basket_order_margin_data_form_dict = basket_order_margin_data.from_dict(basket_order_margin_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


