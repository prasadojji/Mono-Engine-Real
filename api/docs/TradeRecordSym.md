# TradeRecordSym


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**symbol** | **str** |  | [optional] 
**trad_symbol** | **str** |  | [optional] 
**exchange** | **str** |  | [optional] 
**lot** | **str** |  | [optional] 
**instrument** | **str** |  | [optional] 
**company_name** | **str** |  | [optional] 
**expiry** | **str** |  | [optional] 
**disp_symbol** | **str** |  | [optional] 
**asset** | **str** |  | [optional] 
**empty** | **bool** |  | [optional] 

## Example

```python
from openapi_client.models.trade_record_sym import TradeRecordSym

# TODO update the JSON string below
json = "{}"
# create an instance of TradeRecordSym from a JSON string
trade_record_sym_instance = TradeRecordSym.from_json(json)
# print the JSON string representation of the object
print TradeRecordSym.to_json()

# convert the object into a dict
trade_record_sym_dict = trade_record_sym_instance.to_dict()
# create an instance of TradeRecordSym from a dict
trade_record_sym_form_dict = trade_record_sym.from_dict(trade_record_sym_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


