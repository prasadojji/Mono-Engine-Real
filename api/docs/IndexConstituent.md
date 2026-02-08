# IndexConstituent


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**constituents** | [**List[ConstituentData]**](ConstituentData.md) |  | [optional] 
**gainer_count** | **int** |  | [optional] 
**loser_count** | **int** |  | [optional] 
**normal_count** | **int** |  | [optional] 

## Example

```python
from openapi_client.models.index_constituent import IndexConstituent

# TODO update the JSON string below
json = "{}"
# create an instance of IndexConstituent from a JSON string
index_constituent_instance = IndexConstituent.from_json(json)
# print the JSON string representation of the object
print IndexConstituent.to_json()

# convert the object into a dict
index_constituent_dict = index_constituent_instance.to_dict()
# create an instance of IndexConstituent from a dict
index_constituent_form_dict = index_constituent.from_dict(index_constituent_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


