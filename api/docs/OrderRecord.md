# OrderRecord


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sym_id** | **str** |  | [optional] 
**status** | **str** |  | [optional] 
**qty** | **float** | Order quantity | [optional] 
**side** | **str** |  | [optional] 
**type** | **str** |  | [optional] 
**validity** | **str** |  | [optional] 
**valid_till** | **str** |  | [optional] 
**source** | **str** |  | [optional] 
**limit_price** | **float** |  | [optional] 
**exch_order_id** | **str** |  | [optional] 
**disc_qty** | **float** |  | [optional] 
**product** | **str** |  | [optional] 
**exch_time** | **str** | Exchange order time in the format &#39;dd-MM-yyyy HH:mm:ss&#39; | [optional] 
**order_id** | **str** |  | [optional] 
**order_time** | **str** | Order time in the format &#39;dd-MM-yyyy HH:mm:ss&#39; | [optional] 
**avg_price** | **float** |  | [optional] 
**amo** | **bool** |  | [optional] 
**fill_qty** | **float** |  | [optional] 
**trig_price** | **float** | This is required only for stoploss limit and stoploss market orders | [optional] 
**reason** | **str** |  | [optional] 
**pending_qty** | **float** |  | [optional] 
**sym** | [**TradeRecordSym**](TradeRecordSym.md) |  | [optional] 
**mkt_prot** | **float** |  | [optional] 
**stop_trig_price** | **float** | Stop loss leg order trigger price. | [optional] 
**target_price** | **float** | Target order or Profit order price | [optional] 
**trailing_stop_price** | **float** | Trailing stop loss price. | [optional] 
**remarks** | **str** | Remarks added while placing an order. | [optional] 
**leg_type** | **str** | Leg Type. Applicable only for Cover and Bracket order. | [optional] 
**main_leg_order_id** | **str** | Main leg order id. Applicable only for Bracket and Cover order. It is used to exit the order. | [optional] 
**order_value** | **float** |  | [optional] 
**trade_value** | **float** | &#39;tradeValue&#39; is filled quantity * average price | [optional] 
**alg_type** | **str** | Algo type &#39;trailing&#39; or &#39;regular&#39;  | [optional] 
**modifiable** | **bool** |  | [optional] 
**cancellable** | **bool** |  | [optional] 
**exitable** | **bool** |  | [optional] 
**retriable** | **bool** |  | [optional] 
**order_poll** | **bool** |  | [optional] 
**stop_limit_price** | **float** |  | [optional] 

## Example

```python
from openapi_client.models.order_record import OrderRecord

# TODO update the JSON string below
json = "{}"
# create an instance of OrderRecord from a JSON string
order_record_instance = OrderRecord.from_json(json)
# print the JSON string representation of the object
print OrderRecord.to_json()

# convert the object into a dict
order_record_dict = order_record_instance.to_dict()
# create an instance of OrderRecord from a dict
order_record_form_dict = order_record.from_dict(order_record_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


