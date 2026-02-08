# BidDataList

List of BID data

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**no** | **int** |  | [optional] 
**price** | **int** |  | [optional] 
**qty** | **int** |  | [optional] 

## Example

```python
from openapi_client.models.bid_data_list import BidDataList

# TODO update the JSON string below
json = "{}"
# create an instance of BidDataList from a JSON string
bid_data_list_instance = BidDataList.from_json(json)
# print the JSON string representation of the object
print BidDataList.to_json()

# convert the object into a dict
bid_data_list_dict = bid_data_list_instance.to_dict()
# create an instance of BidDataList from a dict
bid_data_list_form_dict = bid_data_list.from_dict(bid_data_list_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


