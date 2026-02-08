# GetPositions200Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**s** | **str** |  | [optional] 
**d** | [**List[PositionRecord]**](PositionRecord.md) |  | [optional] 
**msg** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.get_positions200_response import GetPositions200Response

# TODO update the JSON string below
json = "{}"
# create an instance of GetPositions200Response from a JSON string
get_positions200_response_instance = GetPositions200Response.from_json(json)
# print the JSON string representation of the object
print GetPositions200Response.to_json()

# convert the object into a dict
get_positions200_response_dict = get_positions200_response_instance.to_dict()
# create an instance of GetPositions200Response from a dict
get_positions200_response_form_dict = get_positions200_response.from_dict(get_positions200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


