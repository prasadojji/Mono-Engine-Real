# SymbolStoreData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**sort_order** | **int** |  | [optional] 
**id_format** | **str** |  | [optional] 
**data** | **str** |  | [optional] 
**build_version** | **List[str]** |  | [optional] 
**append** | [**SymbolStoreAppender**](SymbolStoreAppender.md) |  | [optional] 

## Example

```python
from openapi_client.models.symbol_store_data import SymbolStoreData

# TODO update the JSON string below
json = "{}"
# create an instance of SymbolStoreData from a JSON string
symbol_store_data_instance = SymbolStoreData.from_json(json)
# print the JSON string representation of the object
print SymbolStoreData.to_json()

# convert the object into a dict
symbol_store_data_dict = symbol_store_data_instance.to_dict()
# create an instance of SymbolStoreData from a dict
symbol_store_data_form_dict = symbol_store_data.from_dict(symbol_store_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


