# Windows Model Training Guide 


## Prerequisites

1.  **Python Installed**: Ensure Python 3.9+ is installed on your Windows machine.
2.  **Dataset Availability**: Ensure that `data/911.csv` (or `sample_911.csv`) is downloaded and placed in the correct `data/` folder directory relative to this script.

## Step 1: Transfer the code
You can sync your `model/advanced-development` branch to your PC via Git:
```cmd
git checkout -b model/advanced-development
git pull origin model/advanced-development
```

## Step 2: Install Required Libraries
Open your Command Prompt (`cmd`) or PowerShell inside your repository's root directory. Run the following command to install everything listed in your `requirements.txt`:
```cmd
pip install -r requirements.txt
```
*(Note: XGBoost installs beautifully on Windows because it ships with pre-compiled binaries. No extra C++ tools required!)*

## Step 3: Train the Model
Navigate to the `notebook/` folder (or run it from the root):
```cmd
python notebook/train_model.py
```

### What to expect:
1.  **Preprocessing & Engineering**: The script will read the data and start creating the spatial/time features.
2.  **K-Fold & Grid Search**: The script will begin training using K-Fold Validation. It will run dozens of combinations of parameters. **This can take several minutes** depending on your CPU speed.
3.  **Output**: Once finished, it will print out the best algorithm parameters found and the model's final `RMSE` and `R2 Score`. 
4.  **Export**: The winning model will be saved as **`model/best_advanced_model.pkl`**.

## Final Step 
After the `.pkl` file generates on your Windows PC, you can commit it back to your branch or upload it straight to your cloud storage! 
```cmd
git add model/best_advanced_model.pkl
git commit -m "Add trained XGBoost model"
git push origin model/advanced-development
```
