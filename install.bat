@echo off
setlocal

set "SRC=%~dp0lazypush.exe"
set "DEST=%LOCALAPPDATA%\Programs\lazypush"

if not exist "%SRC%" (
    echo [Error] lazypush.exe must be in the same folder as install.bat.
    pause
    exit /b 1
)

if not exist "%DEST%" mkdir "%DEST%"
copy /Y "%SRC%" "%DEST%\lazypush.exe" >nul
if errorlevel 1 (
    echo [Error] Could not copy lazypush.exe. Close any terminal using it and try again.
    pause
    exit /b 1
)

rem Add the install folder to the USER Path (no admin needed, skipped if already there).
rem Keeps %VARIABLES% in your other Path entries intact.
set "PS=$d = Join-Path $env:LOCALAPPDATA 'Programs\lazypush';"
set "PS=%PS% $k = [Microsoft.Win32.Registry]::CurrentUser.OpenSubKey('Environment', $true);"
set "PS=%PS% $p = [string]$k.GetValue('Path', '', 'DoNotExpandEnvironmentNames');"
set "PS=%PS% $parts = @($p -split ';' | Where-Object { $_ -ne '' });"
set "PS=%PS% if ($parts -notcontains $d) { $k.SetValue('Path', (($parts + $d) -join ';'), 'ExpandString') };"
set "PS=%PS% $k.Close();"
rem Setting and clearing a dummy variable makes Windows broadcast the change to new terminals.
set "PS=%PS% [Environment]::SetEnvironmentVariable('LAZYPUSH_REFRESH', '1', 'User');"
set "PS=%PS% [Environment]::SetEnvironmentVariable('LAZYPUSH_REFRESH', $null, 'User')"
powershell -NoProfile -Command "%PS%"
if errorlevel 1 (
    echo [Error] Could not update PATH.
    pause
    exit /b 1
)

echo.
echo Installed to %DEST%
echo Close this window, open a NEW terminal, then run:  lazypush
pause