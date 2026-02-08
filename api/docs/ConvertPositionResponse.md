# ConvertPositionResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**s** | **str** |  | [optional] 
**d** | [**IouMessage**](IouMessage.md) |  | [optional] 

## Example

```python
from openapi_client.models.convert_position_response import ConvertPositionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ConvertPositionResponse from a JSON string
convert_position_response_instance = ConvertPositionResponse.from_json(json)
# print the JSON string representation of the object
print ConvertPositionResponse.to_json()

# convert the object into a dict
convert_position_response_dict = convert_position_response_instance.to_dict()
# create an instance of ConvertPositionResponse from a dict
convert_position_response_form_dict = convert_position_response.from_dict(convert_position_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


