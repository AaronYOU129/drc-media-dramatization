"""
Purpose:
This script combines the two Reuters web-scraped datasets (part1 and part2)
into a single merged file, removing duplicates based on URL.

Design choices:
- Use pandas for data loading and merging
- Remove duplicates based on URL to ensure data integrity
- Save the merged dataset to the processed data directory

Output:
- CSV file containing article-level data (title, date, url)
"""

import pandas as pd
import os

# Get paths relative to script location
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
raw_dir = os.path.join(project_root, 'data', 'raw')
processed_dir = os.path.join(project_root, 'data', 'processed')

# Read both parts
part1_path = os.path.join(raw_dir, 'rtr_web_2021_2025.csv')
part2_path = os.path.join(raw_dir, 'rtr_web_2021_2025_part2.csv')

df_part1 = pd.read_csv(part1_path)
df_part2 = pd.read_csv(part2_path)

print(f'Part 1 rows: {len(df_part1)}')
print(f'Part 2 rows: {len(df_part2)}')

# Combine and remove duplicates
df_combined = pd.concat([df_part1, df_part2], ignore_index=True)
df_combined = df_combined.drop_duplicates(subset=['url'])

# Sort by date (descending)
df_combined = df_combined.sort_values('date', ascending=False)

# Save to processed folder
os.makedirs(processed_dir, exist_ok=True)
output_path = os.path.join(processed_dir, 'rtr_web_2021_2025.csv')
df_combined.to_csv(output_path, index=False)

print(f'Combined rows (after dedup): {len(df_combined)}')
print(f'Date range: {df_combined["date"].min()} to {df_combined["date"].max()}')
print(f'Saved to: {output_path}')
