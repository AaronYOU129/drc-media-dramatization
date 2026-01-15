import pandas as pd

# load data
df = pd.read_csv("/Users/youzhiwei/Downloads/Reuters_2018-2024.csv")

# make sure date column is datetime
df["date"] = pd.to_datetime(df["date"])

# filter 2018–2021 (inclusive)
df_2018_2021 = df[
    (df["date"] >= "2018-01-01") &
    (df["date"] <= "2021-12-31")
]

# save result
df_2018_2021.to_csv("reuters_drc_titles_2018-2021.csv", index=False)
