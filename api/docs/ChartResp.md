# ChartResp


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**s** | **str** |  | [optional] 
**d** | [**ChartDataPointsChartPoints**](ChartDataPointsChartPoints.md) |  | [optional] 

## Example

```python
from openapi_client.models.chart_resp import ChartResp

# TODO update the JSON string below
json = "{}"
# create an instance of ChartResp from a JSON string
chart_resp_instance = ChartResp.from_json(json)
# print the JSON string representation of the object
print ChartResp.to_json()

# convert the object into a dict
chart_resp_dict = chart_resp_instance.to_dict()
# create an instance of ChartResp from a dict
chart_resp_form_dict = chart_resp.from_dict(chart_resp_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


