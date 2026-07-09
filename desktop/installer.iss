; Biznex POS — Inno Setup skripti
; O'rnatuvchi (Setup.exe) yaratish uchun: avval build.bat orqali BiznexPOS.exe yig'ing,
; keyin bu faylni Inno Setup Compiler (http://jrsoftware.org/isinfo.php, bepul) bilan oching va Compile bosing.

#define MyAppName "Biznex POS"
#define MyAppVersion "1.0"
#define MyAppExeName "BiznexPOS.exe"

[Setup]
AppId={{B1ZN3X-P0S-2026-DESKTOP-APP}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\BiznexPOS
DefaultGroupName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
OutputBaseFilename=BiznexPOS-Setup
OutputDir=dist_installer
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\config.json"; DestDir: "{app}"; Flags: onlyifdoesntexist uninsneveruninstall

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{group}\{#MyAppName}ni o'chirish"; Filename: "{uninstallexe}"

[Tasks]
Name: "desktopicon"; Description: "Ish stolida yorliq yaratish"; GroupDescription: "Qo'shimcha:"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Biznex POS'ni ishga tushirish"; Flags: nowait postinstall skipifsilent
