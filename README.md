# TextUI (Windows) – Build, Packaging aur Installer Guide

Yeh README next dev ke liye full reference hai: project overview, build steps, PyInstaller packaging, Inno Setup installer, and saare issues + solutions with exact PowerShell commands. Commands PowerShell (pwsh) ke hisaab se diye gaye hain.

## 1) Overview
- App: Python + Gradio UI wrapped in a pywebview desktop shell
- Entry point: webview_app.py
- Important runtime folders: css, js, extensions, user_data (models download yahin aate hain)
- Windows-only packaged build using PyInstaller (onedir)
- Installer: Inno Setup (includes WebView2 runtime check + auto-install)

App run karta hai local HTTP server (default 7860) aur pywebview isko native window me open karta hai. Installer user system pe sab files copy karta hai, WebView2 runtime check karta hai, aur shortcuts bana deta hai.

## 2) Environment Details
- OS: Windows
- Shell: PowerShell 5.1
- Suggested Python: 3.10+ (current environment me 3.13 bhi chal raha hai, but test karo)
- WebView2 Runtime: Required (installer se auto-install ho jayega)

## 3) Repository Structure (important parts)
- webview_app.py – Main launcher (pywebview + gradio)
- modules/ – App modules (UI, loaders, etc.)
- extensions/ – Optional extension scripts
- css/, js/ – Frontend static assets
- user_data/ – Runtime data (models, characters, etc.). Installer in subfolders create karta hai.
- download_model.py – HF models download utility (packaging me data ke roop me include hota hai)
- modules/ui_model_menu.py – Model download UI + logic (yahin par download_model import fallback implemented hai)
- installer.iss – Inno Setup script (installer banane ke liye)
- installer_assets/MicrosoftEdgeWebView2Setup.exe – WebView2 bootstrapper (aapko yeh file rakhni hoti hai)

Note: PyInstaller onedir build data files ko _internal/ ke andar place karta hai by design.

## 4) Quick Start – Dev Setup aur Run (source se)
1) Virtualenv banao aur activate karo:
```powershell path=null start=null
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

2) Dependencies install karo (minimal example – aap apne project ki needs ke hisaab se add/remove kar sakte ho):
```powershell path=null start=null
pip install pywebview gradio requests tqdm huggingface_hub
```

3) App ko directly run karke test karo:
```powershell path=null start=null
python webview_app.py
```

Localhost:7860 pe server run hoga aur pywebview window open hogi. Firewall prompt aaye to allow kar dena.

## 5) Build (PyInstaller onedir)
Clean build banaane ke liye recommended flags (Hinglish comments ke saath):
```powershell path=null start=null
# In case PyInstaller missing ho
pip install pyinstaller

# Clean previous build
Remove-Item -Recurse -Force .\build -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force .\dist -ErrorAction SilentlyContinue

# IMPORTANT: Windows me --add-data separator ; hota hai
# Gradio / gradio_client ka saara package data include karne ke liye --collect-all
# Static + runtime folders copy karne ke liye --add-data
# download_model ke import ke liye fallback + packaging friendly setup: hidden-import + add-data
pyinstaller `
  --noconfirm `
  --onedir `
  --clean `
  --name webview_app `
  --collect-all gradio `
  --collect-all gradio_client `
  --add-data "css;css" `
  --add-data "js;js" `
  --add-data "extensions;extensions" `
  --add-data "user_data;user_data" `
  --hidden-import download_model `
  --add-data "download_model.py;download_model.py" `
  webview_app.py
```

Notes:
- PyInstaller data files by default onedir me "_internal" ke under aate hain. Example: dist\webview_app\_internal\download_model.py\download_model.py
- Humne modules/ui_model_menu.py me robust fallback import logic dala hua hai jo _MEIPASS aur _internal paths me download_model.py ko dhund leta hai. Isliye current layout me import theek chalega.
- Agar future me download_model.py ko modules/ ke andar module bana ke shift karna ho, to fallback hata sakte ho aur --add-data/--hidden-import ki zarurat nahi padegi (Recommended long-term refactor).

Optional (UPX compression, agar installed ho):
```powershell path=null start=null
# Example only if UPX installed and on PATH
pyinstaller `
  --noconfirm --onedir --clean --name webview_app `
  --collect-all gradio --collect-all gradio_client `
  --add-data "css;css" --add-data "js;js" --add-data "extensions;extensions" --add-data "user_data;user_data" `
  --hidden-import download_model --add-data "download_model.py;download_model.py" `
  --upx-dir "C:\\Path\\To\\upx" `
  webview_app.py
```

After build, sanity-check required runtime folders (kabhi-kabhi empty dirs PyInstaller se skip ho jaati hain):
```powershell path=null start=null
New-Item -ItemType Directory -Force -Path .\dist\webview_app\_internal\user_data\models | Out-Null
New-Item -ItemType Directory -Force -Path .\dist\webview_app\_internal\user_data\characters | Out-Null
```

Run EXE locally to test:
```powershell path=null start=null
.\dist\webview_app\webview_app.exe
```

## 6) Build the Windows Installer (Inno Setup)
Prerequisites:
- Inno Setup installed (ISCC.exe typical path):
  - C:\Program Files (x86)\Inno Setup 6\ISCC.exe
  - or C:\Program Files\Inno Setup 6\ISCC.exe
- WebView2 bootstrapper ko yahan rakho: installer_assets\MicrosoftEdgeWebView2Setup.exe

Build installer:
```powershell path=null start=null
# Generate Setup.exe
$project = "C:\\Users\\Administrator\\stevesailab\\Text_generation"
$iss = Join-Path $project "installer.iss"
$ISCC = "C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe"
if (-not (Test-Path $ISCC)) { $ISCC = "C:\\Program Files\\Inno Setup 6\\ISCC.exe" }
& $ISCC $iss
```

- Output default: installer_output\setup.exe
- Installer features:
  - dist\webview_app ko {app} me copy karta hai
  - {app}\user_data\..., {app}\user_data\models create karta hai
  - WebView2 Runtime check + auto-install (silent)
  - Per-user Desktop shortcut (no admin required to create)
  - Post-install app launch option

## 7) Common Problems & Solutions (Humne face kiye aur fix kiye)
1) PyInstaller command not found
   - Error: "pyinstaller is not recognized..."
   - Fix:
```powershell path=null start=null
pip install pyinstaller
```

2) Missing packages at runtime (e.g., pywebview)
   - Error: ModuleNotFoundError: No module named 'pywebview'
   - Fix:
```powershell path=null start=null
pip install pywebview
```

3) Gradio/Gradio Client ke resources missing (types.json, blocks_events.py, etc.)
   - Symptom: Runtime me internal data files not found
   - Fix: PyInstaller me package data include karo
```powershell path=null start=null
--collect-all gradio --collect-all gradio_client
```

4) user_data subfolders missing (e.g., user_data/models)
   - Symptom: App crash ya write failures on first run
   - Fix: Build ke baad folders create karo (aur installer.iss me [Dirs] bhi create karta hai)
```powershell path=null start=null
New-Item -ItemType Directory -Force -Path .\dist\webview_app\_internal\user_data\models | Out-Null
```

5) ModuleNotFoundError: No module named 'download-model'
   - Root cause: Import typo "download-model" vs filename "download_model.py"
   - Fixes implemented:
     - Code import corrected to download_model
     - Robust fallback import in modules/ui_model_menu.py jo _MEIPASS/_internal paths me download_model.py locate karta hai
     - Build flags add kiye:
```powershell path=null start=null
--hidden-import download_model --add-data "download_model.py;download_model.py"
```
   - Note: PyInstaller data files _internal me aate hain, expected path:
     dist\webview_app\_internal\download_model.py\download_model.py

6) WebView2 Runtime missing on user machine
   - Fix: Installer ships bootstrapper and silently installs if not present
   - Developer tip: Debug ke liye WebView2 evergreen runtime install karke rakh sakte ho

7) Desktop shortcut permission issues
   - Fix: Installer per-user desktop pe shortcut banata hai (no admin elevation needed)

8) Firewall prompt / Port in use
   - Symptom: First run pe Windows firewall prompt – allow kar do
   - Agar 7860 port busy ho to app config me alternate port set karo (code/args side change)

## 8) How to Use (End User + Dev)
- From installer:
  - Run setup.exe, WebView2 install ho jayega agar missing ho
  - App launch hogi aur models ke downloads UI se trigger kar sakte ho

- From packaged EXE:
```powershell path=null start=null
.\dist\webview_app\webview_app.exe
```

- From source (dev mode):
```powershell path=null start=null
.\.venv\Scripts\Activate.ps1
python webview_app.py
```

- Models download (UI):
  - "Model" tab me "Download" sub-tab
  - Popular models dropdown se select karo ya custom repo_id enter karo (e.g., TheBloke/phi-2-GGUF)
  - GGUF file name specify kar sakte ho agar multiple ho; UI suggest bhi kar dega

- Models storage location:
  - Installer build me models default: {app}\user_data\models (on Windows Program Files under app dir)
  - Source/dev mode me: project tree ke user_data\models

## 9) Release Checklist
- [ ] webview_app.py runs fine locally (source and EXE)
- [ ] PyInstaller build successful, EXE opens pywebview, server reachable
- [ ] user_data subfolders present post-build
- [ ] installer_assets\MicrosoftEdgeWebView2Setup.exe present
- [ ] ISCC build successful; setup.exe generated in installer_output
- [ ] Clean VM pe install test: app launches, model download works
- [ ] Update version in installer.iss before release: `#define MyAppVersion "X.Y.Z"`

## 10) Future Improvements (Optional)
- download_model.py ko modules/ me shift karke proper importable module bana do; phir fallback aur extra flags ki zarurat nahi padegi
- user_data ko %LOCALAPPDATA% me move karna for cleaner per-user writes (Program Files write restrictions avoid karne ke liye)
- Build script (PowerShell) add karke single-command build + install automation

## 11) Contact / Ownership
- Publisher: stevesailab
- Maintainers: Add your team info here

Happy building! Agar koi error logs milte hain, exact traceback paste karo – uske basis pe PyInstaller flags (hidden-imports/add-data) aur hooks update kar denge.


## 12) llama.cpp binaries (GPU/CPU) and updated build commands

llama_cpp_binaries package app ke llama.cpp server binaries provide karta hai (including llama-server.exe). Isko install karna zaroori hai jab aap GGUF models ko "llama.cpp" loader ke through chalana chahoge.

Choose ONE of the two options below (GPU vs CPU):

- GPU (CUDA 12.4) build:
```powershell path=null start=null
python -m pip install "https://github.com/oobabooga/llama-cpp-binaries/releases/download/v0.42.0/llama_cpp_binaries-0.42.0+cu124-py3-none-win_amd64.whl"
```

- CPU-only build:
```powershell path=null start=null
python -m pip install "https://github.com/oobabooga/llama-cpp-binaries/releases/download/v0.42.0/llama_cpp_binaries-0.42.0+cpu-py3-none-win_amd64.whl"
```

Updated PyInstaller command (include llama_cpp_binaries):
```powershell path=null start=null
pyinstaller `
  --noconfirm `
  --onedir `
  --clean `
  --name webview_app `
  --collect-all gradio `
  --collect-all gradio_client `
  --collect-all llama_cpp_binaries `
  --add-data "css;css" `
  --add-data "js;js" `
  --add-data "extensions;extensions" `
  --add-data "user_data;user_data" `
  --hidden-import download_model `
  --add-data "download_model.py;download_model.py" `
  webview_app.py
```

Troubleshooting:
- Agar error aata hai like "ModuleNotFoundError: No module named 'llama_cpp_binaries'", pehle upar wala wheel install karo aur phir rebuild karo.
- Agar Windows pe nvcuda.dll ya cudart*.dll missing waali errors aayein, iska matlab CUDA runtime nahi mil raha:
  - CPU-only wheel (upar) install karo, phir dubara PyInstaller build chalao.
- Packaging ke baad, EXE runtime me server path resolve ho jayega (modules/llama_cpp_server.py uses llama_cpp_binaries.get_binary_path()).
