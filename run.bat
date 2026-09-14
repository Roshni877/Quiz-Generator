@echo off
REM Run the Flask app in a new window and open the browser
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    start "Quiz Server" .venv\Scripts\python.exe app.py
) else (
    start "Quiz Server" python app.py
)
REM Wait a moment for the server to start
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:5000"
exit

