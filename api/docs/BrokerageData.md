# BrokerageData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**charges** | **float** |  | [optional] 
**detailed_view** | [**List[Values]**](Values.md) |  | [optional] 

## Example

```python
from openapi_client.models.brokerage_data import BrokerageData

# TODO update the JSON string below
json = "{}"
# create an instance of BrokerageData from a JSON string
brokerage_data_instance = BrokerageData.from_json(json)
# print the JSON string representation of the object
print BrokerageData.to_json()

# convert the object into a dict
brokerage_data_dict = brokerage_data_instance.to_dict()
# create an instance of BrokerageData from a dict
brokerage_data_form_dict = brokerage_data.from_dict(brokerage_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


