# SSOLoginData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**login_time** | **str** |  | [optional] 
**user_name** | **str** |  | [optional] 
**email** | **str** |  | [optional] 
**token** | **str** |  | [optional] 
**pin_status** | **int** |  | [optional] 
**action** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.sso_login_data import SSOLoginData

# TODO update the JSON string below
json = "{}"
# create an instance of SSOLoginData from a JSON string
sso_login_data_instance = SSOLoginData.from_json(json)
# print the JSON string representation of the object
print SSOLoginData.to_json()

# convert the object into a dict
sso_login_data_dict = sso_login_data_instance.to_dict()
# create an instance of SSOLoginData from a dict
sso_login_data_form_dict = sso_login_data.from_dict(sso_login_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


