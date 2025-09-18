"""
Runtime hook for PyInstaller to create required directories
"""
import os
import sys
from pathlib import Path

# Get the directory where the executable is running
if getattr(sys, 'frozen', False):
    # Running in a PyInstaller bundle
    app_path = Path(sys.executable).parent
else:
    # Running in normal Python environment
    app_path = Path(__file__).parent

# Required directories that need to exist
required_dirs = [
    'user_data',
    'user_data/models',
    'user_data/loras', 
    'user_data/characters',
    'user_data/extensions',
    'user_data/grammars',
    'user_data/instruction-templates',
    'user_data/logs',
    'user_data/logs/notebook',
    'user_data/mmproj',
    'user_data/presets',
    'user_data/training',
    'user_data/cache',
    'user_data/cache/gradio',
    'extensions',
    'css',
    'js'
]

# Create directories if they don't exist
for dir_path in required_dirs:
    full_path = app_path / dir_path
    full_path.mkdir(parents=True, exist_ok=True)

print(f"Created required directories in: {app_path}")