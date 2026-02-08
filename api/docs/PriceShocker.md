# PriceShocker


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**change_per** | **str** |  | [optional] 
**avg_price** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.price_shocker import PriceShocker

# TODO update the JSON string below
json = "{}"
# create an instance of PriceShocker from a JSON string
price_shocker_instance = PriceShocker.from_json(json)
# print the JSON string representation of the object
print PriceShocker.to_json()

# convert the object into a dict
price_shocker_dict = price_shocker_instance.to_dict()
# create an instance of PriceShocker from a dict
price_shocker_form_dict = price_shocker.from_dict(price_shocker_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


