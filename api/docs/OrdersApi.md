# openapi_client.OrdersApi

All URIs are relative to *https://api.tradejini.com/v2*

Method | HTTP request | Description
------------- | ------------- | -------------
[**cancel_order**](OrdersApi.md#cancel_order) | **DELETE** /api/oms/cancel-order | Cancel Order
[**convert_position**](OrdersApi.md#convert_position) | **POST** /api/oms/convert-position | Convert Position 
[**get_basket_order_margin**](OrdersApi.md#get_basket_order_margin) | **POST** /api/oms/basket-margin | Basket Order Margin
[**get_holdings**](OrdersApi.md#get_holdings) | **GET** /api/oms/holdings | Holdings 
[**get_order_history**](OrdersApi.md#get_order_history) | **GET** /api/oms/history | History
[**get_order_margin**](OrdersApi.md#get_order_margin) | **POST** /api/oms/margin | Order Margin
[**get_orders**](OrdersApi.md#get_orders) | **GET** /api/oms/orders | Orders
[**get_positions**](OrdersApi.md#get_positions) | **GET** /api/oms/positions | Positions 
[**get_trades**](OrdersApi.md#get_trades) | **GET** /api/oms/trades | Trades
[**modify_order**](OrdersApi.md#modify_order) | **PUT** /api/oms/modify-order | Modify Order
[**place_order**](OrdersApi.md#place_order) | **POST** /api/oms/place-order | Place Order


# **cancel_order**
> CancelOrder200Response cancel_order(order_id)

Cancel Order

to cancel the pending order

### Example

* Bearer (Token) Authentication (http_bearer):

```python
import time
import os
import openapi_client
from openapi_client.models.cancel_order200_response import CancelOrder200Response
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
    api_instance = openapi_client.OrdersApi(api_client)
    order_id = 'order_id_example' # str | Order id of an order which needs to be cancelled. Order id is received from orders response

    try:
        # Cancel Order
        api_response = api_instance.cancel_order(order_id)
        print("The response of OrdersApi->cancel_order:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrdersApi->cancel_order: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **order_id** | **str**| Order id of an order which needs to be cancelled. Order id is received from orders response | 

### Return type

[**CancelOrder200Response**](CancelOrder200Response.md)

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

# **convert_position**
> ConvertPosition200Response convert_position(sym_id, qty, from_product, to_product, side)

Convert Position 

to convert a position from one product type to another

### Example

* Bearer (Token) Authentication (http_bearer):

```python
import time
import os
import openapi_client
from openapi_client.models.convert_position200_response import ConvertPosition200Response
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
    api_instance = openapi_client.OrdersApi(api_client)
    sym_id = 'sym_id_example' # str | Unique identifier of the symbol
    qty = 3.4 # float | No of shares to buy or sell. For derivatives, pass the quantity by multiplying with lot size. Example: To buy 1 lot of NIFTY option, pass the quantity as 50.
    from_product = 'from_product_example' # str | Current product type of a position record
    to_product = 'to_product_example' # str | Product to which the user wants to convert 
    side = 'side_example' # str | Order side 'buy' or 'sell'

    try:
        # Convert Position 
        api_response = api_instance.convert_position(sym_id, qty, from_product, to_product, side)
        print("The response of OrdersApi->convert_position:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrdersApi->convert_position: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sym_id** | **str**| Unique identifier of the symbol | 
 **qty** | **float**| No of shares to buy or sell. For derivatives, pass the quantity by multiplying with lot size. Example: To buy 1 lot of NIFTY option, pass the quantity as 50. | 
 **from_product** | **str**| Current product type of a position record | 
 **to_product** | **str**| Product to which the user wants to convert  | 
 **side** | **str**| Order side &#39;buy&#39; or &#39;sell&#39; | 

### Return type

[**ConvertPosition200Response**](ConvertPosition200Response.md)

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

# **get_basket_order_margin**
> GetBasketOrderMargin200Response get_basket_order_margin(basket_order_margin_request)

Basket Order Margin

Basket order margin

### Example

* Bearer (Token) Authentication (http_bearer):

```python
import time
import os
import openapi_client
from openapi_client.models.basket_order_margin_request import BasketOrderMarginRequest
from openapi_client.models.get_basket_order_margin200_response import GetBasketOrderMargin200Response
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
    api_instance = openapi_client.OrdersApi(api_client)
    basket_order_margin_request = openapi_client.BasketOrderMarginRequest() # BasketOrderMarginRequest | 

    try:
        # Basket Order Margin
        api_response = api_instance.get_basket_order_margin(basket_order_margin_request)
        print("The response of OrdersApi->get_basket_order_margin:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrdersApi->get_basket_order_margin: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **basket_order_margin_request** | [**BasketOrderMarginRequest**](BasketOrderMarginRequest.md)|  | 

### Return type

[**GetBasketOrderMargin200Response**](GetBasketOrderMargin200Response.md)

### Authorization

[http_bearer](../README.md#http_bearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_holdings**
> GetHoldings200Response get_holdings(sym_details=sym_details)

Holdings 

to get the list of holding records

### Example

* Bearer (Token) Authentication (http_bearer):

```python
import time
import os
import openapi_client
from openapi_client.models.get_holdings200_response import GetHoldings200Response
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
    api_instance = openapi_client.OrdersApi(api_client)
    sym_details = True # bool | Sending symDetails:'true' - will provide the symbol object in response for every record. Symbol object contains details such as price-tick, lotsize, token etc.., (optional)

    try:
        # Holdings 
        api_response = api_instance.get_holdings(sym_details=sym_details)
        print("The response of OrdersApi->get_holdings:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrdersApi->get_holdings: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sym_details** | **bool**| Sending symDetails:&#39;true&#39; - will provide the symbol object in response for every record. Symbol object contains details such as price-tick, lotsize, token etc.., | [optional] 

### Return type

[**GetHoldings200Response**](GetHoldings200Response.md)

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

# **get_order_history**
> GetOrderHistory200Response get_order_history(order_id)

History

to get an order history of an order

### Example

* Bearer (Token) Authentication (http_bearer):

```python
import time
import os
import openapi_client
from openapi_client.models.get_order_history200_response import GetOrderHistory200Response
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
    api_instance = openapi_client.OrdersApi(api_client)
    order_id = 'order_id_example' # str | Order id of an order. This will be received in orders response

    try:
        # History
        api_response = api_instance.get_order_history(order_id)
        print("The response of OrdersApi->get_order_history:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrdersApi->get_order_history: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **order_id** | **str**| Order id of an order. This will be received in orders response | 

### Return type

[**GetOrderHistory200Response**](GetOrderHistory200Response.md)

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

# **get_order_margin**
> GetOrderMargin200Response get_order_margin(sym_id, qty, side, type, product, limit_price=limit_price, trig_price=trig_price, stop_trig_price=stop_trig_price, org_qty=org_qty, org_limit_price=org_limit_price, org_trig_price=org_trig_price, org_stop_trig_price=org_stop_trig_price, fill_qty=fill_qty, order_id=order_id, main_leg_order_id=main_leg_order_id)

Order Margin

to get the margin required and available margin info while placing an order

### Example

* Bearer (Token) Authentication (http_bearer):

```python
import time
import os
import openapi_client
from openapi_client.models.get_order_margin200_response import GetOrderMargin200Response
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
    api_instance = openapi_client.OrdersApi(api_client)
    sym_id = 'sym_id_example' # str | Unique identifier of the symbol
    qty = 3.4 # float | 'qty' is number of shares for which required margin, for modification order 'qty' should be 'fillQty' + 'modified qty' 
    side = 'side_example' # str | Order side 'buy' or 'sell'
    type = 'type_example' # str | Price type of an order
    product = 'product_example' # str | Product type of an order. 'delivery' is applicable for equities. 'normal' is applicable for derivatives. 'intraday' is applicable for both equity and derivatives
    limit_price = 3.4 # float | This is required only for limit and stop limit orders (optional)
    trig_price = 3.4 # float | This is required only for stoploss limit and stoploss market orders (optional)
    stop_trig_price = 3.4 # float | Stop loss leg order trigger price. (optional)
    org_qty = 3.4 # float | Original quantity is applicable for modification order, original quantity is 'qty' from orderbook (optional)
    org_limit_price = 3.4 # float | Original limit price is applicable for modification order, original limit price is limit price from orderbook (optional)
    org_trig_price = 3.4 # float | Original trigger price is applicable for modification order, original trigger price is trigger price from orderbook (optional)
    org_stop_trig_price = 3.4 # float | Original stop loss price is applicable only for Cover and Bracket order modification, original stop loss price is stop loss price from orderbook. (optional)
    fill_qty = 3.4 # float | fillQty is partially filled quantity, fillQty is 'fillQty' from orderbook. (optional)
    order_id = 'order_id_example' # str | Order id is applicable for bracket and cover order modification  (optional)
    main_leg_order_id = 'main_leg_order_id_example' # str | Mainleg order id field is applicable for bracket and cover order (optional)

    try:
        # Order Margin
        api_response = api_instance.get_order_margin(sym_id, qty, side, type, product, limit_price=limit_price, trig_price=trig_price, stop_trig_price=stop_trig_price, org_qty=org_qty, org_limit_price=org_limit_price, org_trig_price=org_trig_price, org_stop_trig_price=org_stop_trig_price, fill_qty=fill_qty, order_id=order_id, main_leg_order_id=main_leg_order_id)
        print("The response of OrdersApi->get_order_margin:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrdersApi->get_order_margin: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sym_id** | **str**| Unique identifier of the symbol | 
 **qty** | **float**| &#39;qty&#39; is number of shares for which required margin, for modification order &#39;qty&#39; should be &#39;fillQty&#39; + &#39;modified qty&#39;  | 
 **side** | **str**| Order side &#39;buy&#39; or &#39;sell&#39; | 
 **type** | **str**| Price type of an order | 
 **product** | **str**| Product type of an order. &#39;delivery&#39; is applicable for equities. &#39;normal&#39; is applicable for derivatives. &#39;intraday&#39; is applicable for both equity and derivatives | 
 **limit_price** | **float**| This is required only for limit and stop limit orders | [optional] 
 **trig_price** | **float**| This is required only for stoploss limit and stoploss market orders | [optional] 
 **stop_trig_price** | **float**| Stop loss leg order trigger price. | [optional] 
 **org_qty** | **float**| Original quantity is applicable for modification order, original quantity is &#39;qty&#39; from orderbook | [optional] 
 **org_limit_price** | **float**| Original limit price is applicable for modification order, original limit price is limit price from orderbook | [optional] 
 **org_trig_price** | **float**| Original trigger price is applicable for modification order, original trigger price is trigger price from orderbook | [optional] 
 **org_stop_trig_price** | **float**| Original stop loss price is applicable only for Cover and Bracket order modification, original stop loss price is stop loss price from orderbook. | [optional] 
 **fill_qty** | **float**| fillQty is partially filled quantity, fillQty is &#39;fillQty&#39; from orderbook. | [optional] 
 **order_id** | **str**| Order id is applicable for bracket and cover order modification  | [optional] 
 **main_leg_order_id** | **str**| Mainleg order id field is applicable for bracket and cover order | [optional] 

### Return type

[**GetOrderMargin200Response**](GetOrderMargin200Response.md)

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

# **get_orders**
> GetOrders200Response get_orders(sym_details=sym_details)

Orders

to get list of orders placed

### Example

* Bearer (Token) Authentication (http_bearer):

```python
import time
import os
import openapi_client
from openapi_client.models.get_orders200_response import GetOrders200Response
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
    api_instance = openapi_client.OrdersApi(api_client)
    sym_details = True # bool | Sending symDetails:'true' - will provide the symbol object in response for every record. Symbol object contains details such as price-tick, lotsize, token etc.., (optional)

    try:
        # Orders
        api_response = api_instance.get_orders(sym_details=sym_details)
        print("The response of OrdersApi->get_orders:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrdersApi->get_orders: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sym_details** | **bool**| Sending symDetails:&#39;true&#39; - will provide the symbol object in response for every record. Symbol object contains details such as price-tick, lotsize, token etc.., | [optional] 

### Return type

[**GetOrders200Response**](GetOrders200Response.md)

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

# **get_positions**
> GetPositions200Response get_positions(sym_details=sym_details)

Positions 

to get a list of positions records </br></br> <b>MTM Calculations:</b> <ul> <li><b>Realized:</b> realizedPnl</li> <li><b>UnRealized:</b> ( netQty * ( LTP - netAvgPrice)) * multiplier * pricefactor</li> <li><b>Total MTM:</b> Realized + UnRealized</li> </ul> <b>P&L Calculations:</b> <ul> <li><b>Realized:</b> realizedOrgPnl</li> <li><b>UnRealized:</b> ( netQty * ( LTP - netOrgAvgPrice)) * multiplier * pricefactor</li> <li><b>Total P&L:</b> Realized + UnRealized</li> </ul> <b>Day Positions - MTM Calculations:</b> <ul> <li><b>Realized:</b> dayRealizedPnl</li> <li><b>UnRealized:</b> ( dayQty * ( LTP - dayAvg)) * multiplier * pricefactor</li> <li><b>Total Day MTM:</b> Realized + UnRealized</li> </ul> <b>Note:</b> <ul> <li>For the commodity (MCX), the net quantity should be multiplied by the lot size in the above calculations.</li> <li>The LTP mentioned above should be retrieved from real-time updates via the streaming SDK</li> </ul>

### Example

* Bearer (Token) Authentication (http_bearer):

```python
import time
import os
import openapi_client
from openapi_client.models.get_positions200_response import GetPositions200Response
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
    api_instance = openapi_client.OrdersApi(api_client)
    sym_details = True # bool | Sending symDetails:'true' - will provide the symbol object in response for every record. Symbol object contains details such as price-tick, lotsize, token etc.., (optional)

    try:
        # Positions 
        api_response = api_instance.get_positions(sym_details=sym_details)
        print("The response of OrdersApi->get_positions:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrdersApi->get_positions: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sym_details** | **bool**| Sending symDetails:&#39;true&#39; - will provide the symbol object in response for every record. Symbol object contains details such as price-tick, lotsize, token etc.., | [optional] 

### Return type

[**GetPositions200Response**](GetPositions200Response.md)

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

# **get_trades**
> GetTrades200Response get_trades(sym_details=sym_details)

Trades

to get a list of trade records

### Example

* Bearer (Token) Authentication (http_bearer):

```python
import time
import os
import openapi_client
from openapi_client.models.get_trades200_response import GetTrades200Response
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
    api_instance = openapi_client.OrdersApi(api_client)
    sym_details = True # bool | Sending symDetails:'true' - will provide the symbol object in response for every record. Symbol object contains details such as price-tick, lotsize, token etc.., (optional)

    try:
        # Trades
        api_response = api_instance.get_trades(sym_details=sym_details)
        print("The response of OrdersApi->get_trades:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrdersApi->get_trades: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sym_details** | **bool**| Sending symDetails:&#39;true&#39; - will provide the symbol object in response for every record. Symbol object contains details such as price-tick, lotsize, token etc.., | [optional] 

### Return type

[**GetTrades200Response**](GetTrades200Response.md)

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

# **modify_order**
> ModifyOrder200Response modify_order(sym_id, order_id, qty, type, validity, limit_price=limit_price, trig_price=trig_price, disc_qty=disc_qty, mkt_prot=mkt_prot, side=side)

Modify Order

to modify the pending order

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
    api_instance = openapi_client.OrdersApi(api_client)
    sym_id = 'sym_id_example' # str | Unique identifier of the symbol
    order_id = 'order_id_example' # str | Order id of an order which needs modification. This id will be received in orders service
    qty = 3.4 # float | Total order quantity after the modification. ( Filled Qty (if nonzero) + (Modified Qty or Pending Qty)). Example: If the order quantity is 100, out of that 60 is already filled, and if we are modifying the pending qty from 40 to 70 then qty => (60 + 70) = 130 should be sent. 
    type = 'type_example' # str | Price type of an order
    validity = 'validity_example' # str | Validity of an order, EOS is applicable for BSE scrips only
    limit_price = 3.4 # float | This is required only for limit and stop limit orders (optional)
    trig_price = 3.4 # float | This is required only for stoploss limit and stoploss market orders (optional)
    disc_qty = 3.4 # float | Disclosed quantity of an order (optional)
    mkt_prot = 3.4 # float | Market order protection percentage. Applicable only for market orders (optional)
    side = 'side_example' # str | Order side 'buy' or 'sell' (optional)

    try:
        # Modify Order
        api_response = api_instance.modify_order(sym_id, order_id, qty, type, validity, limit_price=limit_price, trig_price=trig_price, disc_qty=disc_qty, mkt_prot=mkt_prot, side=side)
        print("The response of OrdersApi->modify_order:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrdersApi->modify_order: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sym_id** | **str**| Unique identifier of the symbol | 
 **order_id** | **str**| Order id of an order which needs modification. This id will be received in orders service | 
 **qty** | **float**| Total order quantity after the modification. ( Filled Qty (if nonzero) + (Modified Qty or Pending Qty)). Example: If the order quantity is 100, out of that 60 is already filled, and if we are modifying the pending qty from 40 to 70 then qty &#x3D;&gt; (60 + 70) &#x3D; 130 should be sent.  | 
 **type** | **str**| Price type of an order | 
 **validity** | **str**| Validity of an order, EOS is applicable for BSE scrips only | 
 **limit_price** | **float**| This is required only for limit and stop limit orders | [optional] 
 **trig_price** | **float**| This is required only for stoploss limit and stoploss market orders | [optional] 
 **disc_qty** | **float**| Disclosed quantity of an order | [optional] 
 **mkt_prot** | **float**| Market order protection percentage. Applicable only for market orders | [optional] 
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

# **place_order**
> PlaceOrder200Response place_order(sym_id, qty, side, type, product, validity, limit_price=limit_price, trig_price=trig_price, disc_qty=disc_qty, amo=amo, mkt_prot=mkt_prot, remarks=remarks)

Place Order

to place the order

### Example

* Bearer (Token) Authentication (http_bearer):

```python
import time
import os
import openapi_client
from openapi_client.models.place_order200_response import PlaceOrder200Response
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
    api_instance = openapi_client.OrdersApi(api_client)
    sym_id = 'sym_id_example' # str | Unique identifier of the symbol
    qty = 3.4 # float | No of shares to buy or sell. For derivatives, pass the quantity by multiplying with lot size. Example: To buy 1 lot of NIFTY option, pass the quantity as 50.
    side = 'side_example' # str | Order side 'buy' or 'sell'
    type = 'type_example' # str | Price type of an order
    product = 'product_example' # str | Product type of an order. 'delivery' is applicable for equities. 'normal' is applicable for derivatives. 'intraday' is applicable for both equity and derivatives
    validity = 'validity_example' # str | Validity of an order, EOS is applicable for BSE scrips only
    limit_price = 3.4 # float | This is required only for limit and stop limit orders (optional)
    trig_price = 3.4 # float | This is required only for stoploss limit and stoploss market orders (optional)
    disc_qty = 3.4 # float | Disclosed quantity of an order (optional)
    amo = True # bool | Pass this field as true to place an amo order. (optional)
    mkt_prot = 3.4 # float | Market order protection percentage. Applicable only for market orders (optional)
    remarks = 'remarks_example' # str | Any tag or message to track in orderbook.Allowed length upto 10 Characters. Please note remarks more than 10 characters will be stripped out. (optional)

    try:
        # Place Order
        api_response = api_instance.place_order(sym_id, qty, side, type, product, validity, limit_price=limit_price, trig_price=trig_price, disc_qty=disc_qty, amo=amo, mkt_prot=mkt_prot, remarks=remarks)
        print("The response of OrdersApi->place_order:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrdersApi->place_order: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sym_id** | **str**| Unique identifier of the symbol | 
 **qty** | **float**| No of shares to buy or sell. For derivatives, pass the quantity by multiplying with lot size. Example: To buy 1 lot of NIFTY option, pass the quantity as 50. | 
 **side** | **str**| Order side &#39;buy&#39; or &#39;sell&#39; | 
 **type** | **str**| Price type of an order | 
 **product** | **str**| Product type of an order. &#39;delivery&#39; is applicable for equities. &#39;normal&#39; is applicable for derivatives. &#39;intraday&#39; is applicable for both equity and derivatives | 
 **validity** | **str**| Validity of an order, EOS is applicable for BSE scrips only | 
 **limit_price** | **float**| This is required only for limit and stop limit orders | [optional] 
 **trig_price** | **float**| This is required only for stoploss limit and stoploss market orders | [optional] 
 **disc_qty** | **float**| Disclosed quantity of an order | [optional] 
 **amo** | **bool**| Pass this field as true to place an amo order. | [optional] 
 **mkt_prot** | **float**| Market order protection percentage. Applicable only for market orders | [optional] 
 **remarks** | **str**| Any tag or message to track in orderbook.Allowed length upto 10 Characters. Please note remarks more than 10 characters will be stripped out. | [optional] 

### Return type

[**PlaceOrder200Response**](PlaceOrder200Response.md)

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

