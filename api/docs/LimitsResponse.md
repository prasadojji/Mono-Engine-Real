# LimitsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**s** | **str** |  | [optional] 
**d** | [**LimitData**](LimitData.md) |  | [optional] 

## Example

```python
from openapi_client.models.limits_response import LimitsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of LimitsResponse from a JSON string
limits_response_instance = LimitsResponse.from_json(json)
# print the JSON string representation of the object
print LimitsResponse.to_json()

# convert the object into a dict
limits_response_dict = limits_response_instance.to_dict()
# create an instance of LimitsResponse from a dict
limits_response_form_dict = limits_response.from_dict(limits_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


