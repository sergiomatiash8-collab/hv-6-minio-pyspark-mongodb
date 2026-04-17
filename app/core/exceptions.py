"""
Custom exceptions for the ETL pipeline. 
Provides clear error hierarchy for better error handling.
"""

class ETLException(Exception):
    """Base exception for all ETL errors."""
    pass


class DataValidationError(ETLException):
    """Raised when data validation fails."""
    pass


class StorageError(ETLException):
    """Raised when storage operations fail (MinIO, MongoDB)."""
    pass


class TransformationError(ETLException):
    """Raised when data transformation fails."""
    pass


class SparkSessionError(ETLException):
    """Raised when Spark session initialization fails."""
    pass


class ConfigurationError(ETLException):
    """Raised when configuration is invalid."""
    pass