#define MyAppName        "TextUI"
#define MyAppVersion     "1.0.0"
#define MyAppPublisher   "stevesailab"
#define MyAppExeName     "webview_app.exe"

// Location of the built app (PyInstaller onedir output)
#define SourceBase "C:\\Users\\Administrator\\stevesailab\\Text_generation\\dist\\webview_app"

// WebView2 bootstrapper shipped with installer (download it and keep here)
#define WebView2Bootstrapper "C:\\Users\\Administrator\\stevesailab\\Text_generation\\installer_assets\\MicrosoftEdgeWebView2Setup.exe"

// Where to place the generated setup.exe
#define OutputDir "C:\\Users\\Administrator\\stevesailab\\Text_generation\\installer_output"

[Setup]
AppId={{8F2B5E2A-8E2F-4F39-9C1B-7F7B6B2C9B21}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableDirPage=no
DisableProgramGroupPage=yes
OutputBaseFilename=setup
OutputDir={#OutputDir}
ArchitecturesInstallIn64BitMode=x64
Compression=lzma2/ultra
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
DisableReadyMemo=no
UninstallDisplayIcon={app}\\{#MyAppExeName}
SetupLogging=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &Desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Dirs]
Name: "{app}\user_data"; Flags: uninsalwaysuninstall
Name: "{app}\user_data\characters"; Flags: uninsalwaysuninstall
Name: "{app}\user_data\models"; Flags: uninsalwaysuninstall

[Files]
; App bundle (PyInstaller onedir output)
Source: "{#SourceBase}\\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion; Excludes: "__pycache__\\*;*.pyc;*.pdb;*.log;*.md;tests\\*;*.dist-info\\*;*.egg-info\\*"

; WebView2 bootstrapper (delete after install)
Source: "{#WebView2Bootstrapper}"; DestDir: "{tmp}"; Flags: deleteafterinstall; Check: NeedsWebView2

[Icons]
Name: "{group}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"; WorkingDir: "{app}"
; Use per-user desktop to avoid elevation requirement
Name: "{userdesktop}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"; Tasks: desktopicon; WorkingDir: "{app}"

[Run]
; Install WebView2 if missing
Filename: "{tmp}\\MicrosoftEdgeWebView2Setup.exe"; Parameters: "/install /silent /norestart"; StatusMsg: "Installing Microsoft Edge WebView2 Runtime..."; Flags: runhidden; Check: NeedsWebView2

; Launch app post-install
Filename: "{app}\\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent; WorkingDir: "{app}"

[Code]
function WebView2VersionInstalled(RootKey: Integer): String;
begin
  Result := '';
  if not RegQueryStringValue(RootKey, 'Software\\Microsoft\\EdgeWebView\\BLBeacon', 'version', Result) then
  begin
    RegQueryStringValue(RootKey, 'Software\\WOW6432Node\\Microsoft\\EdgeWebView\\BLBeacon', 'version', Result);
  end;
end;

function NeedsWebView2: Boolean;
var
  Ver: String;
begin
  Ver := WebView2VersionInstalled(HKCU);
  if Ver = '' then
    Ver := WebView2VersionInstalled(HKLM);
  Result := (Ver = '');
end;
