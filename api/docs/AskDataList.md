# AskDataList

List of ASK data

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**no** | **int** |  | [optional] 
**price** | **int** |  | [optional] 
**qty** | **int** |  | [optional] 

## Example

```python
from openapi_client.models.ask_data_list import AskDataList

# TODO update the JSON string below
json = "{}"
# create an instance of AskDataList from a JSON string
ask_data_list_instance = AskDataList.from_json(json)
# print the JSON string representation of the object
print AskDataList.to_json()

# convert the object into a dict
ask_data_list_dict = ask_data_list_instance.to_dict()
# create an instance of AskDataList from a dict
ask_data_list_form_dict = ask_data_list.from_dict(ask_data_list_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


