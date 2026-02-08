# OauthError


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**error** | **str** |  | [optional] 
**error_desc** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.oauth_error import OauthError

# TODO update the JSON string below
json = "{}"
# create an instance of OauthError from a JSON string
oauth_error_instance = OauthError.from_json(json)
# print the JSON string representation of the object
print OauthError.to_json()

# convert the object into a dict
oauth_error_dict = oauth_error_instance.to_dict()
# create an instance of OauthError from a dict
oauth_error_form_dict = oauth_error.from_dict(oauth_error_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


