@echo off
REM Microsoft Store Icon Generator - Windows Launcher

echo Checking and installing dependencies...
python -m pip install --upgrade pip
python -m pip install -q -r requirements.txt

echo.
echo Starting Microsoft Store Icon Generator...
python icon_generator.py

pause
