# openapi_client.AccountApi

All URIs are relative to *https://api.tradejini.com/v2*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_logout_web_response**](AccountApi.md#get_logout_web_response) | **POST** /api/account/logout | Logout
[**get_user_details**](AccountApi.md#get_user_details) | **GET** /api/account/details | Details


# **get_logout_web_response**
> GetLogoutWebResponse200Response get_logout_web_response()

Logout

to logout the user and to clear all authorization tokens

### Example

* Bearer (Token) Authentication (http_bearer):

```python
import time
import os
import openapi_client
from openapi_client.models.get_logout_web_response200_response import GetLogoutWebResponse200Response
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.tradejini.com/v2
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.tradejini.com/v2"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (Token): http_bearer
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AccountApi(api_client)

    try:
        # Logout
        api_response = api_instance.get_logout_web_response()
        print("The response of AccountApi->get_logout_web_response:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccountApi->get_logout_web_response: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**GetLogoutWebResponse200Response**](GetLogoutWebResponse200Response.md)

### Authorization

[http_bearer](../README.md#http_bearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_user_details**
> GetUserDetails200Response get_user_details()

Details

to fetch the primary user details like name, allowed products and segments

### Example

* Bearer (Token) Authentication (http_bearer):

```python
import time
import os
import openapi_client
from openapi_client.models.get_user_details200_response import GetUserDetails200Response
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.tradejini.com/v2
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.tradejini.com/v2"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (Token): http_bearer
configuration = openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AccountApi(api_client)

    try:
        # Details
        api_response = api_instance.get_user_details()
        print("The response of AccountApi->get_user_details:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccountApi->get_user_details: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**GetUserDetails200Response**](GetUserDetails200Response.md)

### Authorization

[http_bearer](../README.md#http_bearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

