# GetBasketOrderMargin200Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**s** | **str** |  | [optional] 
**d** | [**BasketOrderMarginData**](BasketOrderMarginData.md) |  | [optional] 
**msg** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.get_basket_order_margin200_response import GetBasketOrderMargin200Response

# TODO update the JSON string below
json = "{}"
# create an instance of GetBasketOrderMargin200Response from a JSON string
get_basket_order_margin200_response_instance = GetBasketOrderMargin200Response.from_json(json)
# print the JSON string representation of the object
print GetBasketOrderMargin200Response.to_json()

# convert the object into a dict
get_basket_order_margin200_response_dict = get_basket_order_margin200_response_instance.to_dict()
# create an instance of GetBasketOrderMargin200Response from a dict
get_basket_order_margin200_response_form_dict = get_basket_order_margin200_response.from_dict(get_basket_order_margin200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


