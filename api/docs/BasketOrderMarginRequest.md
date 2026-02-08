# BasketOrderMarginRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**basket_orders** | [**List[BasketOrderList]**](BasketOrderList.md) | Basket order is basket of multiple orders | [optional] 

## Example

```python
from openapi_client.models.basket_order_margin_request import BasketOrderMarginRequest

# TODO update the JSON string below
json = "{}"
# create an instance of BasketOrderMarginRequest from a JSON string
basket_order_margin_request_instance = BasketOrderMarginRequest.from_json(json)
# print the JSON string representation of the object
print BasketOrderMarginRequest.to_json()

# convert the object into a dict
basket_order_margin_request_dict = basket_order_margin_request_instance.to_dict()
# create an instance of BasketOrderMarginRequest from a dict
basket_order_margin_request_form_dict = basket_order_margin_request.from_dict(basket_order_margin_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


