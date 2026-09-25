@echo off
title MDTPS - Database and ML Model Setup
echo =====================================================================
echo  MDTPS - Resetting Database and Retraining ML Classifier
echo =====================================================================
echo.

if exist venv\Scripts\python.exe (
    echo [1/3] Generating realistic sample data...
    venv\Scripts\python.exe scripts\generate_sample_data.py
    echo [2/3] Seeding database schema and records...
    venv\Scripts\python.exe -c "from app.seed import seed_all; print(seed_all())"
    echo [3/3] Training Decision Tree defect classifier...
    venv\Scripts\python.exe ml\train_model.py
) else (
    echo [1/3] Generating realistic sample data...
    python scripts\generate_sample_data.py
    echo [2/3] Seeding database schema and records...
    python -c "from app.seed import seed_all; print(seed_all())"
    echo [3/3] Training Decision Tree defect classifier...
    python ml\train_model.py
)

echo.
echo =====================================================================
echo  Setup Complete! You can now run run.bat to start the system.
echo =====================================================================
pause
