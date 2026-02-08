# openapi_client.AuthorizationApi

All URIs are relative to *https://api.tradejini.com/v2*

Method | HTTP request | Description
------------- | ------------- | -------------
[**authorize**](AuthorizationApi.md#authorize) | **GET** /api-gw/oauth/authorize | Authorize
[**get_access_token**](AuthorizationApi.md#get_access_token) | **POST** /api-gw/oauth/token | Access token
[**order_authorize**](AuthorizationApi.md#order_authorize) | **GET** /api-gw/oauth/order-connect | Order Connect [Offsite Orders]
[**updated_individual_token**](AuthorizationApi.md#updated_individual_token) | **POST** /api-gw/oauth/individual-token-v2 | Individual Token service


# **authorize**
> authorize(client_id, redirect_uri, response_type, scope, state)

Authorize

Authorize to get oAuth code. </br><span style='color:red'>This API cannot be test from this API document since it is been redirected.</span>

### Example


```python
import time
import os
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.tradejini.com/v2
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.tradejini.com/v2"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AuthorizationApi(api_client)
    client_id = 'client_id_example' # str | This field value should be the API key mentioned in the registered app. If the value is improper authorization will not be allowed.
    redirect_uri = 'redirect_uri_example' # str | This field value should be the redirect url mentioned in the registered app. If the value is improper authorization will not be allowed.
    response_type = 'response_type_example' # str | As per oAuth specification this value should be __\"code\"__
    scope = 'scope_example' # str | This field value should be __\"general\"__.
    state = 'state_example' # str | A literal string that will be return in the final redirection callback.

    try:
        # Authorize
        api_instance.authorize(client_id, redirect_uri, response_type, scope, state)
    except Exception as e:
        print("Exception when calling AuthorizationApi->authorize: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **client_id** | **str**| This field value should be the API key mentioned in the registered app. If the value is improper authorization will not be allowed. | 
 **redirect_uri** | **str**| This field value should be the redirect url mentioned in the registered app. If the value is improper authorization will not be allowed. | 
 **response_type** | **str**| As per oAuth specification this value should be __\&quot;code\&quot;__ | 
 **scope** | **str**| This field value should be __\&quot;general\&quot;__. | 
 **state** | **str**| A literal string that will be return in the final redirection callback. | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**302** | Redirect to login page or redirect url with code. |  -  |
**400** | Bad inputs |  -  |
**401** | Unauthorized request |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_access_token**
> AccessToken get_access_token(code, client_id, redirect_uri, client_secret, grant_type)

Access token

This service is used to get access token from the code which is received from final redirection call back.

### Example


```python
import time
import os
import openapi_client
from openapi_client.models.access_token import AccessToken
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.tradejini.com/v2
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.tradejini.com/v2"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AuthorizationApi(api_client)
    code = 'code_example' # str | This field value will be same as code received in the final redirection callback.
    client_id = 'client_id_example' # str | This field value should be the API key mentioned in the registered app. If the value is improper access token will not be generated.
    redirect_uri = 'redirect_uri_example' # str | This field value should be the redirect url mentioned in the registered app. If the value is improper access token will not be generated.
    client_secret = 'client_secret_example' # str | This field value should be the API secret provided at the app registration. If the value is improper access token will not be generated.
    grant_type = 'grant_type_example' # str | As per oAuth specification this value should be __\\\"authorization_code\\\"__

    try:
        # Access token
        api_response = api_instance.get_access_token(code, client_id, redirect_uri, client_secret, grant_type)
        print("The response of AuthorizationApi->get_access_token:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthorizationApi->get_access_token: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **code** | **str**| This field value will be same as code received in the final redirection callback. | 
 **client_id** | **str**| This field value should be the API key mentioned in the registered app. If the value is improper access token will not be generated. | 
 **redirect_uri** | **str**| This field value should be the redirect url mentioned in the registered app. If the value is improper access token will not be generated. | 
 **client_secret** | **str**| This field value should be the API secret provided at the app registration. If the value is improper access token will not be generated. | 
 **grant_type** | **str**| As per oAuth specification this value should be __\\\&quot;authorization_code\\\&quot;__ | 

### Return type

[**AccessToken**](AccessToken.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/x-www-form-urlencoded
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **order_authorize**
> order_authorize(client_id, redirect_uri, response_type, scope, state, params)

Order Connect [Offsite Orders]

Authorize to place orders and get oAuth Code to the redirect url at once.</br><span style='color:red'>This API cannot be test from this API document since it is been redirected.</span>

### Example


```python
import time
import os
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.tradejini.com/v2
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.tradejini.com/v2"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AuthorizationApi(api_client)
    client_id = 'client_id_example' # str | This field value should be the API key mentioned in the registered app. If the value is improper authorization will not be allowed.
    redirect_uri = 'redirect_uri_example' # str | This field value should be the redirect url mentioned in the registered app. If the value is improper authorization will not be allowed.
    response_type = 'response_type_example' # str | As per oAuth specification this value should be __\"code\"__
    scope = 'scope_example' # str | This field value should be __\"general\"__.
    state = 'state_example' # str | A literal string that will be return in the final redirection callback.
    params = 'params_example' # str | This field value should be the params required to place orders in json array format and get oAuth Code. </br><span style='color:red'>Each array value should match any of examples provided. Else your authorization will be failed.</span></br> Example :```[{\"exch\":\"NSE\",\"symbol\":\"ACC\",\"series\":\"EQ\",\"inst\":\"EQT\",\"qty\":10,\"side\":\"buy\",\"type\":\"limit\",\"product\":\"intraday\",\"limitPrice\":2700.55,\"validity\":\"day\"},{\"exch\":\"NFO\",\"symbol\":\"NIFTY\",\"expiry\":\"2022-11-24\",\"inst\":\"FUTIDX\",\"qty\":2000,\"side\":\"sell\",\"type\":\"market\",\"product\":\"intraday\",\"limitPrice\":0,\"validity\":\"ioc\",\"discQty\":500},{\"exch\":\"NFO\",\"symbol\":\"BANKNIFTY\",\"expiry\":\"2022-11-24\",\"optType\":\"PE\",\"inst\":\"OPTIDX\",\"strike\":\"34000\",\"qty\":1500,\"side\":\"buy\",\"type\":\"market\",\"product\":\"delivery\",\"limitPrice\":0,\"validity\":\"day\",\"mktProt\":5}]```</br> For equity symbol instrument must be \"EQT\"

    try:
        # Order Connect [Offsite Orders]
        api_instance.order_authorize(client_id, redirect_uri, response_type, scope, state, params)
    except Exception as e:
        print("Exception when calling AuthorizationApi->order_authorize: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **client_id** | **str**| This field value should be the API key mentioned in the registered app. If the value is improper authorization will not be allowed. | 
 **redirect_uri** | **str**| This field value should be the redirect url mentioned in the registered app. If the value is improper authorization will not be allowed. | 
 **response_type** | **str**| As per oAuth specification this value should be __\&quot;code\&quot;__ | 
 **scope** | **str**| This field value should be __\&quot;general\&quot;__. | 
 **state** | **str**| A literal string that will be return in the final redirection callback. | 
 **params** | **str**| This field value should be the params required to place orders in json array format and get oAuth Code. &lt;/br&gt;&lt;span style&#x3D;&#39;color:red&#39;&gt;Each array value should match any of examples provided. Else your authorization will be failed.&lt;/span&gt;&lt;/br&gt; Example :&#x60;&#x60;&#x60;[{\&quot;exch\&quot;:\&quot;NSE\&quot;,\&quot;symbol\&quot;:\&quot;ACC\&quot;,\&quot;series\&quot;:\&quot;EQ\&quot;,\&quot;inst\&quot;:\&quot;EQT\&quot;,\&quot;qty\&quot;:10,\&quot;side\&quot;:\&quot;buy\&quot;,\&quot;type\&quot;:\&quot;limit\&quot;,\&quot;product\&quot;:\&quot;intraday\&quot;,\&quot;limitPrice\&quot;:2700.55,\&quot;validity\&quot;:\&quot;day\&quot;},{\&quot;exch\&quot;:\&quot;NFO\&quot;,\&quot;symbol\&quot;:\&quot;NIFTY\&quot;,\&quot;expiry\&quot;:\&quot;2022-11-24\&quot;,\&quot;inst\&quot;:\&quot;FUTIDX\&quot;,\&quot;qty\&quot;:2000,\&quot;side\&quot;:\&quot;sell\&quot;,\&quot;type\&quot;:\&quot;market\&quot;,\&quot;product\&quot;:\&quot;intraday\&quot;,\&quot;limitPrice\&quot;:0,\&quot;validity\&quot;:\&quot;ioc\&quot;,\&quot;discQty\&quot;:500},{\&quot;exch\&quot;:\&quot;NFO\&quot;,\&quot;symbol\&quot;:\&quot;BANKNIFTY\&quot;,\&quot;expiry\&quot;:\&quot;2022-11-24\&quot;,\&quot;optType\&quot;:\&quot;PE\&quot;,\&quot;inst\&quot;:\&quot;OPTIDX\&quot;,\&quot;strike\&quot;:\&quot;34000\&quot;,\&quot;qty\&quot;:1500,\&quot;side\&quot;:\&quot;buy\&quot;,\&quot;type\&quot;:\&quot;market\&quot;,\&quot;product\&quot;:\&quot;delivery\&quot;,\&quot;limitPrice\&quot;:0,\&quot;validity\&quot;:\&quot;day\&quot;,\&quot;mktProt\&quot;:5}]&#x60;&#x60;&#x60;&lt;/br&gt; For equity symbol instrument must be \&quot;EQT\&quot; | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**302** | Redirect to login page or redirect url with code. |  -  |
**400** | Bad order params |  -  |
**401** | Unauthorized request |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updated_individual_token**
> AccessToken updated_individual_token(authorization, password, two_fa, two_fa_typ)

Individual Token service

This service is an updated version with 2Fa login flow.</br>This service is used to get access token for the individual app registration in the developer portal.</br>Using this api direct login is possible from any programming language

### Example


```python
import time
import os
import openapi_client
from openapi_client.models.access_token import AccessToken
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.tradejini.com/v2
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.tradejini.com/v2"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AuthorizationApi(api_client)
    authorization = 'authorization_example' # str | The value should be in the following format :</br>Bearer clientID</br>*ClientID refers to API key in developer portal.
    password = 'password_example' # str | 
    two_fa = 'two_fa_example' # str | **DOB or PAN will not be accepted as 2FA from 30th September 2022 as per exchange regulations. OTP or Time based OTP should be passed for this field. To get the OTP for your client code, login into the web app <a href='https://cubeplus.tradejini.com/' target='_blank' >link</a> and in the 2FA page, click 'Having trouble with AppCode/TOTP' to see 'Send SMS / Email OTP' option to generate OTP.**  **For Time based OTP, login into this <a href='https://cubeplus.tradejini.com/' target='_blank' >link</a> and set up the Authenticator app to generate time based OTP by scanning the QR code provided under the Settings section.**
    two_fa_typ = 'two_fa_typ_example' # str | **Enter the type of twoFa based on your twoFa field input.**

    try:
        # Individual Token service
        api_response = api_instance.updated_individual_token(authorization, password, two_fa, two_fa_typ)
        print("The response of AuthorizationApi->updated_individual_token:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthorizationApi->updated_individual_token: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **str**| The value should be in the following format :&lt;/br&gt;Bearer clientID&lt;/br&gt;*ClientID refers to API key in developer portal. | 
 **password** | **str**|  | 
 **two_fa** | **str**| **DOB or PAN will not be accepted as 2FA from 30th September 2022 as per exchange regulations. OTP or Time based OTP should be passed for this field. To get the OTP for your client code, login into the web app &lt;a href&#x3D;&#39;https://cubeplus.tradejini.com/&#39; target&#x3D;&#39;_blank&#39; &gt;link&lt;/a&gt; and in the 2FA page, click &#39;Having trouble with AppCode/TOTP&#39; to see &#39;Send SMS / Email OTP&#39; option to generate OTP.**  **For Time based OTP, login into this &lt;a href&#x3D;&#39;https://cubeplus.tradejini.com/&#39; target&#x3D;&#39;_blank&#39; &gt;link&lt;/a&gt; and set up the Authenticator app to generate time based OTP by scanning the QR code provided under the Settings section.** | 
 **two_fa_typ** | **str**| **Enter the type of twoFa based on your twoFa field input.** | 

### Return type

[**AccessToken**](AccessToken.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/x-www-form-urlencoded
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Success response with access token |  -  |
**401** | Unauthorized request |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

