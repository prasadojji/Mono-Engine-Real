# BasketOrderList

Basket order is basket of multiple orders

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sym_id** | **str** | Unique identifier of the symbol | 
**qty** | **float** | No of shares to buy or sell. For derivatives, pass the quantity by multiplying with lot size. Example: To buy 1 lot of NIFTY option, pass the quantity as 50. | 
**limit_price** | **float** | This is required only for limit and stop limit orders | [optional] 
**side** | **str** | Order side &#39;buy&#39; or &#39;sell&#39; | 
**type** | **str** | Price type of an order | 
**product** | **str** | Product type of an order. &#39;delivery&#39; is applicable for equities. &#39;normal&#39; is applicable for derivatives. &#39;intraday&#39; is applicable for both equity and derivatives | 
**trig_price** | **float** | This is required only for stoploss limit and stoploss market orders | [optional] 

## Example

```python
from openapi_client.models.basket_order_list import BasketOrderList

# TODO update the JSON string below
json = "{}"
# create an instance of BasketOrderList from a JSON string
basket_order_list_instance = BasketOrderList.from_json(json)
# print the JSON string representation of the object
print BasketOrderList.to_json()

# convert the object into a dict
basket_order_list_dict = basket_order_list_instance.to_dict()
# create an instance of BasketOrderList from a dict
basket_order_list_form_dict = basket_order_list.from_dict(basket_order_list_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


