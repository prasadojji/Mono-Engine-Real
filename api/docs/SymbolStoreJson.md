# SymbolStoreJson


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**isin** | **str** |  | [optional] 
**disp_name** | **str** |  | [optional] 
**desc** | **str** |  | [optional] 
**exc_token** | **str** |  | [optional] 
**lot** | **str** |  | [optional] 
**tick** | **str** |  | [optional] 
**expiry** | **str** |  | [optional] 
**strike** | **str** |  | [optional] 
**opt_type** | **str** |  | [optional] 
**weekly** | **str** |  | [optional] 
**asset** | **str** |  | [optional] 
**instrument** | **str** |  | [optional] 
**symbol** | **str** |  | [optional] 
**series** | **str** |  | [optional] 
**exchange** | **str** |  | [optional] 
**freeze_qty** | **str** |  | [optional] 
**und_id** | **str** |  | [optional] 
**trd_unit** | **str** |  | [optional] 
**lot_multi** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.symbol_store_json import SymbolStoreJson

# TODO update the JSON string below
json = "{}"
# create an instance of SymbolStoreJson from a JSON string
symbol_store_json_instance = SymbolStoreJson.from_json(json)
# print the JSON string representation of the object
print SymbolStoreJson.to_json()

# convert the object into a dict
symbol_store_json_dict = symbol_store_json_instance.to_dict()
# create an instance of SymbolStoreJson from a dict
symbol_store_json_form_dict = symbol_store_json.from_dict(symbol_store_json_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


