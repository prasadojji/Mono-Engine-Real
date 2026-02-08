# SecurityInfo


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**symbol** | **str** |  | [optional] 
**segment** | **str** |  | [optional] 
**expiry** | **str** |  | [optional] 
**instrument** | **str** |  | [optional] 
**tick_size** | **str** |  | [optional] 
**lot_size** | **str** |  | [optional] 
**multiplier** | **str** |  | [optional] 
**gn_gd_bypn_pd** | **str** |  | [optional] 
**price_unit** | **str** |  | [optional] 
**price_quote_qty** | **str** |  | [optional] 
**trade_unit** | **str** |  | [optional] 
**delivery_unit** | **str** |  | [optional] 
**freeze_qty** | **str** |  | [optional] 
**additional_long_mgn** | **str** |  | [optional] 
**additional_short_mgn** | **str** |  | [optional] 
**exercise_start_date** | **str** |  | [optional] 
**exercise_end_date** | **str** |  | [optional] 
**tender_start_date** | **str** |  | [optional] 
**tender_end_date** | **str** |  | [optional] 
**elm_buy_mgn** | **str** |  | [optional] 
**elm_start_mgn** | **str** |  | [optional] 
**special_long_mgn** | **str** |  | [optional] 
**special_short_mgn** | **str** |  | [optional] 
**contract_token** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.security_info import SecurityInfo

# TODO update the JSON string below
json = "{}"
# create an instance of SecurityInfo from a JSON string
security_info_instance = SecurityInfo.from_json(json)
# print the JSON string representation of the object
print SecurityInfo.to_json()

# convert the object into a dict
security_info_dict = security_info_instance.to_dict()
# create an instance of SecurityInfo from a dict
security_info_form_dict = security_info.from_dict(security_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


