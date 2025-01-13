import os
import sys

from cx_Freeze import Executable, setup

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Get absolute path to project root
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

# Dependencies
build_exe_options = {
    "packages": ["PyQt6", "src.gui", "src.database", "src.utils"],
    "includes": [
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",
        "sqlite3",
        "yaml",
        "fpdf"
    ],
    "include_files": [
        (os.path.join(ROOT_DIR, "src/gui"), "src/gui"),
        (os.path.join(ROOT_DIR, "src/database"), "src/database"),
        (os.path.join(ROOT_DIR, "src/utils"), "src/utils"),
        (os.path.join(ROOT_DIR, "config.yml"), "config.yml")
    ],
    "excludes": ["tkinter", "test"],
    "include_msvcr": True,
    "path": sys.path + [os.path.join(ROOT_DIR, "src")]
}

# Create required directories
for dir_name in ['data', 'logs', 'reports']:
    os.makedirs(os.path.join(ROOT_DIR, dir_name), exist_ok=True)

# Executable configuration
executables = [
    Executable(
        os.path.join(ROOT_DIR, "src/main.py"),
        base="Win32GUI" if sys.platform == "win32" else None,
        target_name="car-management",
        icon=None  # Add icon path if available
    )
]

setup(
    name="Car Management System",
    version="1.0.0",
    description="Car Management System with SQLite and PyQt6",
    options={"build_exe": build_exe_options},
    executables=executables,
    packages=['src', 'src.gui', 'src.database', 'src.utils']
)
