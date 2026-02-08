# PositionRecord


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sym_id** | **str** |  | [optional] 
**product** | **str** |  | [optional] 
**buy_qty** | **float** |  | [optional] 
**buy_value** | **float** |  | [optional] 
**buy_avg_price** | **float** |  | [optional] 
**sell_qty** | **float** |  | [optional] 
**sell_value** | **float** |  | [optional] 
**sell_avg_price** | **float** |  | [optional] 
**cf_qty** | **float** | Carry forward positions quantity | [optional] 
**cf_value** | **float** | Carry forward position value and it is calculated using cfQty * cfAvgPrice * multiplier * pricefactor. | [optional] 
**cf_avg_price** | **float** | The settlement price of the scrip from the last trading day, is used to calculate the mark-to-market (MTM) of the positions | [optional] 
**net_qty** | **float** |  | [optional] 
**net_avg_price** | **float** | The net average price is based on today&#39;s positions and carryforward positions. For carryforward positions, the average would be the settlement price from the last trading day (cfavgprice), while for today&#39;s positions, the average would be the day average price (dayavgprice) | [optional] 
**net_value** | **float** | Net value of the position based on the net average price (netavgprice) | [optional] 
**realized_pnl** | **float** | Realized pnl value | [optional] 
**price_factor** | **float** | Used for pnl calculations. PriceFactor:(General Numerator * Price Numerator)/(General Denominator * Price Denopminator) | [optional] 
**multiplier** | **float** |  | [optional] 
**sym** | [**TradeRecordSym**](TradeRecordSym.md) |  | [optional] 
**cf_org_avg_price** | **float** | The actual buy/sell price of the position, is used to calculate the overall PNL of the positions. | [optional] 
**cf_org_value** | **float** | Carry forward position original value and it is calculated using cfQty * cfOrgAvgPrice * multiplier * pricefactor | [optional] 
**net_org_avg_price** | **float** | The net original average price is based on today&#39;s positions and carryforward positions. For carryforward positions, the average would be the actual buy or sell price of the scrip, while for today&#39;s positions, the average would be the day average price (dayavgprice) | [optional] 
**net_org_value** | **float** | Net original value of the position based on the net original average price (netorgavgprice) | [optional] 
**realized_org_pnl** | **float** |  | [optional] 
**day_pos** | [**DayPosition**](DayPosition.md) |  | [optional] 
**convert_pos** | **bool** |  | [optional] 
**net_premium** | **float** |  | [optional] 
**trans_history** | **bool** |  | [optional] 
**create_tsl** | **bool** |  | [optional] 

## Example

```python
from openapi_client.models.position_record import PositionRecord

# TODO update the JSON string below
json = "{}"
# create an instance of PositionRecord from a JSON string
position_record_instance = PositionRecord.from_json(json)
# print the JSON string representation of the object
print PositionRecord.to_json()

# convert the object into a dict
position_record_dict = position_record_instance.to_dict()
# create an instance of PositionRecord from a dict
position_record_form_dict = position_record.from_dict(position_record_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


