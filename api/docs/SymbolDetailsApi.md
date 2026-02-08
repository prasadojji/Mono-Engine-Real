# openapi_client.SymbolDetailsApi

All URIs are relative to *https://api.tradejini.com/v2*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_symbol_details**](SymbolDetailsApi.md#get_symbol_details) | **GET** /api/mkt-data/scrips/symbol-store/{scripGroup} | Scrip Master Data
[**version_details**](SymbolDetailsApi.md#version_details) | **GET** /api/mkt-data/scrips/symbol-store | Scrip Master Groups


# **get_symbol_details**
> str get_symbol_details(scrip_group)

Scrip Master Data

<ul><li>Get complete list of scrips based on the group passed in path.</li><li>This request accepts two types of response format : text/plain and application/json.</li><li><strong>text/plain</strong> : Normal plain string in csv format, rows separated with newline and columns separated with `,` (comma).</li><li><strong>application/json</strong>: List of scripts in a json array format. But usually slower than plain text format due to its larger size.</li></ul>

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
    api_instance = openapi_client.SymbolDetailsApi(api_client)
    scrip_group = 'scrip_group_example' # str | Enter symbol name to download

    try:
        # Scrip Master Data
        api_response = api_instance.get_symbol_details(scrip_group)
        print("The response of SymbolDetailsApi->get_symbol_details:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SymbolDetailsApi->get_symbol_details: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **scrip_group** | **str**| Enter symbol name to download | 

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **version_details**
> IouResponseScripVersionInfo version_details(version)

Scrip Master Groups

<ul><li>This service can be used to fetch the scrip groups. It requires version number as input. </li><li>Version number is maintained to avoid fetching scrip master data multiple times a day, as  the scrip master data gets updated only once in a day during BOD ( Beginning of Day) process.</li><li>For initial or first api call, version can be passed as 'zero'. If the version number which is been passed in the query param is not matched with the server data version, isUpdated flag will be true and scrip groups data will be received in the response. </li><li>If the version matches with the server data version, isUpdated flag will be false and scrips groups data array would be empty.</li><li>By using the names in scrip master groups response, user can call Scrip Master Data API to get scrip list.</li><li>For effective usage of ScripMaster, users can persist version number, ScripMaster groups and data locally.</li><strong>idFormat Usage :</strong></br><li>Each scrip group has different symbol-id format. This format is mentioned in the `idFormat` key.</br>Eg: For Equity, the id format is instrument_symbol_series_exchange. </li><li>The user can decompose the symbol-id format by splitting with `_` (underscore) delimiter for identifying attributes of a symbol if required.</br>Eg: If user want to know the instrument and exchange of a symbol from Securities group, the 1st and 4th words can be extracted from symbol-id.</li><li>Note: On BOD (Beginning of Day) process, symbol store will be updated and the version will be incremented in the api server.</li></ul>

### Example


```python
import time
import os
import openapi_client
from openapi_client.models.iou_response_scrip_version_info import IouResponseScripVersionInfo
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
    api_instance = openapi_client.SymbolDetailsApi(api_client)
    version = 56 # int | Enter the version

    try:
        # Scrip Master Groups
        api_response = api_instance.version_details(version)
        print("The response of SymbolDetailsApi->version_details:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SymbolDetailsApi->version_details: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **version** | **int**| Enter the version | 

### Return type

[**IouResponseScripVersionInfo**](IouResponseScripVersionInfo.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

