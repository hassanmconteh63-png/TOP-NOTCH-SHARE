@echo off
cd /d "%~dp0"
py -3 top_notch_share_server.py
if errorlevel 1 (
  echo.
  echo Could not start. Check that Python 3 is installed and available with the "py" command.
  pause
)
pause
