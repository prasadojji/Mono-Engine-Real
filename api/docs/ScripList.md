# ScripList


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**s** | **str** |  | [optional] 
**d** | [**List[SymbolStoreJson]**](SymbolStoreJson.md) |  | [optional] 

## Example

```python
from openapi_client.models.scrip_list import ScripList

# TODO update the JSON string below
json = "{}"
# create an instance of ScripList from a JSON string
scrip_list_instance = ScripList.from_json(json)
# print the JSON string representation of the object
print ScripList.to_json()

# convert the object into a dict
scrip_list_dict = scrip_list_instance.to_dict()
# create an instance of ScripList from a dict
scrip_list_form_dict = scrip_list.from_dict(scrip_list_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


