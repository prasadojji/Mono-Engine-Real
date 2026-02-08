# openapi_client.ChartDataApi

All URIs are relative to *https://api.tradejini.com/v2*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_interval_chart_data**](ChartDataApi.md#get_interval_chart_data) | **GET** /api/mkt-data/chart/interval-data | Interval Chart


# **get_interval_chart_data**
> GetIntervalChartData200Response get_interval_chart_data(var_from, to, interval, id)

Interval Chart

This service can be used to fetch the  open, high, low, close and volume values (chart data points) of a given symbol.</br>Also it provides sum up volume of last tick to calculate the current minute volume.</br>For derivative symbol, an additional field Open Interest Change for that particular minute will be added in same response array.

### Example

* Bearer (Token) Authentication (http_bearer):

```python
import time
import os
import openapi_client
from openapi_client.models.get_interval_chart_data200_response import GetIntervalChartData200Response
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
    api_instance = openapi_client.ChartDataApi(api_client)
    var_from = 1685591100 # int | Enter starting datetime(eg: 2023-06-01 9:15:00 ) in timestamp(eg: 1685591100)
    to = 1685605354 # int | Enter ending datetime(eg: 2023-06-01 13:12:34) in timestamp(eg: 1685605354)
    interval = 'interval_example' # str | Enter time interval in minutes
    id = 'EQT_RELIANCE_EQ_NSE' # str | Enter Symbol id

    try:
        # Interval Chart
        api_response = api_instance.get_interval_chart_data(var_from, to, interval, id)
        print("The response of ChartDataApi->get_interval_chart_data:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ChartDataApi->get_interval_chart_data: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **var_from** | **int**| Enter starting datetime(eg: 2023-06-01 9:15:00 ) in timestamp(eg: 1685591100) | 
 **to** | **int**| Enter ending datetime(eg: 2023-06-01 13:12:34) in timestamp(eg: 1685605354) | 
 **interval** | **str**| Enter time interval in minutes | 
 **id** | **str**| Enter Symbol id | 

### Return type

[**GetIntervalChartData200Response**](GetIntervalChartData200Response.md)

### Authorization

[http_bearer](../README.md#http_bearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | successful response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

