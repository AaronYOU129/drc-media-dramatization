"""
Purpose:    Analyze the LLM validation results by computing correlations between
            LLM scores and both PCA-based and binary dictionary scores. This is
            run separately from llm_validation.py so results can be re-analyzed
            without re-calling the API.
Inputs:     output/llm_validation_results.csv — merged dictionary + LLM scores.
Outputs:    output/llm_validation_summary.txt — human-readable summary.
Key Steps:  Load validation results -> compute overall and per-dimension correlations
            -> compute binary agreement rate -> print and save summary.
How to Run: python code/analysis/llm_validation_analysis.py
"""

import pandas as pd
import os

DIMENSIONS = ['emotional', 'personal', 'narrative', 'firstperson']


def compute_correlations(df):
    """Compute overall and per-dimension correlations between LLM and dictionary scores."""
    corr_pca = df['llm_total'].corr(df['drama_pca'])
    corr_binary = df['llm_total'].corr(df['drama_binary'])

    dim_corrs = {}
    for dim in DIMENSIONS:
        llm_col = f'llm_{dim}'
        dict_col = f'has_{dim}'
        if llm_col in df.columns and dict_col in df.columns:
            dim_corrs[dim] = df[llm_col].corr(df[dict_col])

    return corr_pca, corr_binary, dim_corrs


def compute_agreement(df):
    """Compute binary high/low agreement rate between LLM and dictionary methods."""
    llm_high = (df['llm_total'] >= 6).astype(int)
    dict_high = (df['drama_binary'] >= 2).astype(int)
    return (llm_high == dict_high).mean()


def build_summary(df, corr_pca, corr_binary, dim_corrs, agreement):
    """Format results into a printable summary string."""
    lines = [
        "=" * 60,
        "LLM VALIDATION SUMMARY",
        "=" * 60,
        f"\nOverall correlations:",
        f"  LLM vs PCA:    r = {corr_pca:.3f}",
        f"  LLM vs Binary: r = {corr_binary:.3f}",
        f"\nPer-dimension correlations:",
    ]
    for dim, corr in dim_corrs.items():
        lines.append(f"  {dim}: r = {corr:.3f}")
    lines.append(f"\nBinary agreement rate: {agreement:.1%}")
    lines.append(f"Total articles: {len(df)}")
    return '\n'.join(lines)


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    output_dir = os.path.join(project_root, 'output')

    df = pd.read_csv(os.path.join(output_dir, 'llm_validation_results.csv'))

    corr_pca, corr_binary, dim_corrs = compute_correlations(df)
    agreement = compute_agreement(df)
    summary = build_summary(df, corr_pca, corr_binary, dim_corrs, agreement)

    print(summary)

    summary_path = os.path.join(output_dir, 'llm_validation_summary.txt')
    with open(summary_path, 'w') as f:
        f.write(summary)
    print(f"\nSaved to {summary_path}")


if __name__ == "__main__":
    main()
