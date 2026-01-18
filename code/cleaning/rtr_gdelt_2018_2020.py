"""
Purpose:
This script loads raw Reuters–GDELT data covering 2018–2023, filters the
dataset to include only articles dated between 2018 and 2020 (inclusive),
and saves the resulting subset to the processed data folder.

Design choices:
- Use pandas for data loading and filtering
- Save the filtered subset to the processed data directory

Output:
- CSV file containing article-level data (e.g., date, url, title)
"""

import pandas as pd

# Read the data
df = pd.read_csv('data/raw/rtr_gdelt_2018-2023.csv')

# Filter for 2018-2020 (dates less than 20210101)
df_filtered = df[(df['date'] >= 20180101) & (df['date'] <= 20201231)]

# Save to processed folder
df_filtered.to_csv('data/processed/rtr_gdelt_2018-2020.csv', index=False)

print(f'Original rows: {len(df)}')
print(f'Filtered rows (2018-2020): {len(df_filtered)}')
print(f'Date range: {df_filtered["date"].min()} to {df_filtered["date"].max()}')
