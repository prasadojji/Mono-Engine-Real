# CancelOCOOrder200Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**s** | **str** |  | [optional] 
**d** | [**CancelOCOOrderData**](CancelOCOOrderData.md) |  | [optional] 
**msg** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.cancel_oco_order200_response import CancelOCOOrder200Response

# TODO update the JSON string below
json = "{}"
# create an instance of CancelOCOOrder200Response from a JSON string
cancel_oco_order200_response_instance = CancelOCOOrder200Response.from_json(json)
# print the JSON string representation of the object
print CancelOCOOrder200Response.to_json()

# convert the object into a dict
cancel_oco_order200_response_dict = cancel_oco_order200_response_instance.to_dict()
# create an instance of CancelOCOOrder200Response from a dict
cancel_oco_order200_response_form_dict = cancel_oco_order200_response.from_dict(cancel_oco_order200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


