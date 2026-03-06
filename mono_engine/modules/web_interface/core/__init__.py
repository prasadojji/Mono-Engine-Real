"""
Core utilities for the web interface.
Provides shared functionality for data processing, validation, and database operations.
"""

from .data_utils import (
    safe_float, safe_int, safe_str, safe_datetime_str, safe_bool,
    sanitize_dataframe, dataframe_to_json_serializable, validate_json_serializable,
    make_json_response
)
from .db_utils import (
    get_database_path, validate_database_connection, safe_sql_query,
    get_table_info, get_database_stats, execute_safe_query, check_table_exists
)
from .response_utils import (
    success_response, error_response, api_error_handler, validate_request_data,
    paginated_response, health_check_response, database_health_check, APIResponse
)
from .validation import (
    DataValidator, ValidationError, validate_symbol, validate_date_string,
    validate_time_string, validate_pagination_params, validate_filter_params
)

__all__ = [
    # Data utilities
    'safe_float', 'safe_int', 'safe_str', 'safe_datetime_str', 'safe_bool',
    'sanitize_dataframe', 'dataframe_to_json_serializable', 'validate_json_serializable',
    'make_json_response',

    # Database utilities
    'get_database_path', 'validate_database_connection', 'safe_sql_query',
    'get_table_info', 'get_database_stats', 'execute_safe_query', 'check_table_exists',

    # Response utilities
    'success_response', 'error_response', 'api_error_handler', 'validate_request_data',
    'paginated_response', 'health_check_response', 'database_health_check', 'APIResponse',

    # Validation utilities
    'DataValidator', 'ValidationError', 'validate_symbol', 'validate_date_string',
    'validate_time_string', 'validate_pagination_params', 'validate_filter_params'
]