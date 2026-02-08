# SipOrderRecord


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sip_name** | **str** |  | [optional] 
**status** | **str** |  | [optional] 
**sip_type** | **str** |  | 
**modify_start_date** | **bool** | &#39;modifyStartDate&#39; flag will be false if modification of start date is disabled | [optional] 
**registered_date** | **str** |  | [optional] 
**start_date** | **str** |  | [optional] 
**due_date** | **str** |  | [optional] 
**last_executed_date** | **str** |  | [optional] 
**execution_date** | **str** |  | [optional] 
**sip_id** | **str** |  | [optional] 
**pending_period** | **float** | End period | [optional] 
**period** | **float** |  | [optional] 
**executed_period** | **float** |  | [optional] 
**schedule_desc** | **str** |  | [optional] 
**symbols** | [**List[ScripInfo]**](ScripInfo.md) |  | [optional] 

## Example

```python
from openapi_client.models.sip_order_record import SipOrderRecord

# TODO update the JSON string below
json = "{}"
# create an instance of SipOrderRecord from a JSON string
sip_order_record_instance = SipOrderRecord.from_json(json)
# print the JSON string representation of the object
print SipOrderRecord.to_json()

# convert the object into a dict
sip_order_record_dict = sip_order_record_instance.to_dict()
# create an instance of SipOrderRecord from a dict
sip_order_record_form_dict = sip_order_record.from_dict(sip_order_record_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


