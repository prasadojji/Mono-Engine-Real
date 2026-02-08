# ClientDetailsData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **str** |  | [optional] 
**user_name** | **str** |  | [optional] 
**mobile** | **str** |  | [optional] 
**email** | **str** |  | [optional] 
**pan** | **str** |  | [optional] 
**dp_id** | **str** |  | [optional] 
**bank_details** | [**List[BankDtls]**](BankDtls.md) |  | [optional] 
**dp_ids** | **List[str]** |  | [optional] 
**products** | **List[str]** |  | [optional] 
**segments** | **List[str]** |  | [optional] 

## Example

```python
from openapi_client.models.client_details_data import ClientDetailsData

# TODO update the JSON string below
json = "{}"
# create an instance of ClientDetailsData from a JSON string
client_details_data_instance = ClientDetailsData.from_json(json)
# print the JSON string representation of the object
print ClientDetailsData.to_json()

# convert the object into a dict
client_details_data_dict = client_details_data_instance.to_dict()
# create an instance of ClientDetailsData from a dict
client_details_data_form_dict = client_details_data.from_dict(client_details_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


