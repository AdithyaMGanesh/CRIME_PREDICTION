import cx_Oracle
import pandas as pd

# ✅ Connect to Oracle
dsn_tns = cx_Oracle.makedsn("localhost", 1521, service_name="XE")  
username = "system"
password = "adithya123"

conn = cx_Oracle.connect(user=username, password=password, dsn=dsn_tns)
cursor = conn.cursor()

# ✅ Load the cleaned dataset
df = pd.read_csv("cleaned_crime_data.csv")

# ✅ Column mapping (Shortened column names for Oracle)
columns = {
    "state/ut": "state_ut",
    "district": "district",
    "year": "year",
    "murder": "murder",
    "attempt_to_murder": "attempt_to_murder",
    "culpable_homicide_not_amounting_to_murder": "culpable_homicide",
    "rape": "rape",
    "custodial_rape": "custodial_rape",
    "other_rape": "other_rape",
    "kidnapping_&_abduction": "kidnap_abduction",
    "kidnapping_and_abduction_of_women_and_girls": "kidnap_women_girls",
    "kidnapping_and_abduction_of_others": "kidnap_others",
    "dacoity": "dacoity",
    "preparation_and_assembly_for_dacoity": "prep_dacoity",
    "robbery": "robbery",
    "burglary": "burglary",
    "theft": "theft",
    "auto_theft": "auto_theft",
    "other_theft": "other_theft",
    "riots": "riots",
    "criminal_breach_of_trust": "criminal_breach_trust",
    "cheating": "cheating",
    "counterfieting": "counterfeiting",
    "arson": "arson",
    "hurt/grevious_hurt": "grievous_hurt",
    "dowry_deaths": "dowry_deaths",
    "assault_on_women_with_intent_to_outrage_her_modesty": "assault_women",
    "insult_to_modesty_of_women": "insult_modesty_women",
    "cruelty_by_husband_or_his_relatives": "cruelty_by_husband",
    "importation_of_girls_from_foreign_countries": "import_girls_foreign",
    "causing_death_by_negligence": "death_by_negligence",
    "other_ipc_crimes": "other_ipc_crimes",
    "total_ipc_crimes": "total_ipc_crimes"
}

# ✅ Prepare INSERT query
query = f"""
    INSERT INTO crime_data ({', '.join(columns.values())})
    VALUES ({', '.join([':' + str(i) for i in range(1, len(columns) + 1)])})
"""

# ✅ Insert data row by row
for _, row in df.iterrows():
    cursor.execute(query, tuple(row[original_col] for original_col in columns.keys()))

# ✅ Commit and close connection
conn.commit()
cursor.close()
conn.close()

print("✅ Data inserted into Oracle Database successfully!")
