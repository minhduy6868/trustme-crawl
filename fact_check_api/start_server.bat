@echo off
REM Start Article Analyze API Server
echo ============================================================
echo    Article Analyze API Server
echo ============================================================
echo.

cd /d "%~dp0"

echo Starting server on http://localhost:8001...
echo Docs: http://localhost:8001/docs
echo.
echo Press Ctrl+C to stop
echo.

C:\Users\ACER\AppData\Local\Programs\Python\Python311\python.exe api_server.py

pause
