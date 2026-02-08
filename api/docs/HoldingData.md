# HoldingData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**holdings** | [**List[Holdings]**](Holdings.md) |  | [optional] 
**has_non_poa_record** | **bool** |  | [optional] 

## Example

```python
from openapi_client.models.holding_data import HoldingData

# TODO update the JSON string below
json = "{}"
# create an instance of HoldingData from a JSON string
holding_data_instance = HoldingData.from_json(json)
# print the JSON string representation of the object
print HoldingData.to_json()

# convert the object into a dict
holding_data_dict = holding_data_instance.to_dict()
# create an instance of HoldingData from a dict
holding_data_form_dict = holding_data.from_dict(holding_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


