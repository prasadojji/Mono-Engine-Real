# PositionsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**s** | **str** |  | [optional] 
**d** | [**List[PositionRecord]**](PositionRecord.md) |  | [optional] 

## Example

```python
from openapi_client.models.positions_response import PositionsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PositionsResponse from a JSON string
positions_response_instance = PositionsResponse.from_json(json)
# print the JSON string representation of the object
print PositionsResponse.to_json()

# convert the object into a dict
positions_response_dict = positions_response_instance.to_dict()
# create an instance of PositionsResponse from a dict
positions_response_form_dict = positions_response.from_dict(positions_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


