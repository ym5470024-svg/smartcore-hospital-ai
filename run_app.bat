@echo off
setlocal

set PYTHON_CMD=python
where python >nul 2>nul
if errorlevel 1 (
    echo Python was not found in PATH.
    exit /b 1
)

if not exist .venv (
    echo Creating virtual environment...
    %PYTHON_CMD% -m venv .venv
)

call .venv\Scripts\activate
python -m pip install --upgrade pip >nul
python -m pip install -r requirements.txt >nul

start "SmartCore API" cmd /k "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
rem Wait a moment for the API to start.
timeout /t 3 >nul
start "SmartCore Dashboard" cmd /k "streamlit run dashboard/app.py --server.address 0.0.0.0 --server.port 8501"

echo.
echo Smart Core Hospital Intelligence started.
echo API: http://localhost:8000/docs

echo Dashboard: http://localhost:8501

echo Press Ctrl+C in each console window to stop the services.
