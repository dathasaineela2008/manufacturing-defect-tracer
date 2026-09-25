@echo off
title MDTPS - Manufacturing Defect Traceability and Prediction System
echo =====================================================================
echo  MDTPS - Manufacturing Defect Traceability and Prediction System
echo =====================================================================
echo.
echo Starting Flask web server at http://127.0.0.1:5000 ...
echo Demo Account: admin / Admin@123
echo Press Ctrl+C in this window to stop the server.
echo.

if exist venv\Scripts\python.exe (
    venv\Scripts\python.exe run.py
) else (
    python run.py
)
pause
