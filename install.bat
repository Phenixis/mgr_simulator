@echo off
set SCRIPT_PATH=%~dp0install-pyenv.ps1

powershell -ExecutionPolicy Bypass -File "%SCRIPT_PATH%"

pause

pyenv install 3.11.9
pyenv local 3.11.9

%USERPROFILE%\.pyenv\pyenv-win\versions\3.11.9\python.exe -m venv venv
venv\Scripts\activate.bat

pip install -r requirements.txt

pyinstaller --onefile main.py --add-data "venv\Lib\site-packages\snap7;.\snap7" --add-data "img/*;img"
move dist\main.exe .\main.exe

main.exe