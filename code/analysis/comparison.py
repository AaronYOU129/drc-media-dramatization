"""
Purpose:    Compare Guardian vs Reuters dramatization scores across multiple
            dimensions: feature coverage rates, pre/post M23 resurgence changes,
            within-Guardian PCA trends, and yearly breakdowns. The M23 cutoff is
            set at 2021/2022 because the M23 rebel group resumed major operations
            in late 2021.
Inputs:     data/processed/guardian_conflict_analyzed.csv
            data/processed/reuters_conflict_analyzed.csv
Outputs:    output/summary_statistics.csv — key comparison metrics.
Key Steps:  Load both datasets -> compare feature coverage rates -> split by
            pre/post M23 period -> run t-test on Guardian PCA scores -> compute
            yearly breakdowns -> save summary.
How to Run: python code/analysis/comparison.py
"""

import pandas as pd
import numpy as np
import os
from scipy import stats


def load_data(processed_dir):
    """Load analyzed Guardian and Reuters datasets."""
    guardian = pd.read_csv(os.path.join(processed_dir, 'guardian_conflict_analyzed.csv'))
    reuters = pd.read_csv(os.path.join(processed_dir, 'reuters_conflict_analyzed.csv'))
    print(f"Guardian: {len(guardian)} articles | Reuters: {len(reuters)} articles")
    return guardian, reuters


def compare_feature_coverage(guardian, reuters):
    """Compare the rate at which each dramatization dimension appears."""
    features = ['has_emotional', 'has_personal', 'has_narrative', 'has_firstperson']
    labels = ['Emotional', 'Personal', 'Narrative', 'First-person']

    print(f"\n{'Feature':<15} {'Guardian':>10} {'Reuters':>10} {'Ratio':>10}")
    print("-" * 50)

    for feat, label in zip(features, labels):
        g_pct = guardian[feat].mean() * 100
        r_pct = reuters[feat].mean() * 100
        ratio = g_pct / r_pct if r_pct > 0 else float('inf')
        print(f"{label:<15} {g_pct:>9.1f}% {r_pct:>9.1f}% {ratio:>9.1f}x")

    g_mean = guardian['drama_binary'].mean()
    r_mean = reuters['drama_binary'].mean()
    print(f"\n{'Mean (0-4)':<15} {g_mean:>10.2f} {r_mean:>10.2f} {g_mean / r_mean:>9.1f}x")


def compare_m23_periods(guardian, reuters):
    """Compare dramatization before and after the M23 resurgence (cutoff: 2021/2022).

    Returns pre/post means and PCA t-test results for the summary.
    """
    # Binary score comparison across both sources
    g_pre = guardian[guardian['year'] <= 2021]['drama_binary']
    g_post = guardian[guardian['year'] >= 2022]['drama_binary']
    r_pre = reuters[reuters['year'] <= 2021]['drama_binary']
    r_post = reuters[reuters['year'] >= 2022]['drama_binary']

    print(f"\n{'Period':<20} {'Guardian':>12} {'Reuters':>12}")
    print("-" * 50)
    print(f"{'Pre-M23 (2018-21)':<20} {g_pre.mean():>10.2f} (N={len(g_pre)}) {r_pre.mean():>6.2f} (N={len(r_pre)})")
    print(f"{'Post-M23 (2022-24)':<20} {g_post.mean():>10.2f} (N={len(g_post)}) {r_post.mean():>6.2f} (N={len(r_post)})")
    print(f"{'Change':<20} {g_post.mean() - g_pre.mean():>+10.2f} {r_post.mean() - r_pre.mean():>+12.2f}")

    # Within-Guardian PCA analysis
    g_pre_pca = guardian[guardian['year'] <= 2021]['drama_pca']
    g_post_pca = guardian[guardian['year'] >= 2022]['drama_pca']

    t_stat, p_val = stats.ttest_ind(g_pre_pca, g_post_pca)
    cohens_d = (g_post_pca.mean() - g_pre_pca.mean()) / np.sqrt(
        (g_pre_pca.std() ** 2 + g_post_pca.std() ** 2) / 2
    )

    print(f"\nWithin-Guardian PCA (t-test):")
    print(f"  Pre-M23:  mean = {g_pre_pca.mean():+.3f}, SD = {g_pre_pca.std():.3f}, N = {len(g_pre_pca)}")
    print(f"  Post-M23: mean = {g_post_pca.mean():+.3f}, SD = {g_post_pca.std():.3f}, N = {len(g_post_pca)}")
    print(f"  t = {t_stat:.2f}, p = {p_val:.4f}, Cohen's d = {cohens_d:.2f}")

    return {
        'guardian_pre_m23': g_pre.mean(),
        'guardian_post_m23': g_post.mean(),
        'reuters_pre_m23': r_pre.mean(),
        'reuters_post_m23': r_post.mean(),
        'pca_t_stat': t_stat,
        'pca_p_val': p_val,
        'pca_cohens_d': cohens_d,
    }


def print_yearly_breakdown(guardian, reuters):
    """Print year-by-year dramatization comparison."""
    print(f"\n{'Year':<6} {'Guardian':>12} {'Reuters':>12} {'Diff':>10}")
    print("-" * 45)

    for year in range(2018, 2025):
        g_year = guardian[guardian['year'] == year]['drama_binary']
        r_year = reuters[reuters['year'] == year]['drama_binary']
        if len(g_year) > 0 and len(r_year) > 0:
            diff = g_year.mean() - r_year.mean()
            print(f"{year:<6} {g_year.mean():>8.2f} (N={len(g_year):>3}) "
                  f"{r_year.mean():>6.2f} (N={len(r_year):>3}) {diff:>+8.2f}")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    processed_dir = os.path.join(project_root, 'data', 'processed')
    output_dir = os.path.join(project_root, 'output')
    os.makedirs(output_dir, exist_ok=True)

    guardian, reuters = load_data(processed_dir)

    print("\n" + "=" * 60)
    print("Feature Coverage Rates")
    print("=" * 60)
    compare_feature_coverage(guardian, reuters)

    print("\n" + "=" * 60)
    print("M23 Pre/Post Comparison")
    print("=" * 60)
    m23_stats = compare_m23_periods(guardian, reuters)

    print("\n" + "=" * 60)
    print("Yearly Breakdown")
    print("=" * 60)
    print_yearly_breakdown(guardian, reuters)

    # Save summary
    summary = {
        'guardian_n': len(guardian),
        'reuters_n': len(reuters),
        'guardian_mean': guardian['drama_binary'].mean(),
        'reuters_mean': reuters['drama_binary'].mean(),
        'ratio': guardian['drama_binary'].mean() / reuters['drama_binary'].mean(),
        **m23_stats,
    }
    summary_path = os.path.join(output_dir, 'summary_statistics.csv')
    pd.Series(summary).to_csv(summary_path)
    print(f"\nSummary saved to {summary_path}")


if __name__ == '__main__':
    main()
