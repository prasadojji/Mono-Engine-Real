# LimitsV1Data


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_credits** | **float** | Total credits is sum of availableCash, payIn, , adHocMargin, unclearedCash, brokerCollateralAmt,stockCollateral and auxCollateral | [optional] 
**avail_margin** | **float** | Available margin is calculated by ( totalcredits - marginused ) | [optional] 
**margin_used** | **float** | Total margin or total fund used today | [optional] 
**detailed_view** | [**List[DetailedView]**](DetailedView.md) |  | [optional] 

## Example

```python
from openapi_client.models.limits_v1_data import LimitsV1Data

# TODO update the JSON string below
json = "{}"
# create an instance of LimitsV1Data from a JSON string
limits_v1_data_instance = LimitsV1Data.from_json(json)
# print the JSON string representation of the object
print LimitsV1Data.to_json()

# convert the object into a dict
limits_v1_data_dict = limits_v1_data_instance.to_dict()
# create an instance of LimitsV1Data from a dict
limits_v1_data_form_dict = limits_v1_data.from_dict(limits_v1_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


