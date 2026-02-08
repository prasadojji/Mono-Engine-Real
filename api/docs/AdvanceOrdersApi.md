# openapi_client.AdvanceOrdersApi

All URIs are relative to *https://api.tradejini.com/v2*

Method | HTTP request | Description
------------- | ------------- | -------------
[**cancel_gtt_order**](AdvanceOrdersApi.md#cancel_gtt_order) | **DELETE** /api/oms/cancel-order/gtt | Cancel GTT Order
[**cancel_oco_order**](AdvanceOrdersApi.md#cancel_oco_order) | **DELETE** /api/oms/cancel-order/oco | Cancel OCO Order
[**exit_order**](AdvanceOrdersApi.md#exit_order) | **POST** /api/oms/exit-order | Exit Order
[**modify_bracket_order**](AdvanceOrdersApi.md#modify_bracket_order) | **PUT** /api/oms/modify-order/bo | Modify Bracket Order
[**modify_cover_order**](AdvanceOrdersApi.md#modify_cover_order) | **PUT** /api/oms/modify-order/co | Modify Cover Order
[**modify_gtt_order**](AdvanceOrdersApi.md#modify_gtt_order) | **PUT** /api/oms/modify-order/gtt | Modify GTT Order
[**modify_oco_order**](AdvanceOrdersApi.md#modify_oco_order) | **PUT** /api/oms/modify-order/oco | Modify OCO Order
[**pending_gtt_orders**](AdvanceOrdersApi.md#pending_gtt_orders) | **GET** /api/oms/orders/gtt | GTT OrderBook
[**place_bracket_order**](AdvanceOrdersApi.md#place_bracket_order) | **POST** /api/oms/place-order/bo | Place Bracket Order
[**place_cover_order**](AdvanceOrdersApi.md#place_cover_order) | **POST** /api/oms/place-order/co | Place Cover Order
[**place_gtt_order**](AdvanceOrdersApi.md#place_gtt_order) | **POST** /api/oms/place-order/gtt | Place GTT Order
[**place_oco_order**](AdvanceOrdersApi.md#place_oco_order) | **POST** /api/oms/place-order/oco | Place OCO Order


# **cancel_gtt_order**
> CancelGTTOrder200Response cancel_gtt_order(order_no)

Cancel GTT Order

to cancel the GTT order

### Example

* Bearer (Token) Authentication (http_bearer):

```python
import time
import os
import openapi_client
from openapi_client.models.cancel_gtt_order200_response import CancelGTTOrder200Response
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
    api_instance = openapi_client.AdvanceOrdersApi(api_client)
    order_no = 'order_no_example' # str | Order Number is unique number which will be utilized while modifying and cancelling order

    try:
        # Cancel GTT Order
        api_response = api_instance.cancel_gtt_order(order_no)
        print("The response of AdvanceOrdersApi->cancel_gtt_order:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdvanceOrdersApi->cancel_gtt_order: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **order_no** | **str**| Order Number is unique number which will be utilized while modifying and cancelling order | 

### Return type

[**CancelGTTOrder200Response**](CancelGTTOrder200Response.md)

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

# **cancel_oco_order**
> CancelOCOOrder200Response cancel_oco_order(order_no)

Cancel OCO Order

Cancel A one-cancels-the-other order

### Example

* Bearer (Token) Authentication (http_bearer):

```python
import time
import os
import openapi_client
from openapi_client.models.cancel_oco_order200_response import CancelOCOOrder200Response
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
    api_instance = openapi_client.AdvanceOrdersApi(api_client)
    order_no = 'order_no_example' # str | Order Number is unique number which will be utilized while modifying and cancelling order

    try:
        # Cancel OCO Order
        api_response = api_instance.cancel_oco_order(order_no)
        print("The response of AdvanceOrdersApi->cancel_oco_order:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdvanceOrdersApi->cancel_oco_order: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **order_no** | **str**| Order Number is unique number which will be utilized while modifying and cancelling order | 

### Return type

[**CancelOCOOrder200Response**](CancelOCOOrder200Response.md)

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

# **exit_order**
> ExitOrder200Response exit_order(order_id, product)

Exit Order

to exit bracket or cover order.

### Example

* Bearer (Token) Authentication (http_bearer):

```python
import time
import os
import openapi_client
from openapi_client.models.exit_order200_response import ExitOrder200Response
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
    api_instance = openapi_client.AdvanceOrdersApi(api_client)
    order_id = 'order_id_example' # str | Main leg order id of bracker or cover order should be passed here. It will be received from the field 'mainLegOrderId' in orders response
    product = 'product_example' # str | Pass the respective product type bracket or cover here to exit

    try:
        # Exit Order
        api_response = api_instance.exit_order(order_id, product)
        print("The response of AdvanceOrdersApi->exit_order:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdvanceOrdersApi->exit_order: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **order_id** | **str**| Main leg order id of bracker or cover order should be passed here. It will be received from the field &#39;mainLegOrderId&#39; in orders response | 
 **product** | **str**| Pass the respective product type bracket or cover here to exit | 

### Return type

[**ExitOrder200Response**](ExitOrder200Response.md)

### Authorization

[http_bearer](../README.md#http_bearer)

### HTTP request headers

 - **Content-Type**: application/x-www-form-urlencoded
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **modify_bracket_order**
> ModifyOrder200Response modify_bracket_order(sym_id, order_id, qty, type, stop_trig_price, target_price, limit_price=limit_price, trig_price=trig_price, mkt_prot=mkt_prot, trailing_stop_price=trailing_stop_price, side=side)

Modify Bracket Order

to modify the bracket order

### Example

* Bearer (Token) Authentication (http_bearer):

```python
import time
import os
import openapi_client
from openapi_client.models.modify_order200_response import ModifyOrder200Response
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
    api_instance = openapi_client.AdvanceOrdersApi(api_client)
    sym_id = 'sym_id_example' # str | Unique identifier of the symbol
    order_id = 'order_id_example' # str | Order id of an order which needs modification. This id will be received in orders service
    qty = 3.4 # float | Total order quantity after the modification. ( Filled Qty (if nonzero) + (Modified Qty or Pending Qty)). Example: If the order quantity is 100, out of that 60 is already filled, and if we are modifying the pending qty from 40 to 70 then qty => (60 + 70) = 130 should be sent. 
    type = 'type_example' # str | Price type of an order
    stop_trig_price = 3.4 # float | Stop loss leg trigger price. This is the difference of main leg price and the stop loss leg trigger price. If your main leg order price is '2400' and if you want to set the stop loss trigger at '2300' then pass the difference '100' in this field. 
    target_price = 3.4 # float | Target leg price. This is the difference of main leg price and the target leg price. If your main leg order price is '2400' and if you want to set the target or profit order price for 2500 then pass the difference '100' in this field
    limit_price = 3.4 # float | Main leg order price. Required only for 'limit' and 'stoplimit' orders (optional)
    trig_price = 3.4 # float | This is applicable only for the main leg order and required only if the order type is 'stoplimit' (optional)
    mkt_prot = 3.4 # float | This is applicable only for the main leg order and required only if the order type is 'market' (optional)
    trailing_stop_price = 3.4 # float | Trailing stop loss price. (optional)
    side = 'side_example' # str | Order side 'buy' or 'sell' (optional)

    try:
        # Modify Bracket Order
        api_response = api_instance.modify_bracket_order(sym_id, order_id, qty, type, stop_trig_price, target_price, limit_price=limit_price, trig_price=trig_price, mkt_prot=mkt_prot, trailing_stop_price=trailing_stop_price, side=side)
        print("The response of AdvanceOrdersApi->modify_bracket_order:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdvanceOrdersApi->modify_bracket_order: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sym_id** | **str**| Unique identifier of the symbol | 
 **order_id** | **str**| Order id of an order which needs modification. This id will be received in orders service | 
 **qty** | **float**| Total order quantity after the modification. ( Filled Qty (if nonzero) + (Modified Qty or Pending Qty)). Example: If the order quantity is 100, out of that 60 is already filled, and if we are modifying the pending qty from 40 to 70 then qty &#x3D;&gt; (60 + 70) &#x3D; 130 should be sent.  | 
 **type** | **str**| Price type of an order | 
 **stop_trig_price** | **float**| Stop loss leg trigger price. This is the difference of main leg price and the stop loss leg trigger price. If your main leg order price is &#39;2400&#39; and if you want to set the stop loss trigger at &#39;2300&#39; then pass the difference &#39;100&#39; in this field.  | 
 **target_price** | **float**| Target leg price. This is the difference of main leg price and the target leg price. If your main leg order price is &#39;2400&#39; and if you want to set the target or profit order price for 2500 then pass the difference &#39;100&#39; in this field | 
 **limit_price** | **float**| Main leg order price. Required only for &#39;limit&#39; and &#39;stoplimit&#39; orders | [optional] 
 **trig_price** | **float**| This is applicable only for the main leg order and required only if the order type is &#39;stoplimit&#39; | [optional] 
 **mkt_prot** | **float**| This is applicable only for the main leg order and required only if the order type is &#39;market&#39; | [optional] 
 **trailing_stop_price** | **float**| Trailing stop loss price. | [optional] 
 **side** | **str**| Order side &#39;buy&#39; or &#39;sell&#39; | [optional] 

### Return type

[**ModifyOrder200Response**](ModifyOrder200Response.md)

### Authorization

[http_bearer](../README.md#http_bearer)

### HTTP request headers

 - **Content-Type**: application/x-www-form-urlencoded
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **modify_cover_order**
> ModifyOrder200Response modify_cover_order(sym_id, order_id, qty, type, stop_trig_price, limit_price=limit_price, trig_price=trig_price, mkt_prot=mkt_prot, side=side)

Modify Cover Order

to modify the cover order

### Example

* Bearer (Token) Authentication (http_bearer):

```python
import time
import os
import openapi_client
from openapi_client.models.modify_order200_response import ModifyOrder200Response
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
    api_instance = openapi_client.AdvanceOrdersApi(api_client)
    sym_id = 'sym_id_example' # str | Unique identifier of the symbol
    order_id = 'order_id_example' # str | Order id of an order which needs modification. This id will be received in orders service
    qty = 3.4 # float | Total order quantity after the modification. ( Filled Qty (if nonzero) + (Modified Qty or Pending Qty)). Example: If the order quantity is 100, out of that 60 is already filled, and if we are modifying the pending qty from 40 to 70 then qty => (60 + 70) = 130 should be sent. 
    type = 'type_example' # str | Price type of an order
    stop_trig_price = 3.4 # float | Stop loss leg trigger price. This is the difference of main leg price and the stop loss leg trigger price. If your main leg order price is '2400' and if you want to set the stop loss trigger at '2300' then pass the difference '100' in this field. 
    limit_price = 3.4 # float | Main leg order price. Required only for 'limit' and 'stoplimit' orders (optional)
    trig_price = 3.4 # float | This is applicable only for the main leg order and required only if the order type is 'stoplimit' (optional)
    mkt_prot = 3.4 # float | This is applicable only for the main leg order and required only if the order type is 'market' (optional)
    side = 'side_example' # str | Order side 'buy' or 'sell' (optional)

    try:
        # Modify Cover Order
        api_response = api_instance.modify_cover_order(sym_id, order_id, qty, type, stop_trig_price, limit_price=limit_price, trig_price=trig_price, mkt_prot=mkt_prot, side=side)
        print("The response of AdvanceOrdersApi->modify_cover_order:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdvanceOrdersApi->modify_cover_order: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sym_id** | **str**| Unique identifier of the symbol | 
 **order_id** | **str**| Order id of an order which needs modification. This id will be received in orders service | 
 **qty** | **float**| Total order quantity after the modification. ( Filled Qty (if nonzero) + (Modified Qty or Pending Qty)). Example: If the order quantity is 100, out of that 60 is already filled, and if we are modifying the pending qty from 40 to 70 then qty &#x3D;&gt; (60 + 70) &#x3D; 130 should be sent.  | 
 **type** | **str**| Price type of an order | 
 **stop_trig_price** | **float**| Stop loss leg trigger price. This is the difference of main leg price and the stop loss leg trigger price. If your main leg order price is &#39;2400&#39; and if you want to set the stop loss trigger at &#39;2300&#39; then pass the difference &#39;100&#39; in this field.  | 
 **limit_price** | **float**| Main leg order price. Required only for &#39;limit&#39; and &#39;stoplimit&#39; orders | [optional] 
 **trig_price** | **float**| This is applicable only for the main leg order and required only if the order type is &#39;stoplimit&#39; | [optional] 
 **mkt_prot** | **float**| This is applicable only for the main leg order and required only if the order type is &#39;market&#39; | [optional] 
 **side** | **str**| Order side &#39;buy&#39; or &#39;sell&#39; | [optional] 

### Return type

[**ModifyOrder200Response**](ModifyOrder200Response.md)

### Authorization

[http_bearer](../README.md#http_bearer)

### HTTP request headers

 - **Content-Type**: application/x-www-form-urlencoded
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **modify_gtt_order**
> ModifyGTTOrder200Response modify_gtt_order(order_id, sym_id, side, type, product, trig_price_per, trig_price, qty, limit_price=limit_price)

Modify GTT Order

Modify good till triggered order

### Example

* Bearer (Token) Authentication (http_bearer):

```python
import time
import os
import openapi_client
from openapi_client.models.modify_gtt_order200_response import ModifyGTTOrder200Response
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
    api_instance = openapi_client.AdvanceOrdersApi(api_client)
    order_id = 'order_id_example' # str | Order Number is unique number which will be utilized while modifying and cancelling order
    sym_id = 'sym_id_example' # str | Unique identifier of the symbol
    side = 'side_example' # str | Order id of an order. This will be received in orders response
    type = 'type_example' # str | Price type of an order
    product = 'product_example' # str | Product type of an order. 'delivery' is applicable for equities. 'normal' is applicable for derivatives. 'intraday' is applicable for both equity and derivatives
    trig_price_per = 3.4 # float | Price difference from the LTP in percentage, calculated using the formula: (trigPrice - LTP) / LTP × 100. This value can be positive or negative, depending on whether the trigPrice is above or below the LTP.
    trig_price = 3.4 # float | Trigger price with respect to LTP
    qty = 3.4 # float | No of shares to buy or sell. For derivatives, pass the quantity by multiplying with lot size. Example: To buy 1 lot of NIFTY option, pass the quantity as 50.
    limit_price = 3.4 # float | This is required only for limit and stop limit orders (optional)

    try:
        # Modify GTT Order
        api_response = api_instance.modify_gtt_order(order_id, sym_id, side, type, product, trig_price_per, trig_price, qty, limit_price=limit_price)
        print("The response of AdvanceOrdersApi->modify_gtt_order:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdvanceOrdersApi->modify_gtt_order: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **order_id** | **str**| Order Number is unique number which will be utilized while modifying and cancelling order | 
 **sym_id** | **str**| Unique identifier of the symbol | 
 **side** | **str**| Order id of an order. This will be received in orders response | 
 **type** | **str**| Price type of an order | 
 **product** | **str**| Product type of an order. &#39;delivery&#39; is applicable for equities. &#39;normal&#39; is applicable for derivatives. &#39;intraday&#39; is applicable for both equity and derivatives | 
 **trig_price_per** | **float**| Price difference from the LTP in percentage, calculated using the formula: (trigPrice - LTP) / LTP × 100. This value can be positive or negative, depending on whether the trigPrice is above or below the LTP. | 
 **trig_price** | **float**| Trigger price with respect to LTP | 
 **qty** | **float**| No of shares to buy or sell. For derivatives, pass the quantity by multiplying with lot size. Example: To buy 1 lot of NIFTY option, pass the quantity as 50. | 
 **limit_price** | **float**| This is required only for limit and stop limit orders | [optional] 

### Return type

[**ModifyGTTOrder200Response**](ModifyGTTOrder200Response.md)

### Authorization

[http_bearer](../README.md#http_bearer)

### HTTP request headers

 - **Content-Type**: application/x-www-form-urlencoded
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **modify_oco_order**
> ModifyOCOOrder200Response modify_oco_order(order_id, sym_id, side, stop_loss_type, stop_loss_product, stop_trig_price, stop_qty, target_type, target_product, target_trig_price, target_qty, stop_price=stop_price, target_price=target_price)

Modify OCO Order

Modify one-cancels-the-other order

### Example

* Bearer (Token) Authentication (http_bearer):

```python
import time
import os
import openapi_client
from openapi_client.models.modify_oco_order200_response import ModifyOCOOrder200Response
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
    api_instance = openapi_client.AdvanceOrdersApi(api_client)
    order_id = 'order_id_example' # str | Order Number is unique number which will be utilized while modifying and cancelling order
    sym_id = 'sym_id_example' # str | Unique identifier of the symbol
    side = 'side_example' # str | Order id of an order. This will be received in orders response
    stop_loss_type = 'stop_loss_type_example' # str | Price type of an order
    stop_loss_product = 'stop_loss_product_example' # str | Product type of an order. 'delivery' is applicable for equities. 'normal' is applicable for derivatives. 'intraday' is applicable for both equity and derivatives
    stop_trig_price = 3.4 # float | Stoploss trigger price
    stop_qty = 3.4 # float | No of shares to buy or sell. For derivatives, pass the quantity by multiplying with lot size. Example: To buy 1 lot of NIFTY option, pass the quantity as 50.
    target_type = 'target_type_example' # str | Price type of an order
    target_product = 'target_product_example' # str | Product type of an order. 'delivery' is applicable for equities. 'normal' is applicable for derivatives. 'intraday' is applicable for both equity and derivatives
    target_trig_price = 3.4 # float | Target trigger price
    target_qty = 3.4 # float | No of shares to buy or sell. For derivatives, pass the quantity by multiplying with lot size. Example: To buy 1 lot of NIFTY option, pass the quantity as 50.
    stop_price = 3.4 # float | This is required only for limit and stop limit orders (optional)
    target_price = 3.4 # float | This is required only for limit and stop limit orders (optional)

    try:
        # Modify OCO Order
        api_response = api_instance.modify_oco_order(order_id, sym_id, side, stop_loss_type, stop_loss_product, stop_trig_price, stop_qty, target_type, target_product, target_trig_price, target_qty, stop_price=stop_price, target_price=target_price)
        print("The response of AdvanceOrdersApi->modify_oco_order:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdvanceOrdersApi->modify_oco_order: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **order_id** | **str**| Order Number is unique number which will be utilized while modifying and cancelling order | 
 **sym_id** | **str**| Unique identifier of the symbol | 
 **side** | **str**| Order id of an order. This will be received in orders response | 
 **stop_loss_type** | **str**| Price type of an order | 
 **stop_loss_product** | **str**| Product type of an order. &#39;delivery&#39; is applicable for equities. &#39;normal&#39; is applicable for derivatives. &#39;intraday&#39; is applicable for both equity and derivatives | 
 **stop_trig_price** | **float**| Stoploss trigger price | 
 **stop_qty** | **float**| No of shares to buy or sell. For derivatives, pass the quantity by multiplying with lot size. Example: To buy 1 lot of NIFTY option, pass the quantity as 50. | 
 **target_type** | **str**| Price type of an order | 
 **target_product** | **str**| Product type of an order. &#39;delivery&#39; is applicable for equities. &#39;normal&#39; is applicable for derivatives. &#39;intraday&#39; is applicable for both equity and derivatives | 
 **target_trig_price** | **float**| Target trigger price | 
 **target_qty** | **float**| No of shares to buy or sell. For derivatives, pass the quantity by multiplying with lot size. Example: To buy 1 lot of NIFTY option, pass the quantity as 50. | 
 **stop_price** | **float**| This is required only for limit and stop limit orders | [optional] 
 **target_price** | **float**| This is required only for limit and stop limit orders | [optional] 

### Return type

[**ModifyOCOOrder200Response**](ModifyOCOOrder200Response.md)

### Authorization

[http_bearer](../README.md#http_bearer)

### HTTP request headers

 - **Content-Type**: application/x-www-form-urlencoded
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **pending_gtt_orders**
> PendingGTTOrders200Response pending_gtt_orders()

GTT OrderBook

to get the list of pending gtt, oco orders orders

### Example

* Bearer (Token) Authentication (http_bearer):

```python
import time
import os
import openapi_client
from openapi_client.models.pending_gtt_orders200_response import PendingGTTOrders200Response
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
    api_instance = openapi_client.AdvanceOrdersApi(api_client)

    try:
        # GTT OrderBook
        api_response = api_instance.pending_gtt_orders()
        print("The response of AdvanceOrdersApi->pending_gtt_orders:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdvanceOrdersApi->pending_gtt_orders: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**PendingGTTOrders200Response**](PendingGTTOrders200Response.md)

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

# **place_bracket_order**
> PlaceBracketOrder200Response place_bracket_order(sym_id, qty, side, type, stop_trig_price, target_price, limit_price=limit_price, trig_price=trig_price, mkt_prot=mkt_prot, trailing_stop_price=trailing_stop_price, remarks=remarks)

Place Bracket Order

to place the bracket order

### Example

* Bearer (Token) Authentication (http_bearer):

```python
import time
import os
import openapi_client
from openapi_client.models.place_bracket_order200_response import PlaceBracketOrder200Response
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
    api_instance = openapi_client.AdvanceOrdersApi(api_client)
    sym_id = 'sym_id_example' # str | Unique identifier of the symbol
    qty = 3.4 # float | No of shares to buy or sell. For derivatives, pass the quantity by multiplying with lot size. Example: To buy 1 lot of NIFTY option, pass the quantity as 50.
    side = 'side_example' # str | Order side 'buy' or 'sell'
    type = 'type_example' # str | Price type of an order
    stop_trig_price = 3.4 # float | Stop loss leg trigger price. This is the difference of main leg price and the stop loss leg trigger price. If your main leg order price is '2400' and if you want to set the stop loss trigger at '2300' then pass the difference '100' in this field. 
    target_price = 3.4 # float | Target leg price. This is the difference of main leg price and the target leg price. If your main leg order price is '2400' and if you want to set the target or profit order price for 2500 then pass the difference '100' in this field
    limit_price = 3.4 # float | Main leg order price. Required only for 'limit' and 'stoplimit' orders (optional)
    trig_price = 3.4 # float | This is applicable only for the main leg order and required only if the order type is 'stoplimit' (optional)
    mkt_prot = 3.4 # float | This is applicable only for the main leg order and required only if the order type is 'market' (optional)
    trailing_stop_price = 3.4 # float | Trailing stop loss price. (optional)
    remarks = 'remarks_example' # str | Any tag or message to track in orderbook.Allowed length upto 10 Characters. Please note remarks more than 10 characters will be stripped out. (optional)

    try:
        # Place Bracket Order
        api_response = api_instance.place_bracket_order(sym_id, qty, side, type, stop_trig_price, target_price, limit_price=limit_price, trig_price=trig_price, mkt_prot=mkt_prot, trailing_stop_price=trailing_stop_price, remarks=remarks)
        print("The response of AdvanceOrdersApi->place_bracket_order:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdvanceOrdersApi->place_bracket_order: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sym_id** | **str**| Unique identifier of the symbol | 
 **qty** | **float**| No of shares to buy or sell. For derivatives, pass the quantity by multiplying with lot size. Example: To buy 1 lot of NIFTY option, pass the quantity as 50. | 
 **side** | **str**| Order side &#39;buy&#39; or &#39;sell&#39; | 
 **type** | **str**| Price type of an order | 
 **stop_trig_price** | **float**| Stop loss leg trigger price. This is the difference of main leg price and the stop loss leg trigger price. If your main leg order price is &#39;2400&#39; and if you want to set the stop loss trigger at &#39;2300&#39; then pass the difference &#39;100&#39; in this field.  | 
 **target_price** | **float**| Target leg price. This is the difference of main leg price and the target leg price. If your main leg order price is &#39;2400&#39; and if you want to set the target or profit order price for 2500 then pass the difference &#39;100&#39; in this field | 
 **limit_price** | **float**| Main leg order price. Required only for &#39;limit&#39; and &#39;stoplimit&#39; orders | [optional] 
 **trig_price** | **float**| This is applicable only for the main leg order and required only if the order type is &#39;stoplimit&#39; | [optional] 
 **mkt_prot** | **float**| This is applicable only for the main leg order and required only if the order type is &#39;market&#39; | [optional] 
 **trailing_stop_price** | **float**| Trailing stop loss price. | [optional] 
 **remarks** | **str**| Any tag or message to track in orderbook.Allowed length upto 10 Characters. Please note remarks more than 10 characters will be stripped out. | [optional] 

### Return type

[**PlaceBracketOrder200Response**](PlaceBracketOrder200Response.md)

### Authorization

[http_bearer](../README.md#http_bearer)

### HTTP request headers

 - **Content-Type**: application/x-www-form-urlencoded
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **place_cover_order**
> PlaceBracketOrder200Response place_cover_order(sym_id, qty, side, type, stop_trig_price, limit_price=limit_price, trig_price=trig_price, mkt_prot=mkt_prot, remarks=remarks)

Place Cover Order

to place the cover order

### Example

* Bearer (Token) Authentication (http_bearer):

```python
import time
import os
import openapi_client
from openapi_client.models.place_bracket_order200_response import PlaceBracketOrder200Response
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
    api_instance = openapi_client.AdvanceOrdersApi(api_client)
    sym_id = 'sym_id_example' # str | Unique identifier of the symbol
    qty = 3.4 # float | No of shares to buy or sell. For derivatives, pass the quantity by multiplying with lot size. Example: To buy 1 lot of NIFTY option, pass the quantity as 50.
    side = 'side_example' # str | Order side 'buy' or 'sell'
    type = 'type_example' # str | Price type of an order
    stop_trig_price = 3.4 # float | Stop loss leg trigger price. This is the difference of main leg price and the stop loss leg trigger price. If your main leg order price is '2400' and if you want to set the stop loss trigger at '2300' then pass the difference '100' in this field. 
    limit_price = 3.4 # float | Main leg order price. Required only for 'limit' and 'stoplimit' orders (optional)
    trig_price = 3.4 # float | This is applicable only for the main leg order and required only if the order type is 'stoplimit' (optional)
    mkt_prot = 3.4 # float | This is applicable only for the main leg order and required only if the order type is 'market' (optional)
    remarks = 'remarks_example' # str | Any tag or message to track in orderbook.Allowed length upto 10 Characters. Please note remarks more than 10 characters will be stripped out. (optional)

    try:
        # Place Cover Order
        api_response = api_instance.place_cover_order(sym_id, qty, side, type, stop_trig_price, limit_price=limit_price, trig_price=trig_price, mkt_prot=mkt_prot, remarks=remarks)
        print("The response of AdvanceOrdersApi->place_cover_order:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdvanceOrdersApi->place_cover_order: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sym_id** | **str**| Unique identifier of the symbol | 
 **qty** | **float**| No of shares to buy or sell. For derivatives, pass the quantity by multiplying with lot size. Example: To buy 1 lot of NIFTY option, pass the quantity as 50. | 
 **side** | **str**| Order side &#39;buy&#39; or &#39;sell&#39; | 
 **type** | **str**| Price type of an order | 
 **stop_trig_price** | **float**| Stop loss leg trigger price. This is the difference of main leg price and the stop loss leg trigger price. If your main leg order price is &#39;2400&#39; and if you want to set the stop loss trigger at &#39;2300&#39; then pass the difference &#39;100&#39; in this field.  | 
 **limit_price** | **float**| Main leg order price. Required only for &#39;limit&#39; and &#39;stoplimit&#39; orders | [optional] 
 **trig_price** | **float**| This is applicable only for the main leg order and required only if the order type is &#39;stoplimit&#39; | [optional] 
 **mkt_prot** | **float**| This is applicable only for the main leg order and required only if the order type is &#39;market&#39; | [optional] 
 **remarks** | **str**| Any tag or message to track in orderbook.Allowed length upto 10 Characters. Please note remarks more than 10 characters will be stripped out. | [optional] 

### Return type

[**PlaceBracketOrder200Response**](PlaceBracketOrder200Response.md)

### Authorization

[http_bearer](../README.md#http_bearer)

### HTTP request headers

 - **Content-Type**: application/x-www-form-urlencoded
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **place_gtt_order**
> PlaceGTTOrder200Response place_gtt_order(sym_id, type, side, product, trig_price_per, trig_price, qty, limit_price=limit_price)

Place GTT Order

Place good till triggered order

### Example

* Bearer (Token) Authentication (http_bearer):

```python
import time
import os
import openapi_client
from openapi_client.models.place_gtt_order200_response import PlaceGTTOrder200Response
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
    api_instance = openapi_client.AdvanceOrdersApi(api_client)
    sym_id = 'sym_id_example' # str | Unique identifier of the symbol
    type = 'type_example' # str | Price type of an order
    side = 'side_example' # str | Order id of an order. This will be received in orders response
    product = 'product_example' # str | Product type of an order. 'delivery' is applicable for equities. 'normal' is applicable for derivatives. 'intraday' is applicable for both equity and derivatives
    trig_price_per = 3.4 # float | Price difference from the LTP in percentage, calculated using the formula: (trigPrice - LTP) / LTP × 100. This value can be positive or negative, depending on whether the trigPrice is above or below the LTP.
    trig_price = 3.4 # float | Trigger price with respect to LTP
    qty = 3.4 # float | No of shares to buy or sell. For derivatives, pass the quantity by multiplying with lot size. Example: To buy 1 lot of NIFTY option, pass the quantity as 50.
    limit_price = 3.4 # float | This is required only for limit and stop limit orders (optional)

    try:
        # Place GTT Order
        api_response = api_instance.place_gtt_order(sym_id, type, side, product, trig_price_per, trig_price, qty, limit_price=limit_price)
        print("The response of AdvanceOrdersApi->place_gtt_order:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdvanceOrdersApi->place_gtt_order: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sym_id** | **str**| Unique identifier of the symbol | 
 **type** | **str**| Price type of an order | 
 **side** | **str**| Order id of an order. This will be received in orders response | 
 **product** | **str**| Product type of an order. &#39;delivery&#39; is applicable for equities. &#39;normal&#39; is applicable for derivatives. &#39;intraday&#39; is applicable for both equity and derivatives | 
 **trig_price_per** | **float**| Price difference from the LTP in percentage, calculated using the formula: (trigPrice - LTP) / LTP × 100. This value can be positive or negative, depending on whether the trigPrice is above or below the LTP. | 
 **trig_price** | **float**| Trigger price with respect to LTP | 
 **qty** | **float**| No of shares to buy or sell. For derivatives, pass the quantity by multiplying with lot size. Example: To buy 1 lot of NIFTY option, pass the quantity as 50. | 
 **limit_price** | **float**| This is required only for limit and stop limit orders | [optional] 

### Return type

[**PlaceGTTOrder200Response**](PlaceGTTOrder200Response.md)

### Authorization

[http_bearer](../README.md#http_bearer)

### HTTP request headers

 - **Content-Type**: application/x-www-form-urlencoded
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **place_oco_order**
> PlaceOCOOrder200Response place_oco_order(sym_id, side, stop_loss_type, stop_loss_product, stop_trig_price, stop_qty, target_type, target_product, target_trig_price, target_qty, stop_price=stop_price, target_price=target_price)

Place OCO Order

Place A one-cancels-the-other order

### Example

* Bearer (Token) Authentication (http_bearer):

```python
import time
import os
import openapi_client
from openapi_client.models.place_oco_order200_response import PlaceOCOOrder200Response
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
    api_instance = openapi_client.AdvanceOrdersApi(api_client)
    sym_id = 'sym_id_example' # str | Unique identifier of the symbol
    side = 'side_example' # str | Order id of an order. This will be received in orders response
    stop_loss_type = 'stop_loss_type_example' # str | Price type of an order
    stop_loss_product = 'stop_loss_product_example' # str | Product type of an order. 'delivery' is applicable for equities. 'normal' is applicable for derivatives. 'intraday' is applicable for both equity and derivatives
    stop_trig_price = 3.4 # float | Trigger price with respect to LTP
    stop_qty = 3.4 # float | No of shares to buy or sell. For derivatives, pass the quantity by multiplying with lot size. Example: To buy 1 lot of NIFTY option, pass the quantity as 50.
    target_type = 'target_type_example' # str | Price type of an order
    target_product = 'target_product_example' # str | Product type of an order. 'delivery' is applicable for equities. 'normal' is applicable for derivatives. 'intraday' is applicable for both equity and derivatives
    target_trig_price = 3.4 # float | Trigger price with respect to LTP
    target_qty = 3.4 # float | No of shares to buy or sell. For derivatives, pass the quantity by multiplying with lot size. Example: To buy 1 lot of NIFTY option, pass the quantity as 50.
    stop_price = 3.4 # float | This is required only for limit and stop limit orders (optional)
    target_price = 3.4 # float | This is required only for limit and stop limit orders (optional)

    try:
        # Place OCO Order
        api_response = api_instance.place_oco_order(sym_id, side, stop_loss_type, stop_loss_product, stop_trig_price, stop_qty, target_type, target_product, target_trig_price, target_qty, stop_price=stop_price, target_price=target_price)
        print("The response of AdvanceOrdersApi->place_oco_order:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdvanceOrdersApi->place_oco_order: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sym_id** | **str**| Unique identifier of the symbol | 
 **side** | **str**| Order id of an order. This will be received in orders response | 
 **stop_loss_type** | **str**| Price type of an order | 
 **stop_loss_product** | **str**| Product type of an order. &#39;delivery&#39; is applicable for equities. &#39;normal&#39; is applicable for derivatives. &#39;intraday&#39; is applicable for both equity and derivatives | 
 **stop_trig_price** | **float**| Trigger price with respect to LTP | 
 **stop_qty** | **float**| No of shares to buy or sell. For derivatives, pass the quantity by multiplying with lot size. Example: To buy 1 lot of NIFTY option, pass the quantity as 50. | 
 **target_type** | **str**| Price type of an order | 
 **target_product** | **str**| Product type of an order. &#39;delivery&#39; is applicable for equities. &#39;normal&#39; is applicable for derivatives. &#39;intraday&#39; is applicable for both equity and derivatives | 
 **target_trig_price** | **float**| Trigger price with respect to LTP | 
 **target_qty** | **float**| No of shares to buy or sell. For derivatives, pass the quantity by multiplying with lot size. Example: To buy 1 lot of NIFTY option, pass the quantity as 50. | 
 **stop_price** | **float**| This is required only for limit and stop limit orders | [optional] 
 **target_price** | **float**| This is required only for limit and stop limit orders | [optional] 

### Return type

[**PlaceOCOOrder200Response**](PlaceOCOOrder200Response.md)

### Authorization

[http_bearer](../README.md#http_bearer)

### HTTP request headers

 - **Content-Type**: application/x-www-form-urlencoded
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

