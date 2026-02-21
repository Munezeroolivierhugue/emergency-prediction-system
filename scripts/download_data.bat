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

REM 1. 911 Calls
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

REM 2. US Accidents (March 2023)
REM Source: https://www.kaggle.com/datasets/sobhanmoosavi/us-accidents
if not exist "%DATA_DIR%\US_Accidents_March23.csv" (
    echo Downloading US Accidents dataset...
    kaggle datasets download -d sobhanmoosavi/us-accidents -p %DATA_DIR% --unzip
    if %errorlevel% neq 0 (
        echo ERROR: Download failed. Check your Kaggle API key and internet connection.
        exit /b 1
    )
) else (
    echo US_Accidents_March23.csv already exists. Skipping download.
)

echo.
echo Data download complete. Files are in the "%DATA_DIR%" directory.
