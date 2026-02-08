# LoginData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**login_time** | **str** |  | [optional] 
**user_name** | **str** |  | [optional] 
**email** | **str** |  | [optional] 
**token** | **str** |  | [optional] 
**pin_status** | **int** |  | [optional] 
**mobile** | **str** |  | [optional] 
**action** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.login_data import LoginData

# TODO update the JSON string below
json = "{}"
# create an instance of LoginData from a JSON string
login_data_instance = LoginData.from_json(json)
# print the JSON string representation of the object
print LoginData.to_json()

# convert the object into a dict
login_data_dict = login_data_instance.to_dict()
# create an instance of LoginData from a dict
login_data_form_dict = login_data.from_dict(login_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


