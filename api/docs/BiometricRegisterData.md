# BiometricRegisterData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**msg** | **str** |  | [optional] 
**biometric_id** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.biometric_register_data import BiometricRegisterData

# TODO update the JSON string below
json = "{}"
# create an instance of BiometricRegisterData from a JSON string
biometric_register_data_instance = BiometricRegisterData.from_json(json)
# print the JSON string representation of the object
print BiometricRegisterData.to_json()

# convert the object into a dict
biometric_register_data_dict = biometric_register_data_instance.to_dict()
# create an instance of BiometricRegisterData from a dict
biometric_register_data_form_dict = biometric_register_data.from_dict(biometric_register_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


