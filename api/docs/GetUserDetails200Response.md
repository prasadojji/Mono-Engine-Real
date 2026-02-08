# GetUserDetails200Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**s** | **str** |  | [optional] 
**d** | [**ClientDetailsData**](ClientDetailsData.md) |  | [optional] 
**msg** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.get_user_details200_response import GetUserDetails200Response

# TODO update the JSON string below
json = "{}"
# create an instance of GetUserDetails200Response from a JSON string
get_user_details200_response_instance = GetUserDetails200Response.from_json(json)
# print the JSON string representation of the object
print GetUserDetails200Response.to_json()

# convert the object into a dict
get_user_details200_response_dict = get_user_details200_response_instance.to_dict()
# create an instance of GetUserDetails200Response from a dict
get_user_details200_response_form_dict = get_user_details200_response.from_dict(get_user_details200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


