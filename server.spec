# -- mode: python ; coding: utf-8 --
"""
PyInstaller spec file for Text Generation WebUI
Standalone build (no models included).
"""

from PyInstaller.utils.hooks import collect_all, collect_submodules
import os

# Get the script directory
script_dir = os.path.dirname(os.path.abspath(__file__))





datas = []
binaries = []
hiddenimports = []

# === CORE PACKAGES ===
core_packages = [
    'gradio', 'gradio_client', 'uvicorn', 'fastapi',
    'pandas', 'numpy', 'torch', 'transformers',
    'safetensors', 'huggingface_hub', 'tokenizers',
    'jinja2', 'markdown', 'requests', 'aiohttp',
    'websockets', 'pydantic', 'starlette', 'anyio',
    'httpx', 'tqdm', 'psutil', 'yaml', 'pillow',
    'accelerate', 'bitsandbytes', 'llama_cpp_binaries',
    'pywebview'  # Added for explicit collection
]

for package in core_packages:
    try:
        pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all(package)
        datas += pkg_datas or []
        binaries += pkg_binaries or []
        hiddenimports += pkg_hiddenimports or []
    except Exception:
        continue

# === LLAMA.CPP BINARIES SPECIAL HANDLING ===

try:
    import llama_cpp_binaries
    llama_bin_path = os.path.join(os.path.dirname(llama_cpp_binaries.__file__), 'bin')
    if os.path.exists(llama_bin_path):
        for dll_file in [
            'ggml.dll', 'ggml-base.dll', 'ggml-cpu.dll', 'ggml-cuda.dll',
            'llama.dll', 'mtmd.dll',
            'cublas64_12.dll', 'cublasLt64_12.dll', 'cudart64_12.dll'
        ]:
            dll_path = os.path.join(llama_bin_path, dll_file)
            if os.path.exists(dll_path):
                binaries.append((dll_path, '.'))

        server_exe = os.path.join(llama_bin_path, 'llama-server.exe')
        if os.path.exists(server_exe):
            binaries.append((server_exe, '.'))

        print(f"✓ Added llama_cpp_binaries files from {llama_bin_path}")
except Exception as e:
    print(f"⚠ Warning: Could not add llama_cpp_binaries files: {e}")

# === PROJECT FILES ===
modules_path = os.path.join(script_dir, "modules")
if os.path.exists(modules_path):
    for root, dirs, files in os.walk(modules_path):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        for file in files:
            if not file.endswith(('.pyc', '.pyo')):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(root, script_dir)
                datas.append((file_path, rel_path))


user_data_path = os.path.join(script_dir, "user_data")
if os.path.exists(user_data_path):
    for root, dirs, files in os.walk(user_data_path):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        for file in files:
            if not file.endswith(('.pyc', '.pyo')):
                if "models" not in root:  # Skip models entirely
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(root, script_dir)
                    datas.append((file_path, rel_path))

# === MODELS: ALWAYS PLACEHOLDER ONLY (NO REAL MODELS) ===
placeholder_dir = os.path.join(script_dir, "user_data", "models")
os.makedirs(placeholder_dir, exist_ok=True)
placeholder = os.path.join(placeholder_dir, ".placeholder")
with open(placeholder, "w") as f:
    f.write("placeholder")
datas.append((placeholder, "user_data/models"))

# === ASSETS ===
for asset in ["css", "js", "extensions"]:
    asset_path = os.path.join(script_dir, asset)
    if os.path.exists(asset_path):
        for root, dirs, files in os.walk(asset_path):
            dirs[:] = [d for d in dirs if d != '__pycache__']
            for file in files:
                if not file.endswith(('.pyc', '.pyo')):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(root, script_dir)
                    datas.append((file_path, rel_path))



for script in ['download-model.py', 'one_click.py']:
    script_path = os.path.join(script_dir, script)
    if os.path.exists(script_path):
        datas.append((script_path, '.'))

# === SUBMODULES ===
submodule_packages = [
    'pytz', 'transformers', 'gradio', 'uvicorn', 'fastapi',
    'llama_cpp_binaries', 'pywebview', 'PyQt5',
    'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets'
]
for package in submodule_packages:
    try:
        hiddenimports += collect_submodules(package)
    except Exception:
        pass

# === MAIN SCRIPT ===
server_script = os.path.abspath(os.path.join(script_dir, "server.py"))

a = Analysis(
    [server_script],
    pathex=[script_dir],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['pyi_rth_create_dirs.py'],
    excludes=['tkinter', 'PyQt6', 'PySide2', 'PySide6', 'wx', 'sentry_sdk', 'asyncio.windows_utils', 'trio'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

a.hiddenimports = list(set(a.hiddenimports))

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='textui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=['torch*.dll', 'cuda*.dll', 'cudnn*.dll', 'python*.dll'],
    runtime_tmpdir=os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'textui_runtime'),
    console=True,  # Set to False for no console window
    onefile=True,  # Single EXE for sharing (change to False for onedir if build fails/slow)
)