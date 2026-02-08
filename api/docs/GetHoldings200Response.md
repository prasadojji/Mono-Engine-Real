# GetHoldings200Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**s** | **str** |  | [optional] 
**d** | [**HoldingData**](HoldingData.md) |  | [optional] 
**msg** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.get_holdings200_response import GetHoldings200Response

# TODO update the JSON string below
json = "{}"
# create an instance of GetHoldings200Response from a JSON string
get_holdings200_response_instance = GetHoldings200Response.from_json(json)
# print the JSON string representation of the object
print GetHoldings200Response.to_json()

# convert the object into a dict
get_holdings200_response_dict = get_holdings200_response_instance.to_dict()
# create an instance of GetHoldings200Response from a dict
get_holdings200_response_form_dict = get_holdings200_response.from_dict(get_holdings200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


