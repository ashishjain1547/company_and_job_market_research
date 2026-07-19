"""
Section 9 script — auto-extracted from analyze_20260719.py.
Run standalone:  python section_09_tenure.py
Or via runner:   from section_09_tenure import run; run()
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from shared_config import df, company_demo, save_plot, _section, COLORS, SUB_RATINGS, current_year, OUTPUT_DIR

def run():
    _section("SECTION 9: Employee Tenure Analysis (59-74)")
    
    TENURE_COL = 'Median current employee tenure (in years)'
    
    # Build a dedicated company-level tenure dataframe for convenience
    company_tenure = company_demo[['Company', 'avg_rating', 'total_reviews',
        'company_age', 'global_emp', 'india_emp', 'india_pct_of_global',
        'revenue_usd', 'median_tenure',
        'avg_culture', 'avg_salary', 'avg_wlb', 'avg_satisfaction',
        'avg_skill', 'avg_security', 'avg_promotions']].copy()
    
    # Filter to companies that have tenure data
    tenure_data = company_tenure[company_tenure['median_tenure'].notna()].copy()
    num_tenure = len(tenure_data)
    print(
        f"\nTenure data: {num_tenure} companies have median tenure data."
        f"\n  Range: {tenure_data['median_tenure'].min():.1f} – "
        f"{tenure_data['median_tenure'].max():.1f} years, "
        f"Median: {tenure_data['median_tenure'].median():.1f} years"
    )
    
    # ── 9.59 ── Tenure Distribution (Histogram + KDE) ──
    tenure_clean = df[TENURE_COL].dropna()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(tenure_clean, bins=18, kde=True, color='#1abc9c',
                 edgecolor='#16a085', ax=ax)
    ax.axvline(tenure_clean.mean(), color='#e74c3c', linestyle='--', linewidth=2,
               label=f'Mean: {tenure_clean.mean():.1f} yrs')
    ax.axvline(tenure_clean.median(), color='#f39c12', linestyle='--', linewidth=2,
               label=f'Median: {tenure_clean.median():.1f} yrs')
    ax.set_title('Distribution of Median Current Employee Tenure', fontsize=14, pad=15)
    ax.set_xlabel('Median Tenure (Years)', fontsize=12)
    ax.set_ylabel('Number of Companies', fontsize=12)
    ax.legend(fontsize=10)
    save_plot(plt, "59_tenure_distribution_hist.png")
    
    # ── 9.60 ── Top 20 Companies by Longest Median Tenure ──
    top_tenure = tenure_data.nlargest(20, 'median_tenure').sort_values('median_tenure')
    
    fig, ax = plt.subplots(figsize=(12, 8))
    tenure_bar_colors = plt.cm.Greens(0.3 + 0.7 * np.linspace(0, 1, len(top_tenure)))
    bars = ax.barh(top_tenure['Company'], top_tenure['median_tenure'],
                   color=tenure_bar_colors, edgecolor='white')
    ax.set_xlabel('Median Employee Tenure (Years)', fontsize=12)
    ax.set_title('Top 20 Companies by Longest Median Employee Tenure', fontsize=14, pad=15)
    ax.grid(axis='x', linestyle='--', alpha=0.4)
    for bar, (_, row) in zip(bars, top_tenure.iterrows()):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                f'{row["median_tenure"]:.1f} yrs  *{row["avg_rating"]:.1f}',
                va='center', fontsize=9, fontweight='bold')
    save_plot(plt, "60_top_companies_by_tenure.png")
    
    # ── 9.61 ── Bottom 20 Companies by Shortest Median Tenure ──
    bottom_tenure = tenure_data.nsmallest(20, 'median_tenure').sort_values('median_tenure', ascending=False)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    low_tenure_colors = plt.cm.Reds(0.3 + 0.7 * np.linspace(0, 1, len(bottom_tenure)))
    bars = ax.barh(bottom_tenure['Company'], bottom_tenure['median_tenure'],
                   color=low_tenure_colors, edgecolor='white')
    ax.set_xlabel('Median Employee Tenure (Years)', fontsize=12)
    ax.set_title('Bottom 20 Companies by Shortest Median Employee Tenure\n(Potential retention risk)', fontsize=14, pad=15)
    ax.grid(axis='x', linestyle='--', alpha=0.4)
    for bar, (_, row) in zip(bars, bottom_tenure.iterrows()):
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
                f'{row["median_tenure"]:.1f} yrs  *{row["avg_rating"]:.1f}',
                va='center', fontsize=9, fontweight='bold')
    save_plot(plt, "61_bottom_companies_by_tenure.png")
    
    # ── 9.62 ── Tenure vs Overall Rating (Scatter with regression) ──
    tenure_rating_data = tenure_data.dropna(subset=['avg_rating'])
    
    fig, ax = plt.subplots(figsize=(11, 7))
    scatter = ax.scatter(tenure_rating_data['avg_rating'], tenure_rating_data['median_tenure'],
                         s=tenure_rating_data['total_reviews'] / 10 + 60,
                         c=tenure_rating_data['company_age'].fillna(20), cmap='viridis',
                         alpha=0.8, edgecolors='#2c3e50', linewidth=1)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Company Age (years)', fontsize=11)
    ax.set_xlabel('Average Overall Rating', fontsize=12)
    ax.set_ylabel('Median Employee Tenure (Years)', fontsize=12)
    ax.set_title('Employee Tenure vs Overall Rating\n(size = total reviews, color = company age)\n"Are better-rated companies better at retaining talent?"',
                 fontsize=14, pad=15)
    ax.grid(True, linestyle='--', alpha=0.4)
    
    # Regression line
    mask = tenure_rating_data['avg_rating'].notna() & tenure_rating_data['median_tenure'].notna()
    if mask.sum() > 2:
        z = np.polyfit(tenure_rating_data.loc[mask, 'avg_rating'],
                       tenure_rating_data.loc[mask, 'median_tenure'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(tenure_rating_data['avg_rating'].min(),
                             tenure_rating_data['avg_rating'].max(), 100)
        ax.plot(x_line, p(x_line), 'r--', linewidth=1.5, alpha=0.7,
                label=f'Slope: {z[0]:.2f} yr/*')
        corr_val = tenure_rating_data['avg_rating'].corr(tenure_rating_data['median_tenure'])
        ax.text(0.95, 0.05, f'r={corr_val:.2f}', transform=ax.transAxes,
                fontsize=11, ha='right', va='bottom',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
    
    for _, row in tenure_rating_data.iterrows():
        ax.annotate(row['Company'], (row['avg_rating'], row['median_tenure']),
                    textcoords="offset points", xytext=(5, 5),
                    fontsize=7, ha='left')
    ax.legend(fontsize=9)
    save_plot(plt, "62_tenure_vs_rating.png")
    
    # ── 9.63 ── Tenure vs Company Age (Scatter, bubble = global employees) ──
    tenure_age_data = tenure_data.dropna(subset=['company_age'])
    
    fig, ax = plt.subplots(figsize=(11, 7))
    scatter = ax.scatter(tenure_age_data['company_age'], tenure_age_data['median_tenure'],
                         s=tenure_age_data['global_emp'].fillna(1000) / 30 + 60,
                         c=tenure_age_data['avg_rating'], cmap='RdYlGn', alpha=0.8,
                         edgecolors='white', linewidth=1.2, vmin=2, vmax=5)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Average Rating', fontsize=11)
    ax.set_xlabel('Company Age (years since founding)', fontsize=12)
    ax.set_ylabel('Median Employee Tenure (Years)', fontsize=12)
    ax.set_title('Employee Tenure vs Company Age\n(size = global employees, color = rating)\n"Do older companies naturally retain longer?"',
                 fontsize=14, pad=15)
    ax.grid(True, linestyle='--', alpha=0.4)
    
    # Trend line
    mask = tenure_age_data['company_age'].notna() & tenure_age_data['median_tenure'].notna()
    if mask.sum() > 2:
        z = np.polyfit(tenure_age_data.loc[mask, 'company_age'],
                       tenure_age_data.loc[mask, 'median_tenure'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(tenure_age_data['company_age'].min(),
                             tenure_age_data['company_age'].max(), 100)
        ax.plot(x_line, p(x_line), 'r--', linewidth=1.5, alpha=0.7, label='Trend')
        corr_val = tenure_age_data['company_age'].corr(tenure_age_data['median_tenure'])
        ax.text(0.95, 0.05, f'r={corr_val:.2f}', transform=ax.transAxes,
                fontsize=11, ha='right', va='bottom',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
    
    for _, row in tenure_age_data.iterrows():
        ax.annotate(row['Company'], (row['company_age'], row['median_tenure']),
                    textcoords="offset points", xytext=(5, 5),
                    fontsize=7, ha='left')
    ax.legend(fontsize=9)
    save_plot(plt, "63_tenure_vs_company_age.png")
    
    # ── 9.64 ── Tenure vs Sub-Ratings (Small Multiples) ──
    tenure_sub_map = {
        'avg_culture': 'Company Culture',
        'avg_salary': 'Salary (Sub-Rating)',
        'avg_wlb': 'Work-Life Balance',
        'avg_satisfaction': 'Work Satisfaction',
        'avg_skill': 'Skill Development',
        'avg_security': 'Job Security',
        'avg_promotions': 'Promotions',
    }
    
    fig, axes = plt.subplots(3, 3, figsize=(18, 16))
    axes = axes.flatten()
    
    for i, (col, label) in enumerate(tenure_sub_map.items()):
        ax = axes[i]
        sub_clean = tenure_data.dropna(subset=[col])
        scatter = ax.scatter(sub_clean[col], sub_clean['median_tenure'],
                             s=sub_clean['total_reviews'] / 15 + 50,
                             c=sub_clean['avg_rating'], cmap='RdYlGn', alpha=0.8,
                             edgecolors='#2c3e50', linewidth=0.8, vmin=2, vmax=5)
        ax.set_xlabel(f'{label} Rating', fontsize=10)
        ax.set_ylabel('Median Tenure (yrs)', fontsize=10)
        ax.set_title(f'{label}', fontsize=12, fontweight='bold')
        ax.grid(True, linestyle='--', alpha=0.4)
        ax.set_xlim(sub_clean[col].min() - 0.3, sub_clean[col].max() + 0.4)
        ax.set_ylim(sub_clean['median_tenure'].min() - 0.8,
                    sub_clean['median_tenure'].max() + 0.8)
    
        # Regression
        mask = sub_clean[col].notna() & sub_clean['median_tenure'].notna()
        if mask.sum() > 2:
            z = np.polyfit(sub_clean.loc[mask, col],
                           sub_clean.loc[mask, 'median_tenure'], 1)
            p = np.poly1d(z)
            x_line = np.linspace(sub_clean[col].min(), sub_clean[col].max(), 100)
            ax.plot(x_line, p(x_line), 'r--', linewidth=1.2, alpha=0.6)
        corr_val = sub_clean[col].corr(sub_clean['median_tenure'])
        ax.text(0.95, 0.05, f'r={corr_val:.2f}', transform=ax.transAxes,
                fontsize=9, ha='right', va='bottom',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.6))
    
        for _, row in sub_clean.iterrows():
            ax.annotate(row['Company'], (row[col], row['median_tenure']),
                        textcoords="offset points", xytext=(4, 3),
                        fontsize=6, ha='left', alpha=0.85)
    
    for j in range(len(tenure_sub_map), len(axes)):
        axes[j].set_visible(False)
    
    fig.suptitle('Employee Tenure vs Sub-Ratings\n(color = overall rating, size = total reviews)',
                 fontsize=16, y=1.01)
    plt.tight_layout()
    save_plot(plt, "64_tenure_vs_sub_ratings.png")
    
    # ── 9.65 ── Tenure vs Salary (Scatter with quadrant analysis) ──
    tenure_sal_data = tenure_data.dropna(subset=['avg_salary'])
    
    fig, ax = plt.subplots(figsize=(11, 7))
    bubble_sizes = tenure_sal_data['revenue_usd'].fillna(1e9).apply(
        lambda x: np.log10(x + 1) * 25 + 40
    )
    scatter = ax.scatter(tenure_sal_data['avg_salary'], tenure_sal_data['median_tenure'],
                         s=bubble_sizes,
                         c=tenure_sal_data['avg_rating'], cmap='RdYlGn', alpha=0.8,
                         edgecolors='white', linewidth=1, vmin=2, vmax=5)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Average Rating', fontsize=11)
    ax.set_xlabel('Salary Sub-Rating (0–5)', fontsize=12)
    ax.set_ylabel('Median Employee Tenure (Years)', fontsize=12)
    ax.set_title('Employee Tenure vs Salary Rating\n(size = revenue, color = rating)\n"Does paying well keep employees longer?"',
                 fontsize=14, pad=15)
    ax.grid(True, linestyle='--', alpha=0.4)
    
    # Quadrant reference lines
    ax.axvline(tenure_sal_data['avg_salary'].median(), color='gray', linestyle='--',
               alpha=0.4, linewidth=1)
    ax.axhline(tenure_sal_data['median_tenure'].median(), color='gray', linestyle='--',
               alpha=0.4, linewidth=1)
    
    # Quadrant labels
    ax.text(0.98, 0.98, 'HIGH Pay\nLONG Tenure [*]', transform=ax.transAxes,
            fontsize=9, ha='right', va='top', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='#2ecc71', alpha=0.25))
    ax.text(0.02, 0.98, 'LOW Pay\nLONG Tenure', transform=ax.transAxes,
            fontsize=9, ha='left', va='top',
            bbox=dict(boxstyle='round', facecolor='#f39c12', alpha=0.25))
    ax.text(0.98, 0.02, 'HIGH Pay\nSHORT Tenure', transform=ax.transAxes,
            fontsize=9, ha='right', va='bottom',
            bbox=dict(boxstyle='round', facecolor='#e74c3c', alpha=0.25))
    ax.text(0.02, 0.02, 'LOW Pay\nSHORT Tenure [!]', transform=ax.transAxes,
            fontsize=9, ha='left', va='bottom',
            bbox=dict(boxstyle='round', facecolor='#95a5a6', alpha=0.25))
    
    for _, row in tenure_sal_data.iterrows():
        ax.annotate(row['Company'], (row['avg_salary'], row['median_tenure']),
                    textcoords="offset points", xytext=(5, 5),
                    fontsize=7, ha='left')
    corr_val = tenure_sal_data['avg_salary'].corr(tenure_sal_data['median_tenure'])
    ax.text(0.5, 0.01, f'Correlation (Salary* vs Tenure): r={corr_val:.2f}',
            transform=ax.transAxes, fontsize=10, ha='center', fontstyle='italic',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
    save_plot(plt, "65_tenure_vs_salary_quadrant.png")
    
    # ── 9.66 ── Tenure vs Global Employee Count (Scatter) ──
    tenure_emp_data = tenure_data.dropna(subset=['global_emp'])
    
    fig, ax = plt.subplots(figsize=(11, 7))
    scatter = ax.scatter(tenure_emp_data['global_emp'], tenure_emp_data['median_tenure'],
                         s=tenure_emp_data['total_reviews'] / 10 + 60,
                         c=tenure_emp_data['avg_rating'], cmap='RdYlGn', alpha=0.8,
                         edgecolors='white', linewidth=1, vmin=2, vmax=5)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Average Rating', fontsize=11)
    ax.set_xscale('log')
    ax.set_xlabel('Global Employee Count (log scale)', fontsize=12)
    ax.set_ylabel('Median Employee Tenure (Years)', fontsize=12)
    ax.set_title('Employee Tenure vs Company Size\n(size = reviews, color = rating)\n"Do bigger companies retain employees longer?"',
                 fontsize=14, pad=15)
    ax.grid(True, linestyle='--', alpha=0.4)
    
    # Trend line
    mask = tenure_emp_data['global_emp'].notna() & tenure_emp_data['median_tenure'].notna()
    if mask.sum() > 2:
        z = np.polyfit(np.log10(tenure_emp_data.loc[mask, 'global_emp']),
                       tenure_emp_data.loc[mask, 'median_tenure'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(np.log10(tenure_emp_data['global_emp'].min()),
                             np.log10(tenure_emp_data['global_emp'].max()), 100)
        ax.plot(10 ** x_line, p(x_line), 'r--', linewidth=1.5, alpha=0.7, label='Trend')
    
    for _, row in tenure_emp_data.iterrows():
        ax.annotate(row['Company'], (row['global_emp'], row['median_tenure']),
                    textcoords="offset points", xytext=(5, 5),
                    fontsize=7, ha='left')
    ax.legend(fontsize=9)
    save_plot(plt, "66_tenure_vs_company_size.png")
    
    # ── 9.67 ── Tenure by Revenue Tier (Violin Plot) ──
    tenure_rev_data = tenure_data.dropna(subset=['revenue_usd']).copy()
    tenure_rev_data['revenue_tier'] = pd.cut(
        tenure_rev_data['revenue_usd'],
        bins=[0, 1e9, 10e9, 50e9, 200e9, np.inf],
        labels=['<$1B', '$1B–$10B', '$10B–$50B', '$50B–$200B', '>$200B'],
        right=False,
    )
    
    fig, ax = plt.subplots(figsize=(12, 7))
    tier_order = ['<$1B', '$1B–$10B', '$10B–$50B', '$50B–$200B', '>$200B']
    tier_palette_tenure = sns.color_palette("GnBu_d", len(tier_order))
    sns.violinplot(data=tenure_rev_data, x='revenue_tier', y='median_tenure',
                   hue='revenue_tier', palette=tier_palette_tenure, legend=False,
                   order=tier_order, inner='quartile', ax=ax)
    sns.stripplot(data=tenure_rev_data, x='revenue_tier', y='median_tenure',
                  color='black', alpha=0.3, size=5, jitter=True, ax=ax)
    # Annotate company names
    for _, row in tenure_rev_data.iterrows():
        tier_idx = tier_order.index(row['revenue_tier']) if row['revenue_tier'] in tier_order else -1
        if tier_idx >= 0:
            ax.annotate(row['Company'], (tier_idx, row['median_tenure']),
                        textcoords="offset points", xytext=(0, 8),
                        fontsize=6, ha='center', alpha=0.7)
    
    ax.set_title('Employee Tenure Distribution by Revenue Tier\n"Do deep-pocket companies retain longer?"', fontsize=14, pad=15)
    ax.set_xlabel('Revenue Tier', fontsize=12)
    ax.set_ylabel('Median Employee Tenure (Years)', fontsize=12)
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    save_plot(plt, "67_tenure_by_revenue_tier_violin.png")
    
    # ── 9.68 ── Tenure vs Industry Deviation ──
    tenure_dev_data = tenure_data.dropna(subset=['median_tenure'])
    # Get industry deviation from company_demo
    tenure_dev_data = tenure_dev_data.merge(
        company_demo[['Company', 'avg_rating']].rename(columns={'avg_rating': 'rating_ref'}),
        on='Company', how='left'
    )
    
    # Actually, let's compute industry deviation properly
    ind_dev_map = df.groupby('Company')[
        'Industry level insights (%: -100 (below industry\'s average) to 100)'
    ].mean()
    tenure_dev_data['industry_deviation'] = tenure_dev_data['Company'].map(ind_dev_map)
    tenure_dev_data = tenure_dev_data.dropna(subset=['industry_deviation'])
    
    fig, ax = plt.subplots(figsize=(11, 7))
    scatter = ax.scatter(tenure_dev_data['industry_deviation'], tenure_dev_data['median_tenure'],
                         s=tenure_dev_data['total_reviews'] / 10 + 60,
                         c=tenure_dev_data['avg_rating'], cmap='RdYlGn', alpha=0.8,
                         edgecolors='white', linewidth=1, vmin=2, vmax=5)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Average Rating', fontsize=11)
    ax.axvline(0, color='gray', linestyle='--', alpha=0.5, linewidth=1)
    ax.set_xlabel('Industry Deviation (%)', fontsize=12)
    ax.set_ylabel('Median Employee Tenure (Years)', fontsize=12)
    ax.set_title('Employee Tenure vs Industry Standing\n"Do industry-leading companies have better retention?"',
                 fontsize=14, pad=15)
    ax.grid(True, linestyle='--', alpha=0.4)
    
    for _, row in tenure_dev_data.iterrows():
        ax.annotate(row['Company'], (row['industry_deviation'], row['median_tenure']),
                    textcoords="offset points", xytext=(5, 5),
                    fontsize=7, ha='left')
    
    # Quadrant labels
    ax.text(0.98, 0.98, 'Above Industry\nLONG Tenure [*]',
            transform=ax.transAxes, fontsize=9, ha='right', va='top',
            bbox=dict(boxstyle='round', facecolor='#2ecc71', alpha=0.25))
    ax.text(0.02, 0.98, 'Below Industry\nLONG Tenure',
            transform=ax.transAxes, fontsize=9, ha='left', va='top',
            bbox=dict(boxstyle='round', facecolor='#f39c12', alpha=0.25))
    ax.text(0.98, 0.02, 'Above Industry\nSHORT Tenure',
            transform=ax.transAxes, fontsize=9, ha='right', va='bottom',
            bbox=dict(boxstyle='round', facecolor='#3498db', alpha=0.25))
    ax.text(0.02, 0.02, 'Below Industry\nSHORT Tenure [!]',
            transform=ax.transAxes, fontsize=9, ha='left', va='bottom',
            bbox=dict(boxstyle='round', facecolor='#e74c3c', alpha=0.25))
    
    save_plot(plt, "68_tenure_vs_industry_deviation.png")
    
    # ── 9.69 ── Tenure vs India Workforce % ──
    tenure_india_data = tenure_data.dropna(subset=['india_pct_of_global'])
    
    fig, ax = plt.subplots(figsize=(11, 7))
    scatter = ax.scatter(tenure_india_data['india_pct_of_global'],
                         tenure_india_data['median_tenure'],
                         s=tenure_india_data['total_reviews'] / 10 + 60,
                         c=tenure_india_data['avg_rating'], cmap='RdYlGn', alpha=0.8,
                         edgecolors='white', linewidth=1, vmin=2, vmax=5)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Average Rating', fontsize=11)
    ax.axvline(50, color='#7f8c8d', linestyle='--', alpha=0.5,
               label='50% India workforce')
    ax.set_xlabel('India Workforce as % of Global', fontsize=12)
    ax.set_ylabel('Median Employee Tenure (Years)', fontsize=12)
    ax.set_title('Employee Tenure vs India Workforce Concentration\n(size = reviews, color = rating)',
                 fontsize=14, pad=15)
    ax.grid(True, linestyle='--', alpha=0.4)
    
    mask = tenure_india_data['india_pct_of_global'].notna() & tenure_india_data['median_tenure'].notna()
    if mask.sum() > 2:
        z = np.polyfit(tenure_india_data.loc[mask, 'india_pct_of_global'],
                       tenure_india_data.loc[mask, 'median_tenure'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(tenure_india_data['india_pct_of_global'].min(),
                             tenure_india_data['india_pct_of_global'].max(), 100)
        ax.plot(x_line, p(x_line), 'r--', linewidth=1.5, alpha=0.7, label='Trend')
    
    for _, row in tenure_india_data.iterrows():
        ax.annotate(row['Company'],
                    (row['india_pct_of_global'], row['median_tenure']),
                    textcoords="offset points", xytext=(5, 5),
                    fontsize=7, ha='left')
    ax.legend(fontsize=9)
    save_plot(plt, "69_tenure_vs_india_pct.png")
    
    # ── 9.70 ── Tenure Heatmap: Top 15 Companies × Key Metrics ──
    tenure_heatmap_cols = [
        'median_tenure', 'avg_rating', 'company_age',
        'avg_culture', 'avg_salary', 'avg_wlb',
        'avg_satisfaction', 'avg_skill', 'avg_security', 'avg_promotions',
    ]
    tenure_heatmap_labels = [
        'Tenure (yrs)', 'Rating', 'Age (yrs)',
        'Culture', 'Salary*', 'WLB',
        'Satisfaction', 'Skill', 'Security', 'Promotions',
    ]
    
    top15_by_tenure = tenure_data.nlargest(15, 'median_tenure').set_index('Company')
    tenure_heatmap_raw = top15_by_tenure[tenure_heatmap_cols]
    tenure_heatmap_raw.columns = tenure_heatmap_labels
    
    # Normalize columns to 0-1 for colormap
    tenure_heatmap_norm = (tenure_heatmap_raw - tenure_heatmap_raw.min()) / \
                          (tenure_heatmap_raw.max() - tenure_heatmap_raw.min() + 1e-10)
    
    fig, ax = plt.subplots(figsize=(14, 10))
    sns.heatmap(tenure_heatmap_norm, annot=tenure_heatmap_raw.round(1), fmt='.1f',
                cmap='YlOrRd', ax=ax, linewidths=1, linecolor='white',
                annot_kws={'fontsize': 9}, cbar_kws={'label': 'Normalized Score (0–1)'})
    ax.set_title('Top 15 Companies by Longest Tenure: Key Metrics Comparison', fontsize=14, pad=15)
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.tick_params(axis='both', labelsize=10)
    save_plot(plt, "70_tenure_heatmap_top15.png")
    
    # ── 9.71 ── Tenure: Founding Era Breakdown ──
    tenure_era_data = tenure_data.dropna(subset=['company_age']).copy()
    tenure_era_data['founding_era'] = pd.cut(
        2026 - tenure_era_data['company_age'],
        bins=[1800, 1970, 2000, 2010, 2030],
        labels=['Pre-1970', '1970-1999', '2000-2010', 'Post-2010'],
    )
    
    tenure_era_stats = tenure_era_data.groupby('founding_era', observed=False).agg(
        avg_tenure=('median_tenure', 'mean'),
        median_tenure=('median_tenure', 'median'),
        company_count=('Company', 'count'),
    ).dropna().reset_index()
    
    if len(tenure_era_stats) >= 2:
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
        # Left: avg tenure by era
        ax = axes[0]
        bars = ax.bar(tenure_era_stats['founding_era'], tenure_era_stats['avg_tenure'],
                      color=sns.color_palette("Greens_r", len(tenure_era_stats)), edgecolor='white')
        ax.set_title('Average Employee Tenure by Founding Era', fontsize=13)
        ax.set_ylabel('Average Median Tenure (Years)', fontsize=11)
        ax.set_xlabel('Founding Era', fontsize=11)
        ax.set_ylim(0, tenure_era_stats['avg_tenure'].max() * 1.3)
        for bar, val, cnt in zip(bars, tenure_era_stats['avg_tenure'], tenure_era_stats['company_count']):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.15,
                    f'{val:.1f} yrs\n(n={int(cnt)})', ha='center', fontsize=10, fontweight='bold')
    
        # Right: company count by era
        ax = axes[1]
        bars = ax.bar(tenure_era_stats['founding_era'], tenure_era_stats['company_count'],
                      color=sns.color_palette("Blues_r", len(tenure_era_stats)), edgecolor='white')
        ax.set_title('Number of Companies with Tenure Data per Era', fontsize=13)
        ax.set_ylabel('Company Count', fontsize=11)
        ax.set_xlabel('Founding Era', fontsize=11)
        for bar, val in zip(bars, tenure_era_stats['company_count']):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                    str(int(val)), ha='center', fontsize=11, fontweight='bold')
    
        fig.suptitle('Employee Tenure by Founding Era', fontsize=15, y=1.02)
        plt.tight_layout()
        save_plot(plt, "71_tenure_by_founding_era.png")
    
    # ── 9.72 ── Tenure: Comprehensive Correlation Heatmap ──
    tenure_corr_cols = [
        'median_tenure', 'avg_rating', 'total_reviews',
        'company_age', 'global_emp', 'india_emp', 'india_pct_of_global',
        'avg_culture', 'avg_salary', 'avg_wlb',
        'avg_satisfaction', 'avg_skill', 'avg_security', 'avg_promotions',
    ]
    tenure_corr_labels = [
        'Tenure (yrs)', 'Rating', 'Reviews',
        'Age (yrs)', 'Global Emp', 'India Emp', 'India %',
        'Culture', 'Salary*', 'WLB',
        'Satisfaction', 'Skill', 'Security', 'Promotions',
    ]
    
    tenure_corr_df = tenure_data[tenure_corr_cols].copy()
    # Log-transform scale variables
    for col in ['global_emp', 'india_emp', 'total_reviews']:
        tenure_corr_df[col] = np.log10(tenure_corr_df[col].replace(0, np.nan))
    tenure_corr_df.columns = tenure_corr_labels
    tenure_corr = tenure_corr_df.corr()
    
    fig, ax = plt.subplots(figsize=(14, 12))
    mask = np.triu(np.ones_like(tenure_corr, dtype=bool), k=1)
    sns.heatmap(tenure_corr, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
                square=True, ax=ax, mask=mask, vmin=-1, vmax=1,
                annot_kws={'fontsize': 8}, linewidths=0.5,
                cbar_kws={'label': 'Pearson r (log₁₀ for scale vars)'})
    # Highlight the tenure row
    for i in range(tenure_corr.shape[1]):
        if i > 0:  # Skip self-correlation
            val = tenure_corr.iloc[0, i]
            color = '#2ecc71' if val > 0 else '#e74c3c' if val < -0.1 else '#666'
            ax.text(i + 0.5, 0.5, f'{val:.2f}', ha='center', va='center',
                    fontsize=10, fontweight='bold', color=color)
    ax.set_title('Employee Tenure: Comprehensive Correlation Matrix\n(log₁₀ transformed for employee count & review variables)\nFirst row = what correlates with tenure',
                 fontsize=14, pad=18)
    ax.tick_params(axis='both', labelsize=9)
    save_plot(plt, "72_tenure_correlation_heatmap.png")
    
    # ── 9.73 ── Tenure vs Revenue (Scatter) ──
    tenure_rev_scatter = tenure_data.dropna(subset=['revenue_usd'])
    
    fig, ax = plt.subplots(figsize=(12, 7))
    scatter = ax.scatter(tenure_rev_scatter['revenue_usd'],
                         tenure_rev_scatter['median_tenure'],
                         s=tenure_rev_scatter['global_emp'].fillna(1000) / 30 + 80,
                         c=tenure_rev_scatter['avg_rating'], cmap='RdYlGn', alpha=0.8,
                         edgecolors='#2c3e50', linewidth=1.2, vmin=2, vmax=5)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Average Rating', fontsize=11)
    ax.set_xscale('log')
    ax.set_xlabel('Annual Revenue (USD, log scale)', fontsize=12)
    ax.set_ylabel('Median Employee Tenure (Years)', fontsize=12)
    ax.set_title('Employee Tenure vs Company Revenue\n(size = global employees, color = rating)\n"Revenue-rich = retention-rich?"',
                 fontsize=14, pad=15)
    ax.grid(True, linestyle='--', alpha=0.4)
    
    mask = tenure_rev_scatter['revenue_usd'].notna() & tenure_rev_scatter['median_tenure'].notna()
    if mask.sum() > 2:
        z = np.polyfit(np.log10(tenure_rev_scatter.loc[mask, 'revenue_usd']),
                       tenure_rev_scatter.loc[mask, 'median_tenure'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(np.log10(tenure_rev_scatter['revenue_usd'].min()),
                             np.log10(tenure_rev_scatter['revenue_usd'].max()), 100)
        ax.plot(10 ** x_line, p(x_line), 'r--', linewidth=1.5, alpha=0.7, label='Trend')
    
    for _, row in tenure_rev_scatter.iterrows():
        ax.annotate(row['Company'], (row['revenue_usd'], row['median_tenure']),
                    textcoords="offset points", xytext=(5, 5),
                    fontsize=7, ha='left')
    ax.legend(fontsize=9)
    save_plot(plt, "73_tenure_vs_revenue.png")
    
    # ── 9.74 ── Tenure: "Retention Scorecard" — Combined Bar (Tenure + Rating) ──
    # Sort by tenure, annotate with rating; a quick-glance retention dashboard
    scorecard_data = tenure_data.nlargest(25, 'median_tenure').sort_values('median_tenure')
    
    fig, ax = plt.subplots(figsize=(12, 9))
    # Color bars by rating (green = high rating, red = lower)
    scorecard_norm = plt.Normalize(scorecard_data['avg_rating'].min(),
                                    scorecard_data['avg_rating'].max())
    scorecard_colors = plt.cm.RdYlGn(0.15 + 0.7 * scorecard_norm(scorecard_data['avg_rating']))
    bars = ax.barh(scorecard_data['Company'], scorecard_data['median_tenure'],
                   color=scorecard_colors, edgecolor='#2c3e50', linewidth=0.8)
    ax.set_xlabel('Median Employee Tenure (Years)', fontsize=12)
    ax.set_title('Retention Scorecard: Top 25 Companies by Employee Tenure\n(Color = overall rating: green->high, red->lower)',
                 fontsize=14, pad=15)
    ax.grid(axis='x', linestyle='--', alpha=0.4)
    
    # Add a colorbar as legend for rating
    sm = plt.cm.ScalarMappable(cmap='RdYlGn', norm=scorecard_norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label('Overall Rating', fontsize=11)
    
    for bar, (_, row) in zip(bars, scorecard_data.iterrows()):
        ax.text(bar.get_width() + 0.15, bar.get_y() + bar.get_height()/2,
                f'{row["median_tenure"]:.1f} yrs  *{row["avg_rating"]:.1f}',
                va='center', fontsize=9, fontweight='bold')
    save_plot(plt, "74_tenure_retention_scorecard.png")
    
    print(f"\nEmployee Tenure section plots saved (59–74).")
    print(f"  ✓ Section 9 complete — 16 plots saved.")

if __name__ == "__main__":
    run()
