import sys
import os
from pathlib import Path

# Runtime hook to fix CSS file loading in PyInstaller bundle
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # We're running in a PyInstaller bundle
    bundle_dir = sys._MEIPASS
    
    print(f"PyInstaller bundle detected. Bundle directory: {bundle_dir}")
    
    # Get the directory where the executable is located (not the _internal directory)
    exe_dir = os.path.dirname(sys.executable)
    print(f"Executable directory: {exe_dir}")
    
    # Set up proper working directory to the exe directory
    os.chdir(exe_dir)
    print(f"Changed working directory to: {os.getcwd()}")
    
    # Set a flag for other modules to detect PyInstaller environment
    import modules.shared as shared
    shared.is_pyinstaller = True
    print("Set PyInstaller flag in shared module")
    
    # Create symlinks or copy directories that Gradio needs to serve
    def setup_gradio_directories():
        """Set up directories that Gradio needs to serve files"""
        import shutil
        
        # Directories to make available for Gradio
        dirs_to_setup = ['css', 'js', 'extensions']
        
        for dir_name in dirs_to_setup:
            source_dir = Path(bundle_dir) / dir_name
            target_dir = Path.cwd() / dir_name
            
            if source_dir.exists() and not target_dir.exists():
                try:
                    # Try to create a symlink first (faster)
                    target_dir.symlink_to(source_dir, target_is_directory=True)
                    print(f"Created symlink: {target_dir} -> {source_dir}")
                except OSError:
                    # If symlink fails (e.g., on Windows without admin), copy the directory
                    shutil.copytree(source_dir, target_dir)
                    print(f"Copied directory: {source_dir} -> {target_dir}")
            elif target_dir.exists():
                print(f"Directory already exists: {target_dir}")
            else:
                print(f"Source directory not found: {source_dir}")
    
    setup_gradio_directories()
    
    # Create a monkey patch for the CSS loading
    def patch_css_loading():
        """Monkey patch to fix CSS file loading in PyInstaller bundle"""
        import importlib.util
        
        # Check if html_generator module is already loaded
        if 'modules.html_generator' in sys.modules:
            print("html_generator module already loaded, applying CSS fix...")
            
            # Get the module
            html_gen_module = sys.modules['modules.html_generator']
            
            # Fix the chat_styles dictionary if it's empty or has KeyError issues
            if not hasattr(html_gen_module, 'chat_styles') or not html_gen_module.chat_styles:
                print("Fixing chat_styles dictionary...")
                
                # Load CSS files manually
                css_dir = Path(bundle_dir) / 'css'
                chat_styles = {}
                
                if css_dir.exists():
                    css_files = list(css_dir.glob('chat_style*.css'))
                    print(f"Found {len(css_files)} chat style files")
                    
                    for css_file in css_files:
                        # Extract style name from filename
                        style_name = '-'.join(css_file.stem.split('-')[1:])
                        try:
                            with open(css_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                                # Apply minification if the function exists
                                if hasattr(html_gen_module, 'minify_css'):
                                    content = html_gen_module.minify_css(content)
                                chat_styles[style_name] = content
                                print(f"Loaded CSS style: {style_name}")
                        except Exception as e:
                            print(f"Error loading CSS file {css_file}: {e}")
                
                # Update the module's chat_styles
                html_gen_module.chat_styles = chat_styles
                print(f"Updated chat_styles with {len(chat_styles)} styles")
                
                # Also try to load the readable and instruct CSS files
                try:
                    readable_css_path = css_dir / 'html_readable_style.css'
                    instruct_css_path = css_dir / 'html_instruct_style.css'
                    
                    if readable_css_path.exists():
                        with open(readable_css_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if hasattr(html_gen_module, 'minify_css'):
                                content = html_gen_module.minify_css(content)
                            html_gen_module.readable_css = content
                            print("Loaded readable CSS")
                    
                    if instruct_css_path.exists():
                        with open(instruct_css_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if hasattr(html_gen_module, 'minify_css'):
                                content = html_gen_module.minify_css(content)
                            html_gen_module.instruct_css = content
                            print("Loaded instruct CSS")
                            
                except Exception as e:
                    print(f"Error loading additional CSS files: {e}")
    
    # Try to patch immediately
    patch_css_loading()
    
    # Also set up a delayed patch in case the module loads later
    original_import = __builtins__.__import__
    
    def patched_import(name, *args, **kwargs):
        module = original_import(name, *args, **kwargs)
        if name == 'modules.html_generator' or name.endswith('.html_generator'):
            print(f"Detected html_generator import, applying CSS patch...")
            patch_css_loading()
        return module
    
    __builtins__.__import__ = patched_import
    
    # Fix llama_cpp_binaries path
    try:
        import llama_cpp_binaries
        original_get_binary_path = llama_cpp_binaries.get_binary_path
        
        def patched_get_binary_path():
            # In PyInstaller bundle, look for the binary in the correct location
            binary_path = Path(bundle_dir) / 'llama_cpp_binaries' / 'bin' / 'llama-server.exe'
            if binary_path.exists():
                print(f"Found llama-server.exe at: {binary_path}")
                return str(binary_path)
            else:
                print(f"llama-server.exe not found at expected path: {binary_path}")
                # Fallback to original function
                return original_get_binary_path()
        
        # Monkey patch the function
        llama_cpp_binaries.get_binary_path = patched_get_binary_path
        print("Patched llama_cpp_binaries.get_binary_path()")
        
    except ImportError:
        print("llama_cpp_binaries not available for patching")
