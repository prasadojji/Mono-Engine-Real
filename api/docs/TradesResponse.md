# TradesResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**s** | **str** |  | [optional] 
**d** | [**List[TradeRecord]**](TradeRecord.md) |  | [optional] 

## Example

```python
from openapi_client.models.trades_response import TradesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of TradesResponse from a JSON string
trades_response_instance = TradesResponse.from_json(json)
# print the JSON string representation of the object
print TradesResponse.to_json()

# convert the object into a dict
trades_response_dict = trades_response_instance.to_dict()
# create an instance of TradesResponse from a dict
trades_response_form_dict = trades_response.from_dict(trades_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


