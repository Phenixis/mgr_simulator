@echo off
set SCRIPT_PATH=%~dp0install-pyenv.ps1

powershell -ExecutionPolicy Bypass -File "%SCRIPT_PATH%"

pause

pyenv install 3.11.9
pyenv local 3.11.9