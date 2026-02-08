# ConstituentData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**change_per** | **float** |  | [optional] 
**weightage** | **float** |  | [optional] 
**contribution_point** | **float** |  | [optional] 

## Example

```python
from openapi_client.models.constituent_data import ConstituentData

# TODO update the JSON string below
json = "{}"
# create an instance of ConstituentData from a JSON string
constituent_data_instance = ConstituentData.from_json(json)
# print the JSON string representation of the object
print ConstituentData.to_json()

# convert the object into a dict
constituent_data_dict = constituent_data_instance.to_dict()
# create an instance of ConstituentData from a dict
constituent_data_form_dict = constituent_data.from_dict(constituent_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


