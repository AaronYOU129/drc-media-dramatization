"""
Purpose:    Combine the two Reuters web-scraped files (part1 and part2) into a
            single deduplicated dataset. Deduplication is by URL to avoid counting
            articles that appeared in both scraping runs.
Inputs:     data/raw/rtr_web_2021_2025.csv — part1 scrape.
            data/raw/rtr_web_2021_2025_part2.csv — part2 scrape.
Outputs:    data/processed/rtr_web_2021_2025.csv — merged and deduplicated.
Key Steps:  Load both parts -> concatenate -> deduplicate on URL -> sort by date
            descending -> save.
How to Run: python code/cleaning/rtr_web_2021_2025_combine.py
"""

import pandas as pd
import os


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    raw_dir = os.path.join(project_root, 'data', 'raw')
    processed_dir = os.path.join(project_root, 'data', 'processed')

    df_part1 = pd.read_csv(os.path.join(raw_dir, 'rtr_web_2021_2025.csv'))
    df_part2 = pd.read_csv(os.path.join(raw_dir, 'rtr_web_2021_2025_part2.csv'))
    print(f'Part 1: {len(df_part1)} rows | Part 2: {len(df_part2)} rows')

    df_combined = pd.concat([df_part1, df_part2], ignore_index=True)
    df_combined = df_combined.drop_duplicates(subset=['url'])
    df_combined = df_combined.sort_values('date', ascending=False)

    os.makedirs(processed_dir, exist_ok=True)
    output_path = os.path.join(processed_dir, 'rtr_web_2021_2025.csv')
    df_combined.to_csv(output_path, index=False)

    print(f'Combined (after dedup): {len(df_combined)} rows')
    print(f'Date range: {df_combined["date"].min()} to {df_combined["date"].max()}')
    print(f'Saved to: {output_path}')


if __name__ == "__main__":
    main()
