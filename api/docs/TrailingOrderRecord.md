# TrailingOrderRecord


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sym_id** | **str** |  | [optional] 
**order_id** | **str** |  | [optional] 
**side** | **str** |  | [optional] 
**type** | **str** |  | [optional] 
**product** | **str** |  | [optional] 
**validity** | **str** |  | [optional] 
**qty** | **float** | Order quantity | [optional] 
**limit_price** | **float** |  | [optional] 
**target_price** | **float** | Target order or Profit order price | [optional] 
**trailing_stop_price** | **float** | Trailing stop loss price. | [optional] 
**reason** | **str** |  | [optional] 
**price_factor** | **float** | Used for pnl calculations. PriceFactor:(General Numerator * Price Numerator)/(General Denominator * Price Denopminator) | [optional] 
**multiplier** | **float** |  | [optional] 
**trig_price** | **float** | This is required only for stoploss limit and stoploss market orders | [optional] 
**status** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.trailing_order_record import TrailingOrderRecord

# TODO update the JSON string below
json = "{}"
# create an instance of TrailingOrderRecord from a JSON string
trailing_order_record_instance = TrailingOrderRecord.from_json(json)
# print the JSON string representation of the object
print TrailingOrderRecord.to_json()

# convert the object into a dict
trailing_order_record_dict = trailing_order_record_instance.to_dict()
# create an instance of TrailingOrderRecord from a dict
trailing_order_record_form_dict = trailing_order_record.from_dict(trailing_order_record_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


