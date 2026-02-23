@echo off
REM ============================================================
REM Emergency Prediction System - Data Download Script (Windows)
REM ============================================================
REM Requirements:
REM   1. Python + Kaggle CLI:  pip install kaggle
REM   2. Kaggle API key placed at:  C:\Users\<YourName>\.kaggle\kaggle.json
REM      Get your key from: https://www.kaggle.com/settings (Account -> API)
REM ============================================================

echo Downloading Emergency Dataset...

set DATA_DIR=data
if not exist "%DATA_DIR%" mkdir "%DATA_DIR%"

REM 911 Calls (the only dataset used by train_model.py)
REM Source: https://www.kaggle.com/datasets/mchirico/montcoalert
if not exist "%DATA_DIR%\911.csv" (
    echo Downloading 911 Calls dataset...
    kaggle datasets download -d mchirico/montcoalert -p %DATA_DIR% --unzip
    if %errorlevel% neq 0 (
        echo ERROR: Download failed. Check your Kaggle API key and internet connection.
        exit /b 1
    )
) else (
    echo 911.csv already exists. Skipping download.
)

echo.
echo Data download complete. Files are in the "%DATA_DIR%" directory.
