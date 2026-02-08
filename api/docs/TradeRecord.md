# TradeRecord


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sym_id** | **str** |  | [optional] 
**side** | **str** |  | [optional] 
**type** | **str** |  | [optional] 
**validity** | **str** |  | [optional] 
**product** | **str** |  | [optional] 
**order_id** | **str** |  | [optional] 
**fill_id** | **str** |  | [optional] 
**fill_qty** | **float** |  | [optional] 
**fill_price** | **float** |  | [optional] 
**fill_value** | **float** |  | [optional] 
**time** | **str** | Traded time in the format &#39;dd-MM-yyyy HH:mm:ss&#39; | [optional] 
**exch_order_id** | **str** |  | [optional] 
**avg_price** | **float** |  | [optional] 
**sym** | [**TradeRecordSym**](TradeRecordSym.md) |  | [optional] 
**remarks** | **str** | Remarks added while placing an order. | [optional] 
**leg_type** | **str** | Leg Type. Applicable only for Cover and Bracket order. | [optional] 
**main_leg_order_id** | **str** | Main leg order id. Applicable only for Bracket and Cover order. It is used to exit the order. | [optional] 

## Example

```python
from openapi_client.models.trade_record import TradeRecord

# TODO update the JSON string below
json = "{}"
# create an instance of TradeRecord from a JSON string
trade_record_instance = TradeRecord.from_json(json)
# print the JSON string representation of the object
print TradeRecord.to_json()

# convert the object into a dict
trade_record_dict = trade_record_instance.to_dict()
# create an instance of TradeRecord from a dict
trade_record_form_dict = trade_record.from_dict(trade_record_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


