# ChartPoints


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**time** | **int** |  | [optional] 
**open** | **float** |  | [optional] 
**high** | **float** |  | [optional] 
**low** | **float** |  | [optional] 
**close** | **float** |  | [optional] 
**volume** | **int** |  | [optional] 
**minute_oi** | **int** |  | [optional] 

## Example

```python
from openapi_client.models.chart_points import ChartPoints

# TODO update the JSON string below
json = "{}"
# create an instance of ChartPoints from a JSON string
chart_points_instance = ChartPoints.from_json(json)
# print the JSON string representation of the object
print ChartPoints.to_json()

# convert the object into a dict
chart_points_dict = chart_points_instance.to_dict()
# create an instance of ChartPoints from a dict
chart_points_form_dict = chart_points.from_dict(chart_points_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


