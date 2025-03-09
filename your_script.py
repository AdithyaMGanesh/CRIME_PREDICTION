import pandas as pd

# Load the dataset
df = pd.read_csv("crime_data.csv")  # Ensure the file is in the same directory

# Display the first few rows
print("✅ Original Dataset:")
print(df.head())

# Handle missing values (if any)
df.fillna(method='ffill', inplace=True)

# Convert column names to lowercase & remove spaces
df.columns = df.columns.str.lower().str.replace(" ", "_")

# Convert date columns to datetime format (modify based on dataset)
if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'])

# Drop duplicates
df.drop_duplicates(inplace=True)

# Display cleaned dataset
print("\n✅ Preprocessed Dataset:")
print(df.head())

# Save the cleaned dataset
df.to_csv("cleaned_crime_data.csv", index=False)

print("\n✅ Preprocessed data saved as 'cleaned_crime_data.csv'")
