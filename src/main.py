import logging
import sys
import os
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from database.db_manager import DatabaseManager
from gui.main_window import MainWindow
from utils.config import load_config
from utils.logger import setup_logger

# Configure application constants
APP_NAME = "Car Management System"
APP_VERSION = "1.0.0"
CONFIG_FILE = "config.yml"


def setup_environment():
    """Setup application environment"""
    # Create necessary directories first
    dirs = ["logs", "data", "reports"]
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
    
    # Setup logging with proper path
    log_file = Path("logs") / f"app_{datetime.now().strftime('%Y%m%d')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    logging.info(f"Starting {APP_NAME} v{APP_VERSION}")

    # Load configuration
    config = load_config(CONFIG_FILE)

    return config


def initialize_database(config: dict):
    """Initialize database connection"""
    try:
        db_config = config.get('database', {})
        db_path = os.path.join(
            db_config.get('path', 'data'),
            db_config.get('name', 'car_management.db')
        )
        
        # Create data directory
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        db_manager = DatabaseManager(db_path)
        db_manager.initialize_tables()
        logging.info(f"Database initialized at: {db_path}")
        return db_manager
        
    except Exception as e:
        logging.error(f"Database initialization failed: {str(e)}")
        raise


def setup_application():
    """Setup Qt application with configurations"""
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)

    # Set application style
    app.setStyle("Fusion")

    # Qt6 handles high DPI scaling automatically
    # No need to set AA_EnableHighDpiScaling as it's deprecated in Qt6

    return app


def main():
    """Main application entry point"""
    try:
        # Setup environment and logging
        config = setup_environment()
        logging.info(f"Starting {APP_NAME} v{APP_VERSION}")

        # Initialize Qt Application
        app = setup_application()

        # Initialize database
        db_manager = initialize_database(config)

        # Create and show main window
        main_window = MainWindow(db_manager)
        main_window.show()

        # Start application event loop
        exit_code = app.exec()

        # Cleanup
        logging.info("Application shutting down")
        sys.exit(exit_code)

    except Exception as e:
        logging.critical(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
