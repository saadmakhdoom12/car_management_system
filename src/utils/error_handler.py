import sys
import logging
import traceback
from functools import wraps
from typing import Callable, Type, Union
from PyQt6.QtWidgets import QMessageBox


class CarManagementError(Exception):
    """Base exception class for Car Management System"""
    pass


class DatabaseError(CarManagementError):
    """Database related errors"""
    pass


class ValidationError(CarManagementError):
    """Data validation errors"""
    pass


def show_error_dialog(error_msg: str, title: str = "Error"):
    """Display error message in GUI dialog"""
    error_box = QMessageBox()
    error_box.setIcon(QMessageBox.Icon.Critical)
    error_box.setWindowTitle(title)
    error_box.setText(error_msg)
    error_box.exec()


def log_error(error: Exception, context: str = ""):
    """Log error with context information"""
    error_msg = f"{context}: {str(error)}" if context else str(error)
    logging.error(error_msg)
    logging.debug(traceback.format_exc())


def error_handler(error_types: Union[Type[Exception], tuple] = Exception,
                 show_dialog: bool = True):
    """Decorator for handling errors in functions"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except error_types as e:
                context = f"Error in {func.__name__}"
                log_error(e, context)
                if show_dialog:
                    show_error_dialog(str(e))
                raise
        return wrapper
    return decorator


def setup_exception_handling():
    """Setup global exception handler"""
    def global_exception_handler(exctype, value, tb):
        """Handle uncaught exceptions"""
        error_msg = ''.join(traceback.format_exception(exctype, value, tb))
        log_error(value, "Uncaught exception")
        show_error_dialog(
            "An unexpected error occurred. Please check the logs for details.",
            "Critical Error"
        )
        # Call original exception handler
        sys.__excepthook__(exctype, value, tb)

    sys.excepthook = global_exception_handler


@error_handler(DatabaseError)
def handle_db_error(operation: str):
    """Handle database specific errors"""
    raise DatabaseError(f"Database operation failed: {operation}")


@error_handler(ValidationError)
def handle_validation_error(field: str, value: str):
    """Handle validation specific errors"""
    raise ValidationError(f"Invalid {field}: {value}")