# ConvertPosition200Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**s** | **str** |  | [optional] 
**d** | [**IouMessage**](IouMessage.md) |  | [optional] 
**msg** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.convert_position200_response import ConvertPosition200Response

# TODO update the JSON string below
json = "{}"
# create an instance of ConvertPosition200Response from a JSON string
convert_position200_response_instance = ConvertPosition200Response.from_json(json)
# print the JSON string representation of the object
print ConvertPosition200Response.to_json()

# convert the object into a dict
convert_position200_response_dict = convert_position200_response_instance.to_dict()
# create an instance of ConvertPosition200Response from a dict
convert_position200_response_form_dict = convert_position200_response.from_dict(convert_position200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


