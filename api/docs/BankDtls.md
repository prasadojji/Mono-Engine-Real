# BankDtls


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**bank_name** | **str** |  | [optional] 
**acc_no** | **str** |  | [optional] 
**ifsc** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.bank_dtls import BankDtls

# TODO update the JSON string below
json = "{}"
# create an instance of BankDtls from a JSON string
bank_dtls_instance = BankDtls.from_json(json)
# print the JSON string representation of the object
print BankDtls.to_json()

# convert the object into a dict
bank_dtls_dict = bank_dtls_instance.to_dict()
# create an instance of BankDtls from a dict
bank_dtls_form_dict = bank_dtls.from_dict(bank_dtls_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


