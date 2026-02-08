# Holdings


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sym_id** | **str** |  | [optional] 
**sym** | [**TradeRecordSym**](TradeRecordSym.md) |  | [optional] 
**qty** | **float** | Quantity is sum of ( btstQuantity, holdingQuantity, brokerQuantity, unPledgedQty, beneficiaryQuantity, MaxOf(nonPoaQuantity,dpQuantity)) minus tradedQuantity | [optional] 
**avg_price** | **float** | Average buy price | [optional] 
**t1_qty** | **float** | T1 or BTST quantity | [optional] 
**saleable_qty** | **float** | Saleable quantity is sum of ( btstQuantity, holdingQuantity, unPledgedQty, beneficiaryQuantity, dpQuantity ) minus tradedQty | [optional] 
**pledge_qty** | **float** | Collateral or pledged quantity | [optional] 
**non_poa_qty** | **float** | Non POA quantity | [optional] 
**dp_qty** | **float** | DP holding quantity | [optional] 
**ben_qty** | **float** | Beneficiary quantity | [optional] 
**unpledged_qty** | **float** | Unpledged quantity | [optional] 
**broker_col_qty** | **float** | Broker collateral | [optional] 
**btst_colqty** | **float** | BTST collateral quantity | [optional] 
**used_qty** | **float** | Holding quantity used today | [optional] 
**traded_qty** | **float** | Holding quantity traded today | [optional] 
**realized_pnl** | **float** | &#39;realizedPnL   | [optional] 
**total_qty** | **float** |  | [optional] 
**trans_history** | **bool** |  | [optional] 
**day_qty** | **float** |  | [optional] 

## Example

```python
from openapi_client.models.holdings import Holdings

# TODO update the JSON string below
json = "{}"
# create an instance of Holdings from a JSON string
holdings_instance = Holdings.from_json(json)
# print the JSON string representation of the object
print Holdings.to_json()

# convert the object into a dict
holdings_dict = holdings_instance.to_dict()
# create an instance of Holdings from a dict
holdings_form_dict = holdings.from_dict(holdings_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


