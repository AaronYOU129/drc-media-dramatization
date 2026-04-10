"""
Purpose:    Merge Reuters data from two different sources (GDELT 2018-2020 and
            web-scraped 2021-2024) into a single timeline. Date formats differ
            between sources: GDELT uses integer YYYYMMDD, web data uses ISO8601.
            Both are standardized to datetime before merging.
Inputs:     data/processed/rtr_gdelt_2018-2020.csv — GDELT source (no titles).
            data/processed/rtr_web_2021_2025.csv — web-scraped source.
Outputs:    data/processed/rtr_combined_2018_2024.csv — unified Reuters dataset.
Key Steps:  Load both sources -> parse dates to common datetime format -> filter
            web data to 2021-2024 -> combine -> deduplicate on URL -> sort by date.
How to Run: python code/cleaning/rtr_combined_2018_2024.py
"""

import pandas as pd
import os


def load_web_data(processed_dir):
    """Load web-scraped Reuters data and filter to 2021-2024."""
    df = pd.read_csv(os.path.join(processed_dir, 'rtr_web_2021_2025.csv'))
    df['date_parsed'] = pd.to_datetime(df['date'], format='ISO8601').dt.tz_localize(None)
    df = df[(df['date_parsed'].dt.year >= 2021) & (df['date_parsed'].dt.year <= 2024)]
    return df[['title', 'date_parsed', 'url']].rename(columns={'date_parsed': 'date'})


def load_gdelt_data(processed_dir):
    """Load GDELT data and convert integer dates to datetime."""
    df = pd.read_csv(os.path.join(processed_dir, 'rtr_gdelt_2018-2020.csv'))
    df['date_parsed'] = pd.to_datetime(df['date'], format='%Y%m%d')
    df_out = df[['date_parsed', 'url']].rename(columns={'date_parsed': 'date'})
    df_out['title'] = None  # GDELT source has no titles
    return df_out


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    processed_dir = os.path.join(project_root, 'data', 'processed')

    df_web = load_web_data(processed_dir)
    df_gdelt = load_gdelt_data(processed_dir)
    print(f'Web data (2021-2024): {len(df_web)} rows')
    print(f'GDELT data (2018-2020): {len(df_gdelt)} rows')

    df_combined = pd.concat([df_gdelt, df_web], ignore_index=True)
    df_combined = df_combined.drop_duplicates(subset=['url'])
    df_combined = df_combined.sort_values('date')

    output_path = os.path.join(processed_dir, 'rtr_combined_2018_2024.csv')
    df_combined.to_csv(output_path, index=False)

    print(f'\nCombined total: {len(df_combined)} rows')
    print(f'Date range: {df_combined["date"].min()} to {df_combined["date"].max()}')
    print(f'Saved to: {output_path}')


if __name__ == "__main__":
    main()
