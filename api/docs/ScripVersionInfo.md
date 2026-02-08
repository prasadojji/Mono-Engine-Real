# ScripVersionInfo


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**version** | **int** |  | [optional] 
**updated** | **bool** |  | [optional] 
**symbol_store** | [**List[SymbolStoreData]**](SymbolStoreData.md) |  | [optional] 

## Example

```python
from openapi_client.models.scrip_version_info import ScripVersionInfo

# TODO update the JSON string below
json = "{}"
# create an instance of ScripVersionInfo from a JSON string
scrip_version_info_instance = ScripVersionInfo.from_json(json)
# print the JSON string representation of the object
print ScripVersionInfo.to_json()

# convert the object into a dict
scrip_version_info_dict = scrip_version_info_instance.to_dict()
# create an instance of ScripVersionInfo from a dict
scrip_version_info_form_dict = scrip_version_info.from_dict(scrip_version_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


