# StageMessage


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**msg** | **str** |  | [optional] 
**risk** | **str** | severity of surveillance stage measure | [optional] 

## Example

```python
from openapi_client.models.stage_message import StageMessage

# TODO update the JSON string below
json = "{}"
# create an instance of StageMessage from a JSON string
stage_message_instance = StageMessage.from_json(json)
# print the JSON string representation of the object
print StageMessage.to_json()

# convert the object into a dict
stage_message_dict = stage_message_instance.to_dict()
# create an instance of StageMessage from a dict
stage_message_form_dict = stage_message.from_dict(stage_message_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


