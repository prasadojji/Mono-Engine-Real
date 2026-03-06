"""
Data validation utilities for API requests and responses.
Provides validation functions for different data types and structures.
"""

from typing import Any, Dict, List, Optional, Union, Callable
import re


class ValidationError(Exception):
    """Custom exception for validation errors."""

    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(self.message)


class DataValidator:
    """Base class for data validation with common validation methods."""

    @staticmethod
    def validate_string(value: Any, field_name: str = "value",
                       min_length: Optional[int] = None,
                       max_length: Optional[int] = None,
                       pattern: Optional[str] = None) -> str:
        """
        Validate and convert to string.

        Args:
            value: Value to validate
            field_name: Name of the field for error messages
            min_length: Minimum string length
            max_length: Maximum string length
            pattern: Regex pattern to match

        Returns:
            Validated string

        Raises:
            ValidationError: If validation fails
        """
        if value is None:
            raise ValidationError(f"{field_name} cannot be null", field_name, value)

        str_value = str(value).strip()

        if min_length is not None and len(str_value) < min_length:
            raise ValidationError(
                f"{field_name} must be at least {min_length} characters long",
                field_name, value
            )

        if max_length is not None and len(str_value) > max_length:
            raise ValidationError(
                f"{field_name} must be at most {max_length} characters long",
                field_name, value
            )

        if pattern and not re.match(pattern, str_value):
            raise ValidationError(
                f"{field_name} does not match required pattern",
                field_name, value
            )

        return str_value

    @staticmethod
    def validate_number(value: Any, field_name: str = "value",
                       min_value: Optional[Union[int, float]] = None,
                       max_value: Optional[Union[int, float]] = None,
                       allow_float: bool = True) -> Union[int, float]:
        """
        Validate and convert to number.

        Args:
            value: Value to validate
            field_name: Name of the field for error messages
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            allow_float: Whether to allow float values

        Returns:
            Validated number

        Raises:
            ValidationError: If validation fails
        """
        if value is None or str(value).lower() in ['nan', 'inf', '-inf', '']:
            raise ValidationError(f"{field_name} must be a valid number", field_name, value)

        try:
            if allow_float:
                num_value = float(value)
            else:
                num_value = int(float(value))  # Convert through float to handle strings

            if not allow_float and not num_value == int(num_value):
                raise ValidationError(f"{field_name} must be an integer", field_name, value)

            if min_value is not None and num_value < min_value:
                raise ValidationError(
                    f"{field_name} must be at least {min_value}",
                    field_name, value
                )

            if max_value is not None and num_value > max_value:
                raise ValidationError(
                    f"{field_name} must be at most {max_value}",
                    field_name, value
                )

            return num_value

        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} must be a valid number", field_name, value)

    @staticmethod
    def validate_boolean(value: Any, field_name: str = "value") -> bool:
        """
        Validate and convert to boolean.

        Args:
            value: Value to validate
            field_name: Name of the field for error messages

        Returns:
            Validated boolean

        Raises:
            ValidationError: If validation fails
        """
        if isinstance(value, bool):
            return value

        if isinstance(value, (int, float)):
            return bool(value)

        if isinstance(value, str):
            lower_value = value.lower().strip()
            if lower_value in ['true', '1', 'yes', 'on']:
                return True
            elif lower_value in ['false', '0', 'no', 'off']:
                return False

        raise ValidationError(f"{field_name} must be a valid boolean", field_name, value)

    @staticmethod
    def validate_list(value: Any, field_name: str = "value",
                     min_length: Optional[int] = None,
                     max_length: Optional[int] = None,
                     item_validator: Optional[Callable] = None) -> list:
        """
        Validate and convert to list.

        Args:
            value: Value to validate
            field_name: Name of the field for error messages
            min_length: Minimum list length
            max_length: Maximum list length
            item_validator: Function to validate each item

        Returns:
            Validated list

        Raises:
            ValidationError: If validation fails
        """
        if value is None:
            raise ValidationError(f"{field_name} cannot be null", field_name, value)

        if not isinstance(value, list):
            raise ValidationError(f"{field_name} must be a list", field_name, value)

        if min_length is not None and len(value) < min_length:
            raise ValidationError(
                f"{field_name} must have at least {min_length} items",
                field_name, value
            )

        if max_length is not None and len(value) > max_length:
            raise ValidationError(
                f"{field_name} must have at most {max_length} items",
                field_name, value
            )

        if item_validator:
            validated_items = []
            for i, item in enumerate(value):
                try:
                    validated_items.append(item_validator(item))
                except ValidationError as e:
                    raise ValidationError(
                        f"{field_name}[{i}]: {e.message}",
                        f"{field_name}[{i}]", item
                    )
            return validated_items

        return value

    @staticmethod
    def validate_dict(value: Any, field_name: str = "value",
                     required_keys: Optional[List[str]] = None,
                     key_validator: Optional[Callable] = None) -> dict:
        """
        Validate and convert to dictionary.

        Args:
            value: Value to validate
            field_name: Name of the field for error messages
            required_keys: List of required keys
            key_validator: Function to validate key-value pairs

        Returns:
            Validated dictionary

        Raises:
            ValidationError: If validation fails
        """
        if value is None:
            raise ValidationError(f"{field_name} cannot be null", field_name, value)

        if not isinstance(value, dict):
            raise ValidationError(f"{field_name} must be a dictionary", field_name, value)

        if required_keys:
            missing_keys = [key for key in required_keys if key not in value]
            if missing_keys:
                raise ValidationError(
                    f"{field_name} is missing required keys: {', '.join(missing_keys)}",
                    field_name, value
                )

        if key_validator:
            validated_dict = {}
            for key, val in value.items():
                try:
                    validated_key, validated_value = key_validator(key, val)
                    validated_dict[validated_key] = validated_value
                except ValidationError as e:
                    raise ValidationError(
                        f"{field_name}['{key}']: {e.message}",
                        f"{field_name}['{key}']", val
                    )
            return validated_dict

        return value


# Predefined validators for common use cases
def validate_symbol(symbol: str) -> str:
    """Validate trading symbol format."""
    if not symbol or not isinstance(symbol, str):
        raise ValidationError("Symbol must be a non-empty string", "symbol", symbol)

    # Basic symbol validation (alphanumeric, underscore, hyphen)
    if not re.match(r'^[A-Z0-9_-]+$', symbol.upper()):
        raise ValidationError("Symbol contains invalid characters", "symbol", symbol)

    return symbol.upper()


def validate_date_string(date_str: str) -> str:
    """Validate date string format (YYYY-MM-DD)."""
    if not date_str or not isinstance(date_str, str):
        raise ValidationError("Date must be a non-empty string", "date", date_str)

    # Basic date format validation
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        raise ValidationError("Date must be in YYYY-MM-DD format", "date", date_str)

    return date_str


def validate_time_string(time_str: str) -> str:
    """Validate time string format (HH:MM)."""
    if not time_str or not isinstance(time_str, str):
        raise ValidationError("Time must be a non-empty string", "time", time_str)

    # Basic time format validation
    if not re.match(r'^\d{2}:\d{2}$', time_str):
        raise ValidationError("Time must be in HH:MM format", "time", time_str)

    return time_str


def validate_pagination_params(page: Any, per_page: Any) -> tuple:
    """Validate pagination parameters."""
    validator = DataValidator()

    page_num = validator.validate_number(page, "page", min_value=1)
    per_page_num = validator.validate_number(per_page, "per_page", min_value=1, max_value=1000)

    return int(page_num), int(per_page_num)


def validate_filter_params(filters: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and sanitize filter parameters."""
    validated_filters = {}

    # Define allowed filter fields and their validators
    filter_validators = {
        'symbol': validate_symbol,
        'type': lambda x: DataValidator.validate_string(x, "type", max_length=20),
        'status': lambda x: DataValidator.validate_string(x, "status", max_length=20),
        'from_date': validate_date_string,
        'to_date': validate_date_string,
        'from_time': validate_time_string,
        'to_time': validate_time_string,
        'pnl_filter': lambda x: DataValidator.validate_string(x, "pnl_filter", max_length=20),
        'sell_reason': lambda x: DataValidator.validate_string(x, "sell_reason", max_length=100),
    }

    for key, value in filters.items():
        if key in filter_validators and value is not None and str(value).strip():
            try:
                validated_filters[key] = filter_validators[key](value)
            except ValidationError:
                # Skip invalid filter values
                continue

    return validated_filters