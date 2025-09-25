"""
PyInstaller runtime hook to create required directories.
This file should be named pyi_rth_*.py to be automatically detected.
"""
import os
import sys
from pathlib import Path

def create_required_dirs():
    # Get the directory where the executable is running
    if getattr(sys, 'frozen', False):
        # Running in a PyInstaller bundle
        app_dir = Path(sys.executable).parent
    else:
        # Running in normal Python environment  
        app_dir = Path(__file__).parent
    
    # List of required directories
    required_dirs = [
        'user_data',
        'user_data/models',
        'user_data/loras',
        'user_data/characters',
        'user_data/extensions', 
        'user_data/grammars',
        'user_data/instruction-templates',
        'user_data/logs',
        'user_data/logs/chat',
        'user_data/logs/instruct',
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
    for dir_name in required_dirs:
        dir_path = app_dir / dir_name
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Warning: Could not create directory {dir_path}: {e}")

# Run the function when this hook is loaded
create_required_dirs()