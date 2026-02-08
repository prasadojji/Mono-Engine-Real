# LimitData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_credits** | **float** | Total credits is sum of availableCash, payIn, , adHocMargin, unclearedCash, brokerCollateralAmt,stockCollateral and auxCollateral | [optional] 
**avail_margin** | **float** | Available margin is calculated by ( totalcredits - marginused ) | [optional] 
**brokerage** | **float** | Brokerage amount | [optional] 
**avail_cash** | **float** | Cash Margin available | [optional] 
**peak_margin** | **float** | Peak margin used by the user | [optional] 
**pay_in** | **float** | Total Amount transferred using Payin&#39;s today | [optional] 
**span** | **float** | Span used | [optional] 
**realized_pnl** | **float** | Current realized PnL | [optional] 
**unrealized_pn_l** | **float** | Unrealized PnL | [optional] 
**exposure** | **float** | Exposure margin | [optional] 
**ad_hoc_margin** | **float** | Additional leverage amount or the amount added to handle system errors - by broker. | [optional] 
**stock_collateral** | **float** | Collateral amount calculated based on uploaded holdings | [optional] 
**option_premium** | **float** | Derivative Margin | [optional] 
**segment** | **str** | Segment | [optional] 
**pay_out** | **float** | Total amount requested for withdrawal today | [optional] 
**brk_collat_amount** | **float** | Broker Collateral Amount | [optional] 
**uncleared_cash** | **float** | Uncleared Cash | [optional] 
**aux_cash** | **float** | Aux day Cash | [optional] 
**aux_collat_amount** | **float** |  | [optional] 
**aux_uncleared_cash** | **float** |  | [optional] 
**day_cash** | **float** | Additional leverage amount or the amount added to handle system errors - by broker. | [optional] 
**turn_over_lmt** | **float** |  | [optional] 
**pend_ord_val_lmt** | **float** |  | [optional] 
**turnover** | **float** | Turnover | [optional] 
**pend_ord_value** | **float** | Pending Order value | [optional] 
**margin_used** | **float** | Total margin or total fund used today | [optional] 
**premium** | **float** | Premium used | [optional] 
**brokerage_derivatives_bo** | **float** | Brokerage Derivative Bracket Order | [optional] 
**brokerage_derivatives_margin** | **float** | Brokerage Derivative Margin | [optional] 
**opt_premium_der_marg** | **float** | Option premium Derivative Margin | [optional] 

## Example

```python
from openapi_client.models.limit_data import LimitData

# TODO update the JSON string below
json = "{}"
# create an instance of LimitData from a JSON string
limit_data_instance = LimitData.from_json(json)
# print the JSON string representation of the object
print LimitData.to_json()

# convert the object into a dict
limit_data_dict = limit_data_instance.to_dict()
# create an instance of LimitData from a dict
limit_data_form_dict = limit_data.from_dict(limit_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


