# ChartDataPointsChartPoints


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**bars** | **List[List[ChartPoints]]** |  | [optional] 
**sum_up_volume** | **int** |  | [optional] 

## Example

```python
from openapi_client.models.chart_data_points_chart_points import ChartDataPointsChartPoints

# TODO update the JSON string below
json = "{}"
# create an instance of ChartDataPointsChartPoints from a JSON string
chart_data_points_chart_points_instance = ChartDataPointsChartPoints.from_json(json)
# print the JSON string representation of the object
print ChartDataPointsChartPoints.to_json()

# convert the object into a dict
chart_data_points_chart_points_dict = chart_data_points_chart_points_instance.to_dict()
# create an instance of ChartDataPointsChartPoints from a dict
chart_data_points_chart_points_form_dict = chart_data_points_chart_points.from_dict(chart_data_points_chart_points_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


