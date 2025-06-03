venv\Scripts\activate.bat

pyinstaller --onefile main.py --add-data "venv\Lib\site-packages\snap7;.\snap7" --add-data "img/*;img"
move dist\main.exe .\main.exe