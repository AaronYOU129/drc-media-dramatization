# ============================================================
# Analyze the results of the LLM validation
# ============================================================

import pandas as pd
import os

# Get paths
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
output_dir = os.path.join(project_root, 'output')

# Load the existing results
df = pd.read_csv(os.path.join(output_dir, 'llm_validation_results.csv'))

# Calculate the correlations
corr_pca = df['llm_total'].corr(df['drama_pca'])
corr_binary = df['llm_total'].corr(df['drama_binary'])

# Per-dimension correlations
dims = ['emotional', 'personal', 'narrative', 'firstperson']
dim_corrs = {}
for dim in dims:
    llm_col = f'llm_{dim}'
    dict_col = f'has_{dim}'
    if llm_col in df.columns and dict_col in df.columns:
        dim_corrs[dim] = df[llm_col].corr(df[dict_col])

# Agreement rate
df['llm_high'] = (df['llm_total'] >= 6).astype(int)
df['dict_high'] = (df['drama_binary'] >= 2).astype(int)
agreement = (df['llm_high'] == df['dict_high']).mean()

# Build summary
lines = []
lines.append("=" * 60)
lines.append("LLM VALIDATION SUMMARY")
lines.append("=" * 60)
lines.append(f"\nOverall correlations:")
lines.append(f"  LLM vs PCA:    r = {corr_pca:.3f}")
lines.append(f"  LLM vs Binary: r = {corr_binary:.3f}")
lines.append(f"\nPer-dimension correlations:")
for dim, corr in dim_corrs.items():
    lines.append(f"  {dim}: r = {corr:.3f}")
lines.append(f"\nBinary agreement rate: {agreement:.1%}")
lines.append(f"Total articles: {len(df)}")

summary = '\n'.join(lines)
print(summary)

# Save to file
summary_path = os.path.join(output_dir, 'llm_validation_summary.txt')
with open(summary_path, 'w') as f:
    f.write(summary)
print(f"\nSaved to {summary_path}")
