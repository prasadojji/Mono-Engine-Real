# CancelGTTOrder200Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**s** | **str** |  | [optional] 
**d** | [**CancelGTTOrderData**](CancelGTTOrderData.md) |  | [optional] 
**msg** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.cancel_gtt_order200_response import CancelGTTOrder200Response

# TODO update the JSON string below
json = "{}"
# create an instance of CancelGTTOrder200Response from a JSON string
cancel_gtt_order200_response_instance = CancelGTTOrder200Response.from_json(json)
# print the JSON string representation of the object
print CancelGTTOrder200Response.to_json()

# convert the object into a dict
cancel_gtt_order200_response_dict = cancel_gtt_order200_response_instance.to_dict()
# create an instance of CancelGTTOrder200Response from a dict
cancel_gtt_order200_response_form_dict = cancel_gtt_order200_response.from_dict(cancel_gtt_order200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


