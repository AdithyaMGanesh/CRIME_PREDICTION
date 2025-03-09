import pandas as pd

# Load the cleaned dataset
df = pd.read_csv("cleaned_crime_data.csv")

# Rename columns to be Oracle-friendly (<= 30 chars)
new_column_names = {
    "state/ut": "state_ut",
    "culpable_homicide_not_amounting_to_murder": "culpable_homicide",
    "kidnapping_&_abduction": "kidnap_abduction",
    "kidnapping_and_abduction_of_women_and_girls": "kidnap_women_girls",
    "kidnapping_and_abduction_of_others": "kidnap_others",
    "preparation_and_assembly_for_dacoity": "prep_dacoity",
    "hurt/grevious_hurt": "grievous_hurt",
    "assault_on_women_with_intent_to_outrage_her_modesty": "assault_women",
    "cruelty_by_husband_or_his_relatives": "cruelty_by_husband",
    "importation_of_girls_from_foreign_countries": "import_girls_foreign",
    "causing_death_by_negligence": "death_by_negligence"
}

# Apply renaming
df.rename(columns=new_column_names, inplace=True)

# Save the modified CSV
df.to_csv("final_cleaned_crime_data.csv", index=False)

print("✅ Column names updated and saved as 'final_cleaned_crime_data.csv'")
