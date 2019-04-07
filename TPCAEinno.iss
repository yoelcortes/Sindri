; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{AE889C70-CE01-4AB1-8A95-C510F8415553}
AppName=TPCAE
AppVersion=1.0
;AppVerName=TPCAE 1.0
AppPublisher=Marcus Bruno
AppPublisherURL=www.github.com/mrcsbrn
AppSupportURL=www.github.com/mrcsbrn
AppUpdatesURL=www.github.com/mrcsbrn
DefaultDirName={pf}\TPCAE
DisableProgramGroupPage=yes
OutputBaseFilename=TPCAE_setup
Compression=lzma
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Dirs]
Name: {app}; Permissions: users-full

[Files]
Source: ".\TPCAE\TPCAE.exe"; DestDir: "{app}"; Flags: ignoreversion;  Permissions: everyone-full
Source: ".\TPCAE\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Permissions: everyone-full
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{commonprograms}\TPCAE"; Filename: "{app}\TPCAE.exe"
Name: "{commondesktop}\TPCAE"; Filename: "{app}\TPCAE.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\TPCAE.exe"; Description: "{cm:LaunchProgram,TPCAE}"; Flags: nowait postinstall skipifsilent

