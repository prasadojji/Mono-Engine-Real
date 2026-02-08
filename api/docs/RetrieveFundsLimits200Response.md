# RetrieveFundsLimits200Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**s** | **str** |  | [optional] 
**d** | [**LimitData**](LimitData.md) |  | [optional] 
**msg** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.retrieve_funds_limits200_response import RetrieveFundsLimits200Response

# TODO update the JSON string below
json = "{}"
# create an instance of RetrieveFundsLimits200Response from a JSON string
retrieve_funds_limits200_response_instance = RetrieveFundsLimits200Response.from_json(json)
# print the JSON string representation of the object
print RetrieveFundsLimits200Response.to_json()

# convert the object into a dict
retrieve_funds_limits200_response_dict = retrieve_funds_limits200_response_instance.to_dict()
# create an instance of RetrieveFundsLimits200Response from a dict
retrieve_funds_limits200_response_form_dict = retrieve_funds_limits200_response.from_dict(retrieve_funds_limits200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


