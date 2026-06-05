; BookFix Installer Script for Inno Setup
; Build: ISCC.exe installer.iss
; NOTE: This file is processed from the build_stage directory.
;        All paths are relative to that directory.

#define MyAppName "BookFix"
#define MyAppVersion "2.0.0"
#define MyAppPublisher "BookFix Project"

[Setup]
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={localappdata}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=.\output
OutputBaseFilename=BookFix-Setup-{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\python\pythonw.exe
PrivilegesRequired=lowest
AllowCancelDuringInstall=False

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
Source: "main.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "launcher.pyw"; DestDir: "{app}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "bookfix\*"; DestDir: "{app}\bookfix"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "data\*"; DestDir: "{app}\data"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "prompts\*"; DestDir: "{app}\prompts"; Flags: ignoreversion recursesubdirs createallsubdirs
; Bundled Python embeddable (configured for pip)
Source: "python\*"; DestDir: "{app}\python"; Flags: ignoreversion recursesubdirs createallsubdirs


[Icons]
Name: "{group}\{#MyAppName}"; \
  Filename: "{app}\python\python.exe"; \
  Parameters: """{app}\launcher.pyw"""; \
  WorkingDir: "{app}"; \
  IconFilename: "{app}\python\python.exe"; \
  Comment: "Ebook Text Processor for TTS Preparation"
Name: "{userdesktop}\{#MyAppName}"; \
  Filename: "{app}\python\python.exe"; \
  Parameters: """{app}\launcher.pyw"""; \
  WorkingDir: "{app}"; \
  IconFilename: "{app}\python\python.exe"; \
  Tasks: desktopicon; \
  Comment: "Ebook Text Processor for TTS Preparation"

[Run]
Filename: "{app}\python\python.exe"; \
  Parameters: """{app}\launcher.pyw"""; \
  WorkingDir: "{app}"; \
  Description: "Launch {#MyAppName}"; \
  Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
Type: dirifempty; Name: "{localappdata}\{#MyAppName}"
