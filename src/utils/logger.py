import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

def setup_logger(log_file: str, level: str = 'INFO') -> logging.Logger:
    """Setup application logger with file and console handlers"""
    
    # Create logs directory if it doesn't exist
    Path(log_file).parent.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger('CarManagementSystem')
    logger.setLevel(getattr(logging, level.upper()))
    
    # File Handler
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=1024 * 1024,  # 1MB
        backupCount=5
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger