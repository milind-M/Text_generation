# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path
import site

block_cipher = None

# Get the current directory
current_dir = os.getcwd()

# Find site-packages directory
site_packages = site.getsitepackages()[0]

# Define data files to include
datas = [
    ('css', 'css'),
    ('js', 'js'),
    ('extensions', 'extensions'),
    ('modules', 'modules'),
    ('user_data', 'user_data'),
    ('requirements', 'requirements'),
    ('download_model.py', '.'),  # Include download_model.py in root
    ('server.py', '.'),          # Include original server.py
]

# Include any .py files in the root directory
for file in os.listdir(current_dir):
    if file.endswith('.py') and file not in ['webview_app.py', 'download_model.py', 'server.py']:
        datas.append((file, '.'))

# Explicitly ensure CSS files are included (critical for chat styles)
css_files = [
    'css/chat_style-cai-chat.css',
    'css/chat_style-cai-chat-square.css', 
    'css/chat_style-Dark.css',
    'css/chat_style-TheEncrypted777.css',
    'css/chat_style-messenger.css',
    'css/chat_style-wpp.css',
    'css/html_readable_style.css',
    'css/html_instruct_style.css',
    'css/main.css'
]

# Add individual CSS files to ensure they're not missed
for css_file in css_files:
    if os.path.exists(css_file):
        datas.append((css_file, 'css'))
        print(f"Explicitly added CSS file: {css_file}")
    else:
        print(f"Warning: CSS file not found: {css_file}")

# Add CSS directories 
css_dirs = ['css/NotoSans', 'css/highlightjs', 'css/katex']
for css_dir in css_dirs:
    if os.path.exists(css_dir):
        datas.append((css_dir, css_dir))
        print(f"Added CSS directory: {css_dir}")

# Add Gradio files - use collect_all_packages for comprehensive inclusion
try:
    from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_all
    
    # Collect all Gradio files (data, submodules, etc.)
    gradio_datas, gradio_binaries, gradio_hiddenimports = collect_all('gradio')
    gradio_client_datas, gradio_client_binaries, gradio_client_hiddenimports = collect_all('gradio_client')
    
    # Add to our lists
    datas.extend(gradio_datas)
    datas.extend(gradio_client_datas)
    
    print(f"Added {len(gradio_datas)} Gradio data files")
    print(f"Added {len(gradio_client_datas)} Gradio client data files")
    
except Exception as e:
    print(f"Warning: Could not collect all Gradio files: {e}")
    # More comprehensive fallback
    gradio_path = os.path.join(site_packages, 'gradio')
    gradio_client_path = os.path.join(site_packages, 'gradio_client')
    
    if os.path.exists(gradio_path):
        # Add entire gradio package
        datas.append((gradio_path, 'gradio'))
        print(f"Added entire gradio directory as fallback")
        
    if os.path.exists(gradio_client_path):
        # Add entire gradio_client package
        datas.append((gradio_client_path, 'gradio_client'))
        print(f"Added entire gradio_client directory as fallback")

# Add llama_cpp_binaries package and its binary files
try:
    import llama_cpp_binaries
    llama_cpp_bin_path = os.path.dirname(llama_cpp_binaries.get_binary_path())
    if os.path.exists(llama_cpp_bin_path):
        datas.append((llama_cpp_bin_path, 'llama_cpp_binaries/bin'))
        print(f"Added llama_cpp_binaries from: {llama_cpp_bin_path}")
except ImportError:
    print("Warning: llama_cpp_binaries not found")

# Add other critical packages that might be missing
try:
    # Collect other important packages - expanded list (including llama_cpp_binaries)
    critical_packages = ['fastapi', 'starlette', 'uvicorn', 'pydantic', 'anyio', 'httpx', 'jinja2', 'aiofiles', 'websockets', 'orjson', 'python_multipart', 'h11', 'httptools', 'sniffio', 'httpcore', 'wsproto', 'llama_cpp_binaries']
    for pkg in critical_packages:
        try:
            pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all(pkg)
            datas.extend(pkg_datas)
            print(f"Added {len(pkg_datas)} files from {pkg}")
        except Exception as pkg_e:
            print(f"Warning: Could not collect {pkg}: {pkg_e}")
            # Fallback: add entire package directory
            pkg_path = os.path.join(site_packages, pkg)
            if os.path.exists(pkg_path):
                datas.append((pkg_path, pkg))
                print(f"Added entire {pkg} directory as fallback")

    # Force include entire gradio and gradio_client packages as final fallback
    gradio_path = os.path.join(site_packages, 'gradio')
    gradio_client_path = os.path.join(site_packages, 'gradio_client')
    
    if os.path.exists(gradio_path):
        datas.append((gradio_path, 'gradio'))
        print(f"Force added entire gradio package")
        
    if os.path.exists(gradio_client_path):
        datas.append((gradio_client_path, 'gradio_client'))
        print(f"Force added entire gradio_client package")
                
except Exception as e:
    print(f"Warning: Error collecting critical packages: {e}")

# Automatically collect all submodules for critical packages
try:
    gradio_submodules = collect_submodules('gradio')
    gradio_client_submodules = collect_submodules('gradio_client')
    fastapi_submodules = collect_submodules('fastapi')
    starlette_submodules = collect_submodules('starlette')
    uvicorn_submodules = collect_submodules('uvicorn')
    
    print(f"Found {len(gradio_submodules)} gradio submodules")
    print(f"Found {len(gradio_client_submodules)} gradio_client submodules")
    print(f"Found {len(fastapi_submodules)} fastapi submodules")
    print(f"Found {len(starlette_submodules)} starlette submodules")
    print(f"Found {len(uvicorn_submodules)} uvicorn submodules")
    
except Exception as e:
    print(f"Warning: Could not collect submodules: {e}")
    gradio_submodules = []
    gradio_client_submodules = []
    fastapi_submodules = []
    starlette_submodules = []
    uvicorn_submodules = []


# Add model files and directories with proper structure
model_locations = ['models', 'user_data/models']
for model_dir in model_locations:
    if os.path.exists(model_dir):
        datas.append((model_dir, model_dir))
        print(f"Added model directory: {model_dir}")

# Add any additional files that might be needed
# Add configuration files
config_files = [
    'settings.yaml',
    'user_data/settings.yaml',
    'characters', 
    'loras',
    'presets',
    'prompts',
    'training/datasets',
    'training/formats'
]

for config_item in config_files:
    if os.path.exists(config_item):
        if os.path.isfile(config_item):
            datas.append((config_item, os.path.dirname(config_item) if os.path.dirname(config_item) else '.'))
        else:
            datas.append((config_item, config_item))
        print(f"Added config item: {config_item}")

# Hidden imports - modules that PyInstaller might miss
hiddenimports = [
    'webview',
    'webview.platforms.winforms',
    'webview.platforms.cef',
    'webview.platforms.mshtml',
    'webview.platforms.edgechromium',
    'gradio',
    'gradio.components',
    'gradio.interface',
    'gradio.blocks',
    'gradio.blocks_events',  # This was missing!
    'gradio.routes',
    'gradio.utils',
    'gradio.queueing', 
    'gradio.route_utils',
    'gradio.processing_utils',
    'gradio.data_classes',
    'gradio.themes',
    'gradio.themes.utils',
    'gradio._simple_templates',
    'gradio._simple_templates.simpledropdown',
    'gradio._simple_templates.simpleimage',
    'gradio._simple_templates.simpletextbox',
    'gradio.helpers',
    'gradio.queue',
    'gradio.events',
    'gradio.flagging',
    'gradio.interpretation',
    'gradio.external',
    'gradio.networking',
    'gradio.reload',
    'gradio.oauth',
    'gradio.server',
    'gradio.cli',
    'gradio_client',
    'gradio_client.client',
    'gradio_client.serializing',
    'gradio_client.compatibility',
    'gradio_client.utils',
    # FastAPI and related
    'fastapi',
    'fastapi.applications',
    'fastapi.routing',
    'fastapi.responses',
    'fastapi.requests',
    'fastapi.params',
    'fastapi.dependencies',
    'fastapi.security',
    'fastapi.middleware',
    'fastapi.encoders',
    'fastapi.exceptions',
    'fastapi.background',
    'fastapi.staticfiles',
    'fastapi.templating',
    # Starlette
    'starlette',
    'starlette.applications',
    'starlette.routing',
    'starlette.responses',
    'starlette.requests',
    'starlette.middleware',
    'starlette.middleware.errors',
    'starlette.middleware.cors',
    'starlette.middleware.trustedhost',
    'starlette._exception_handler',
    'starlette.staticfiles',
    'starlette.templating',
    'starlette.background',
    'starlette.websockets',
    # Uvicorn
    'uvicorn',
    'uvicorn.main',
    'uvicorn.server',
    'uvicorn.config',
    'uvicorn.protocols.http.h11_impl',
    'uvicorn.protocols.http.httptools_impl',
    'uvicorn.protocols.websockets.websockets_impl',
    'uvicorn.protocols.websockets.wsproto_impl',
    'uvicorn.lifespan.on',
    'uvicorn.lifespan.off',
    'uvicorn.loops.auto',
    'uvicorn.loops.asyncio',
    'uvicorn.middleware.proxy_headers',
    'uvicorn.middleware.wsgi',
    'uvicorn.middleware.asgi2',
    # Other critical web dependencies
    'anyio',
    'anyio._backends._asyncio',
    'anyio.to_thread',
    'anyio.from_thread',
    'sniffio',
    'httpx',
    'httpcore',
    'h11',
    'httptools',
    'websockets',
    'websockets.server',
    'websockets.client',
    'wsproto',
    'pydantic',
    'pydantic.fields',
    'pydantic.validators',
    'pydantic.json_encoders',
    'pydantic.config',
    'jinja2',
    'jinja2.loaders',
    'aiofiles',
    'python_multipart',
    'orjson',
    # Exception handling
    'exceptiongroup',
    'exceptiongroup._exceptions', 
    'modules.shared',
    'modules.ui',
    'modules.ui_chat',
    'modules.ui_default',
    'modules.ui_notebook',
    'modules.ui_parameters',
    'modules.ui_model_menu',
    'modules.ui_session',
    'modules.ui_file_saving',
    'modules.logging_colors',
    'modules.utils',
    'modules.extensions',
    'modules.models',
    'modules.training',
    'modules.chat',
    'modules.LoRA',
    'modules.models_settings',
    'modules.gradio_hijack',
    'modules.block_requests',
    'modules.prompts',
    'transformers',
    'torch',
    'accelerate',
    'bitsandbytes',
    'sentencepiece',
    'tiktoken',
    'datasets',
    'peft',
    'safetensors',
    # Llama.cpp binaries support
    'llama_cpp_binaries',
    
    # Other utilities (removing duplicates)
    'yaml',
    'markdown',
    'rich',
    'psutil',
    'requests',
    'numpy',
    'pandas',
    'matplotlib',
    'scipy',
    'PIL',
    'einops',
    'tqdm',
    'wandb',
    'tensorboard',
    'html2text',
    'python_docx',
    'PyPDF2',
    'bottle',
    'flask',
    'werkzeug'
]

# Remove duplicates from hiddenimports
hiddenimports = list(set(hiddenimports))

# Exclude some modules that might cause issues
excludes = [
    'tkinter',
    'matplotlib.tests',
    'numpy.tests',
    'scipy.tests',
    'pandas.tests',
    'PIL.tests',
]

a = Analysis(
    ['webview_app.py'],
    pathex=[current_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['runtime_hook_fix_css.py'],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TextGenWebUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Set to False for windowed app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # You can add an icon file here if you have one
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TextGenWebUI',
)