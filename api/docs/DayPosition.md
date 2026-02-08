# DayPosition

Today's position details

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**day_qty** | **float** |  | [optional] 
**day_avg** | **float** |  | [optional] 
**day_realized_pnl** | **float** |  | [optional] 
**day_net_value** | **float** |  dayNetValue is calculated by &#39;dayBuyValue - daySellValue&#39;. | [optional] 
**convert_pos** | **bool** |  | [optional] 
**day_premium** | **float** |  | [optional] 

## Example

```python
from openapi_client.models.day_position import DayPosition

# TODO update the JSON string below
json = "{}"
# create an instance of DayPosition from a JSON string
day_position_instance = DayPosition.from_json(json)
# print the JSON string representation of the object
print DayPosition.to_json()

# convert the object into a dict
day_position_dict = day_position_instance.to_dict()
# create an instance of DayPosition from a dict
day_position_form_dict = day_position.from_dict(day_position_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


