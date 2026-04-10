"""
Purpose:    Generate four publication-quality figures comparing Guardian and Reuters
            dramatization scores. Figures include trend lines, feature coverage bars,
            PCA time series with confidence intervals, and pre/post M23 box plots.
Inputs:     data/processed/guardian_conflict_analyzed.csv
            data/processed/reuters_conflict_analyzed.csv
Outputs:    output/figures/fig1_guardian_vs_reuters_trend.pdf
            output/figures/fig2_feature_coverage.pdf
            output/figures/fig3_guardian_pca_trend.pdf
            output/figures/fig4_pre_post_m23.pdf
Key Steps:  Load both datasets -> generate each figure -> save as PDF.
How to Run: python code/analysis/figures.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from scipy import stats

# ---------------------------------------------------------------------------
# Paths and data
# ---------------------------------------------------------------------------
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
processed_dir = os.path.join(project_root, 'data', 'processed')
figures_dir = os.path.join(project_root, 'output', 'figures')

YEARS = range(2018, 2025)

# Colors used consistently across all figures
COLOR_GUARDIAN = '#27ae60'
COLOR_REUTERS = '#3498db'
COLOR_PCA = '#c0392b'
COLOR_PRE_M23 = '#3498db'
COLOR_POST_M23 = '#e74c3c'


def load_data():
    """Load analyzed Guardian and Reuters datasets."""
    guardian = pd.read_csv(os.path.join(processed_dir, 'guardian_conflict_analyzed.csv'))
    reuters = pd.read_csv(os.path.join(processed_dir, 'reuters_conflict_analyzed.csv'))
    return guardian, reuters


# ---------------------------------------------------------------------------
# Figure 1: Guardian vs Reuters trend over time
# ---------------------------------------------------------------------------
def fig1_trend(guardian, reuters):
    fig, ax = plt.subplots(figsize=(8, 5))

    g_yearly = [guardian[guardian['year'] == y]['drama_binary'].mean() for y in YEARS]
    r_yearly = [reuters[reuters['year'] == y]['drama_binary'].mean() for y in YEARS]

    ax.plot(YEARS, g_yearly, 'o-', color=COLOR_GUARDIAN, linewidth=2.5, markersize=10,
            label='Guardian (full text)')
    ax.plot(YEARS, r_yearly, 's-', color=COLOR_REUTERS, linewidth=2.5, markersize=10,
            label='Reuters (headline)')
    ax.axvline(x=2021.5, color='red', linestyle='--', alpha=0.7, linewidth=2)
    ax.fill_between(YEARS, g_yearly, r_yearly, alpha=0.15, color=COLOR_GUARDIAN)

    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Dramatization Score\n(dimensions present, 0-4)', fontsize=11)
    ax.set_title('Guardian vs Reuters: Dramatization Over Time', fontsize=13, fontweight='bold')
    ax.legend(loc='center right', fontsize=10)
    ax.set_xticks(YEARS)
    ax.set_ylim(0, 4)
    ax.grid(True, alpha=0.3)
    ax.text(2021.7, 3.7, 'M23\nResurgence', fontsize=9, color='red', ha='left')

    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, 'fig1_guardian_vs_reuters_trend.pdf'), bbox_inches='tight')
    plt.close()
    print("Figure 1 saved")


# ---------------------------------------------------------------------------
# Figure 2: Feature coverage bar chart
# ---------------------------------------------------------------------------
def fig2_coverage(guardian, reuters):
    fig, ax = plt.subplots(figsize=(8, 5))

    feature_names = ['Emotional', 'Personal', 'Narrative', 'First-person']
    feature_cols = ['has_emotional', 'has_personal', 'has_narrative', 'has_firstperson']
    g_vals = [guardian[col].mean() * 100 for col in feature_cols]
    r_vals = [reuters[col].mean() * 100 for col in feature_cols]

    x = np.arange(len(feature_names))
    width = 0.35

    bars_g = ax.bar(x - width / 2, g_vals, width, label='Guardian', color=COLOR_GUARDIAN, alpha=0.85)
    bars_r = ax.bar(x + width / 2, r_vals, width, label='Reuters', color=COLOR_REUTERS, alpha=0.85)

    ax.set_ylabel('% of articles with feature', fontsize=11)
    ax.set_title('Feature Coverage: Guardian vs Reuters', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(feature_names, fontsize=11)
    ax.legend(fontsize=10)
    ax.set_ylim(0, 105)
    ax.grid(True, alpha=0.3, axis='y')

    for bar, val in zip(bars_g, g_vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
                f'{val:.0f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
    for bar, val in zip(bars_r, r_vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
                f'{val:.0f}%', ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, 'fig2_feature_coverage.pdf'), bbox_inches='tight')
    plt.close()
    print("Figure 2 saved")


# ---------------------------------------------------------------------------
# Figure 3: Guardian PCA trend with 95% CI
# ---------------------------------------------------------------------------
def fig3_pca_trend(guardian):
    fig, ax = plt.subplots(figsize=(8, 5))

    yearly_stats = guardian.groupby('year')['drama_pca'].agg(['mean', 'std', 'count'])
    means = [yearly_stats.loc[y, 'mean'] for y in YEARS]
    standard_errors = [yearly_stats.loc[y, 'std'] / np.sqrt(yearly_stats.loc[y, 'count'])
                       for y in YEARS]

    ax.plot(YEARS, means, 'o-', color=COLOR_PCA, linewidth=2.5, markersize=10)
    ax.fill_between(YEARS,
                    [m - 1.96 * se for m, se in zip(means, standard_errors)],
                    [m + 1.96 * se for m, se in zip(means, standard_errors)],
                    alpha=0.2, color=COLOR_PCA)
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax.axvline(x=2021.5, color='red', linestyle='--', alpha=0.7, linewidth=2)

    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Dramatization Index (PC1)', fontsize=11)
    ax.set_title('Guardian Conflict Coverage: Dramatization Over Time', fontsize=13, fontweight='bold')
    ax.set_xticks(YEARS)
    ax.grid(True, alpha=0.3)
    ax.text(2021.7, 0.4, 'M23\nResurgence', fontsize=9, color='red', ha='left')

    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, 'fig3_guardian_pca_trend.pdf'), bbox_inches='tight')
    plt.close()
    print("Figure 3 saved")


# ---------------------------------------------------------------------------
# Figure 4: Pre vs Post M23 box plot
# ---------------------------------------------------------------------------
def fig4_m23_comparison(guardian):
    fig, ax = plt.subplots(figsize=(7, 5))

    pre_m23 = guardian[guardian['year'] <= 2021]['drama_pca']
    post_m23 = guardian[guardian['year'] >= 2022]['drama_pca']

    bp = ax.boxplot([pre_m23, post_m23], positions=[1, 2], widths=0.5, patch_artist=True)
    bp['boxes'][0].set_facecolor(COLOR_PRE_M23)
    bp['boxes'][0].set_alpha(0.7)
    bp['boxes'][1].set_facecolor(COLOR_POST_M23)
    bp['boxes'][1].set_alpha(0.7)

    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax.set_xticks([1, 2])
    ax.set_xticklabels([f'Pre-M23\n(2018-2021)\n$N$={len(pre_m23)}',
                        f'Post-M23\n(2022-2024)\n$N$={len(post_m23)}'], fontsize=11)
    ax.set_ylabel('Dramatization Index (PC1)', fontsize=11)
    ax.set_title('Guardian: Pre vs Post M23 Comparison', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

    t_stat, p_val = stats.ttest_ind(pre_m23, post_m23)
    cohens_d = (post_m23.mean() - pre_m23.mean()) / np.sqrt(
        (pre_m23.std() ** 2 + post_m23.std() ** 2) / 2
    )
    ax.text(1.5, ax.get_ylim()[1] * 0.9,
            f'$\\Delta$ = {post_m23.mean() - pre_m23.mean():.3f}\n'
            f'$t$ = {abs(t_stat):.2f}, $p$ = {p_val:.3f}\n'
            f"Cohen's $d$ = {cohens_d:.2f}",
            ha='center', va='top', fontsize=11,
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, 'fig4_pre_post_m23.pdf'), bbox_inches='tight')
    plt.close()
    print("Figure 4 saved")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    os.makedirs(figures_dir, exist_ok=True)
    guardian, reuters = load_data()

    fig1_trend(guardian, reuters)
    fig2_coverage(guardian, reuters)
    fig3_pca_trend(guardian)
    fig4_m23_comparison(guardian)

    print(f"\nAll figures saved to {figures_dir}")


if __name__ == '__main__':
    main()
