@echo off
setlocal

set "DEST=%LOCALAPPDATA%\Programs\lazypush"

set "PS=$d = Join-Path $env:LOCALAPPDATA 'Programs\lazypush';"
set "PS=%PS% $k = [Microsoft.Win32.Registry]::CurrentUser.OpenSubKey('Environment', $true);"
set "PS=%PS% $p = [string]$k.GetValue('Path', '', 'DoNotExpandEnvironmentNames');"
set "PS=%PS% $parts = @($p -split ';' | Where-Object { $_ -ne '' -and $_ -ne $d });"
set "PS=%PS% $k.SetValue('Path', ($parts -join ';'), 'ExpandString');"
set "PS=%PS% $k.Close();"
set "PS=%PS% [Environment]::SetEnvironmentVariable('LAZYPUSH_REFRESH', '1', 'User');"
set "PS=%PS% [Environment]::SetEnvironmentVariable('LAZYPUSH_REFRESH', $null, 'User')"
powershell -NoProfile -Command "%PS%"

if exist "%DEST%" rmdir /s /q "%DEST%"

echo.
echo lazypush was removed. Open a new terminal to refresh PATH.
pause