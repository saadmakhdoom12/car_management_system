import os
import yaml
from typing import Dict, Any


def load_config(config_file: str) -> Dict[str, Any]:
    """Load configuration from YAML file"""
    default_config = {
        'database': {
            'name': 'car_management.db',
            'path': 'data'
        },
        'logging': {
            'level': 'INFO',
            'file': 'logs/app.log'
        },
        'reports': {
            'output_dir': 'reports'
        }
    }
    
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                return config if config else default_config
        return default_config
    except Exception as e:
        print(f"Error loading config: {e}")
        return default_config