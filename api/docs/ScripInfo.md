# ScripInfo


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sym_id** | **str** | Unique identifier of the symbol | [optional] 
**invest_by** | **str** | Investment type should be in qty or amount  | [optional] 
**qty** | **float** | No of shares to buy or sell. For derivatives, pass the quantity by multiplying with lot size. Example: To buy 1 lot of NIFTY option, pass the quantity as 50. | [optional] 
**amount** | **float** | Amount | [optional] 

## Example

```python
from openapi_client.models.scrip_info import ScripInfo

# TODO update the JSON string below
json = "{}"
# create an instance of ScripInfo from a JSON string
scrip_info_instance = ScripInfo.from_json(json)
# print the JSON string representation of the object
print ScripInfo.to_json()

# convert the object into a dict
scrip_info_dict = scrip_info_instance.to_dict()
# create an instance of ScripInfo from a dict
scrip_info_form_dict = scrip_info.from_dict(scrip_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


