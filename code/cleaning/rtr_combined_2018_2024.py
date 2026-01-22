"""
Purpose:
This script combines Reuters data from two sources:
1. GDELT data (2018-2020)
2. Web-scraped data (filtered to 2021-2024)

Design choices:
- Filter web data to 2021-2024 only
- Standardize date formats across sources
- Remove duplicates based on URL
- Sort by date ascending

Output:
- CSV file containing article-level data (title, date, url)
- Date range: 2018-2024
"""

import pandas as pd
import os

# Get paths relative to script location
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
processed_dir = os.path.join(project_root, 'data', 'processed')

# Read the combined web data
web_path = os.path.join(processed_dir, 'rtr_web_2021_2025.csv')
df_web = pd.read_csv(web_path)

# Convert date to datetime and remove timezone
df_web['date_parsed'] = pd.to_datetime(df_web['date'], format='ISO8601').dt.tz_localize(None)
df_web_filtered = df_web[(df_web['date_parsed'].dt.year >= 2021) & (df_web['date_parsed'].dt.year <= 2024)]

print(f'Web data (2021-2024): {len(df_web_filtered)} rows')
print(f'Date range: {df_web_filtered["date_parsed"].min()} to {df_web_filtered["date_parsed"].max()}')

# Read the gdelt 2018-2020 data
gdelt_path = os.path.join(processed_dir, 'rtr_gdelt_2018-2020.csv')
df_gdelt = pd.read_csv(gdelt_path)
print(f'GDELT data (2018-2020): {len(df_gdelt)} rows')

# Convert gdelt date to datetime
df_gdelt['date_parsed'] = pd.to_datetime(df_gdelt['date'], format='%Y%m%d')

# Prepare for combining
df_web_out = df_web_filtered[['title', 'date_parsed', 'url']].rename(columns={'date_parsed': 'date'})
df_gdelt_out = df_gdelt[['date_parsed', 'url']].rename(columns={'date_parsed': 'date'})
df_gdelt_out['title'] = None  # gdelt doesn't have title

# Combine both datasets
df_combined = pd.concat([df_gdelt_out, df_web_out], ignore_index=True)
df_combined = df_combined.drop_duplicates(subset=['url'])
df_combined = df_combined.sort_values('date')

# Save
output_path = os.path.join(processed_dir, 'rtr_combined_2018_2024.csv')
df_combined.to_csv(output_path, index=False)

print(f'\nCombined total: {len(df_combined)} rows')
print(f'Date range: {df_combined["date"].min()} to {df_combined["date"].max()}')
print(f'Saved to: {output_path}')
