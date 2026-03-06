"""
Response utilities for standardized API responses and error handling.
Provides consistent JSON response formatting across all API endpoints.
"""

from flask import jsonify
from typing import Any, Dict, Optional
import traceback
import logging

# Set up logging
logger = logging.getLogger(__name__)


def success_response(data: Any = None, message: str = "", **kwargs) -> Dict[str, Any]:
    """
    Create a standardized success response.

    Args:
        data: Response data
        message: Optional success message
        **kwargs: Additional response fields

    Returns:
        Standardized success response dictionary
    """
    response = {
        'success': True,
        'data': data if data is not None else {}
    }

    if message:
        response['message'] = message

    # Add any additional fields
    response.update(kwargs)

    return response


def error_response(message: str, error_code: Optional[str] = None,
                  details: Optional[Any] = None, **kwargs) -> Dict[str, Any]:
    """
    Create a standardized error response.

    Args:
        message: Error message
        error_code: Optional error code
        details: Optional error details
        **kwargs: Additional response fields

    Returns:
        Standardized error response dictionary
    """
    response = {
        'success': False,
        'message': message
    }

    if error_code:
        response['error_code'] = error_code

    if details is not None:
        response['details'] = details

    # Add any additional fields
    response.update(kwargs)

    return response


def api_error_handler(func):
    """
    Decorator for API endpoints to handle exceptions and return standardized error responses.

    Args:
        func: API endpoint function

    Returns:
        Wrapped function with error handling
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"API Error in {func.__name__}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")

            # Return standardized error response
            error_resp = error_response(
                message="An internal server error occurred",
                error_code="INTERNAL_ERROR",
                details=str(e) if logger.level <= logging.DEBUG else None
            )

            return jsonify(error_resp), 500

    wrapper.__name__ = func.__name__
    return wrapper


def validate_request_data(required_fields: list, data: Dict[str, Any]) -> tuple:
    """
    Validate that required fields are present in request data.

    Args:
        required_fields: List of required field names
        data: Request data dictionary

    Returns:
        Tuple of (is_valid, missing_fields, error_response)
    """
    missing_fields = []

    for field in required_fields:
        if field not in data or data[field] is None:
            missing_fields.append(field)

    if missing_fields:
        error_resp = error_response(
            message=f"Missing required fields: {', '.join(missing_fields)}",
            error_code="MISSING_FIELDS",
            missing_fields=missing_fields
        )
        return False, missing_fields, error_resp

    return True, [], None


def paginated_response(data: list, page: int = 1, per_page: int = 50,
                      total: Optional[int] = None) -> Dict[str, Any]:
    """
    Create a paginated response.

    Args:
        data: List of data items
        page: Current page number
        per_page: Items per page
        total: Total number of items (if None, calculated from data length)

    Returns:
        Paginated response dictionary
    """
    if total is None:
        total = len(data)

    total_pages = (total + per_page - 1) // per_page  # Ceiling division

    response_data = {
        'items': data,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    }

    return success_response(response_data)


def health_check_response(service_name: str, status: str = "healthy",
                         details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create a health check response.

    Args:
        service_name: Name of the service
        status: Health status
        details: Optional health check details

    Returns:
        Health check response dictionary
    """
    response_data = {
        'service': service_name,
        'status': status,
        'timestamp': __import__('datetime').datetime.utcnow().isoformat()
    }

    if details:
        response_data['details'] = details

    return success_response(response_data)


def database_health_check(db_path: str) -> Dict[str, Any]:
    """
    Perform a database health check.

    Args:
        db_path: Path to the database file

    Returns:
        Health check response dictionary
    """
    try:
        from .db_utils import validate_database_connection, get_database_stats

        is_connected = validate_database_connection(db_path)

        if is_connected:
            stats = get_database_stats(db_path)
            return health_check_response(
                service_name="database",
                status="healthy",
                details={
                    'connection': 'ok',
                    'tables_count': len(stats.get('tables', {})),
                    'total_records': stats.get('total_records', 0)
                }
            )
        else:
            return health_check_response(
                service_name="database",
                status="unhealthy",
                details={'connection': 'failed'}
            )

    except Exception as e:
        return health_check_response(
            service_name="database",
            status="error",
            details={'error': str(e)}
        )


class APIResponse:
    """Helper class for building API responses."""

    def __init__(self):
        self.data = {}
        self.errors = []
        self.warnings = []

    def add_data(self, key: str, value: Any):
        """Add data to the response."""
        self.data[key] = value
        return self

    def add_error(self, message: str, code: Optional[str] = None):
        """Add an error to the response."""
        error = {'message': message}
        if code:
            error['code'] = code
        self.errors.append(error)
        return self

    def add_warning(self, message: str):
        """Add a warning to the response."""
        self.warnings.append(message)
        return self

    def to_response(self, success: bool = None) -> Dict[str, Any]:
        """Convert to response dictionary."""
        if success is None:
            success = len(self.errors) == 0

        response = {
            'success': success,
            'data': self.data
        }

        if self.errors:
            response['errors'] = self.errors

        if self.warnings:
            response['warnings'] = self.warnings

        return response