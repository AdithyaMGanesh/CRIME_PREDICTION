import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import pickle
import math

# Step 1: Load the preprocessed data
df = pd.read_csv("final_cleaned_crime_data.csv")

# Print the available columns for verification
print("Columns in dataset:", df.columns.tolist())

# Step 2: Set the target variable.
target_column = "total_ipc_crimes"

# Check if the target column exists
if target_column not in df.columns:
    raise KeyError(f"Target column '{target_column}' not found. Available columns: {df.columns.tolist()}")

# Step 3: Separate features and target variable
X = df.drop(target_column, axis=1)
y = df[target_column]

# Step 4: Encode categorical features
# Convert 'state_ut' and 'district' into numerical values using one-hot encoding
categorical_columns = ['state_ut', 'district']
X = pd.get_dummies(X, columns=categorical_columns, drop_first=True)

# Step 5: Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 6: Train a RandomForestRegressor
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Step 7: Evaluate model performance using R² and RMSE
train_predictions = model.predict(X_train)
test_predictions = model.predict(X_test)

train_r2 = r2_score(y_train, train_predictions)
test_r2 = r2_score(y_test, test_predictions)
train_rmse = math.sqrt(mean_squared_error(y_train, train_predictions))
test_rmse = math.sqrt(mean_squared_error(y_test, test_predictions))

print(f"Training R²: {train_r2:.2f}")
print(f"Testing R²: {test_r2:.2f}")
print(f"Training RMSE: {train_rmse:.2f}")
print(f"Testing RMSE: {test_rmse:.2f}")

# Step 8: Save the trained model to a file for later use
with open("crime_model.pkl", "wb") as f:
    pickle.dump(model, f)
print("Model saved as crime_model.pkl")
