@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0ffprobe.ps1" %*
exit /b %ERRORLEVEL%
