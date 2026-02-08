# IouMessageResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**msg** | **str** |  | [optional] 
**s** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.iou_message_response import IouMessageResponse

# TODO update the JSON string below
json = "{}"
# create an instance of IouMessageResponse from a JSON string
iou_message_response_instance = IouMessageResponse.from_json(json)
# print the JSON string representation of the object
print IouMessageResponse.to_json()

# convert the object into a dict
iou_message_response_dict = iou_message_response_instance.to_dict()
# create an instance of IouMessageResponse from a dict
iou_message_response_form_dict = iou_message_response.from_dict(iou_message_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


