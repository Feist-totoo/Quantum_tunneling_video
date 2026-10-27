@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0ffmpeg.ps1" %*
exit /b %ERRORLEVEL%
