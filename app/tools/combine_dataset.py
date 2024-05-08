import pandas as pd
from pprint import pprint
from services.constants import COMBINED_DATASET, LEGAL_DATASET, LEGAL_URLS, LEGAL_URLS_CSV, OUTPUT_FEATURES_PATH


if __name__ == "__main__":
    phishing_data = pd.read_csv(OUTPUT_FEATURES_PATH)
    legal_data = pd.read_csv(LEGAL_URLS_CSV)

    phishing_data['phishing'] = 1 
    legal_data['phishing'] = 0

    # Concatenate the two DataFrames
    combined_data = pd.concat([phishing_data, legal_data], ignore_index=True)

    # Optionally, shuffle the combined DataFrame if needed
    combined_data = combined_data.sample(frac=1).reset_index(drop=True)

    # Save the combined DataFrame to a new CSV file
    combined_data.to_csv(COMBINED_DATASET, index=False)

    print("Combined data saved to 'combined_data.csv'.")
