# OrderMarginData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**available_margin** | **float** | Available margin to trade | [optional] 
**required_margin** | **float** | Required margin to trade | [optional] 
**shortfall** | **float** |  | [optional] 
**hold_qty** | **float** | This is applicable only for SELL order of Equity ( Delivery ) | [optional] 
**remarks** | **str** | Remarks is applicable for failure cases | [optional] 
**edis_auth_required** | **bool** | &#39;edisAuthEnabled&#39; flag should be consume in case of edis navigation | [optional] 

## Example

```python
from openapi_client.models.order_margin_data import OrderMarginData

# TODO update the JSON string below
json = "{}"
# create an instance of OrderMarginData from a JSON string
order_margin_data_instance = OrderMarginData.from_json(json)
# print the JSON string representation of the object
print OrderMarginData.to_json()

# convert the object into a dict
order_margin_data_dict = order_margin_data_instance.to_dict()
# create an instance of OrderMarginData from a dict
order_margin_data_form_dict = order_margin_data.from_dict(order_margin_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


