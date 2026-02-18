#!/bin/bash

# Emergency Prediction System - Data Download Script

echo "Downloading Emergency Dataset..."
echo "NOTE: This script assumes you have the Kaggle CLI installed and configured."
echo "If not, please download the datasets manually from the links below."

DATA_DIR="data"
mkdir -p $DATA_DIR

# 1. US Accidents (March 2023)
# Source: https://www.kaggle.com/datasets/sobhanmoosavi/us-accidents
if [ ! -f "$DATA_DIR/US_Accidents_March23.csv" ]; then
    echo "Downloading US Accidents dataset..."
    kaggle datasets download -d sobhanmoosavi/us-accidents -p $DATA_DIR --unzip
else
    echo "US_Accidents_March23.csv already exists."
fi

# 2. 911 Calls
# Source: https://www.kaggle.com/datasets/mchirico/montcoalert
if [ ! -f "$DATA_DIR/911.csv" ]; then
    echo "Downloading 911 Calls dataset..."
    kaggle datasets download -d mchirico/montcoalert -p $DATA_DIR --unzip
else
    echo "911.csv already exists."
fi

echo "Data download complete."
