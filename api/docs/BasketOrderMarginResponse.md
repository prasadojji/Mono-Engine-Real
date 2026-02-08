# BasketOrderMarginResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**s** | **str** |  | [optional] 
**d** | [**BasketOrderMarginData**](BasketOrderMarginData.md) |  | [optional] 

## Example

```python
from openapi_client.models.basket_order_margin_response import BasketOrderMarginResponse

# TODO update the JSON string below
json = "{}"
# create an instance of BasketOrderMarginResponse from a JSON string
basket_order_margin_response_instance = BasketOrderMarginResponse.from_json(json)
# print the JSON string representation of the object
print BasketOrderMarginResponse.to_json()

# convert the object into a dict
basket_order_margin_response_dict = basket_order_margin_response_instance.to_dict()
# create an instance of BasketOrderMarginResponse from a dict
basket_order_margin_response_form_dict = basket_order_margin_response.from_dict(basket_order_margin_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


