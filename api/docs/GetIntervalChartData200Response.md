# GetIntervalChartData200Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**s** | **str** |  | [optional] 
**d** | [**ChartDataPointsChartPoints**](ChartDataPointsChartPoints.md) |  | [optional] 
**msg** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.get_interval_chart_data200_response import GetIntervalChartData200Response

# TODO update the JSON string below
json = "{}"
# create an instance of GetIntervalChartData200Response from a JSON string
get_interval_chart_data200_response_instance = GetIntervalChartData200Response.from_json(json)
# print the JSON string representation of the object
print GetIntervalChartData200Response.to_json()

# convert the object into a dict
get_interval_chart_data200_response_dict = get_interval_chart_data200_response_instance.to_dict()
# create an instance of GetIntervalChartData200Response from a dict
get_interval_chart_data200_response_form_dict = get_interval_chart_data200_response.from_dict(get_interval_chart_data200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


