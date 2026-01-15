import pandas as pd

df = pd.read_csv('/Users/youzhiwei/salience_news/reuters_drc_all.csv')

# 转换日期（数据里既有带 Z 的 ISO8601，也有其他格式）
df['date'] = pd.to_datetime(df['date'], format='ISO8601', utc=True, errors='coerce')
# 丢弃无法解析的日期
df = df[df['date'].notna()]

# 筛选2022-2024
df_filtered = df[(df['date'] >= '2022-01-01') & (df['date'] <= '2024-12-31')]

# 按日期排序
df_filtered = df_filtered.sort_values('date').reset_index(drop=True)

print(f"原始: {len(df)} 篇")
print(f"2022-2024: {len(df_filtered)} 篇")
print(f"日期范围: {df_filtered['date'].min()} to {df_filtered['date'].max()}")

# 保存
df_filtered.to_csv('reuters_drc_2022_2024.csv', index=False)