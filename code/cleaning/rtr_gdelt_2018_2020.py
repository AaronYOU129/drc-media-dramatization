"""
Purpose:    Filter raw Reuters-GDELT data to the 2018-2020 date range. The GDELT
            source covers 2018-2023, but only 2018-2020 is needed because web-scraped
            Reuters data covers 2021 onward.
Inputs:     data/raw/rtr_gdelt_2018-2023.csv — raw GDELT export with integer dates.
Outputs:    data/processed/rtr_gdelt_2018-2020.csv — filtered subset.
Key Steps:  Load raw CSV -> filter rows where date is between 20180101 and 20201231
            -> save.
How to Run: python code/cleaning/rtr_gdelt_2018_2020.py
"""

import pandas as pd


def main():
    df = pd.read_csv('data/raw/rtr_gdelt_2018-2023.csv')
    df_filtered = df[(df['date'] >= 20180101) & (df['date'] <= 20201231)]

    df_filtered.to_csv('data/processed/rtr_gdelt_2018-2020.csv', index=False)

    print(f'Original rows: {len(df)}')
    print(f'Filtered rows (2018-2020): {len(df_filtered)}')
    print(f'Date range: {df_filtered["date"].min()} to {df_filtered["date"].max()}')


if __name__ == "__main__":
    main()
