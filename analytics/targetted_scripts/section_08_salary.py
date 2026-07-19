"""
Section 8 script — auto-extracted from analyze_20260719.py.
Run standalone:  python section_08_salary.py
Or via runner:   from section_08_salary import run; run()
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from shared_config import df, company_demo, save_plot, _section, COLORS, SUB_RATINGS, current_year, OUTPUT_DIR

def run():
    _section("SECTION 8: Salary & Experience Analysis (46-58)")
    
    # Build company-level salary aggregates
    company_salary = df.groupby('Company').agg(
        avg_salary_lyr=('Avg Salary (L/Yr)', 'mean'),
        salary_count=('Avg Salary (L/Yr)', 'count'),
        avg_rating=('Rating', 'mean'),
        total_reviews=('#Reviews', 'sum'),
        avg_salary_sub=('Salary', 'mean'),           # Salary sub-rating
        avg_wlb=('Work-Life Balance', 'mean'),
        avg_culture=('Company Culture', 'mean'),
        avg_satisfaction=('Work Satisfaction', 'mean'),
        avg_skill=('Skill Development', 'mean'),
        avg_security=('Job Security', 'mean'),
        avg_promotions=('Promotions', 'mean'),
        industry_deviation=('Industry level insights (%: -100 (below industry\'s average) to 100)', 'mean'),
        global_emp=('Global Employee Count', 'first'),
        india_emp=('India Employee Count', 'first'),
        founded=('Founded in', 'first'),
    ).reset_index()
    
    # Merge revenue data
    company_salary['revenue_usd'] = company_salary['Company'].map(
        lambda c: company_demo.set_index('Company')['revenue_usd'].get(c)
    )
    company_salary['company_age'] = current_year - company_salary['founded']
    
    # Salary per YOE (proxy for per-year earning efficiency)
    company_salary['salary_per_yoe'] = company_salary['avg_salary_lyr'] / 13.0
    
    print(
        f"\nSalary data: {company_salary['avg_salary_lyr'].notna().sum()} companies "
        f"have salary data. "
        f"Range: Rs.{company_salary['avg_salary_lyr'].min():.1f}L–"
        f"Rs.{company_salary['avg_salary_lyr'].max():.1f}L/yr, "
        f"Median: Rs.{company_salary['avg_salary_lyr'].median():.1f}L/yr"
    )
    
    # ── 8.46 ── Salary Distribution (Histogram + KDE) ──
    salary_clean = df['Avg Salary (L/Yr)'].dropna()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(salary_clean, bins=20, kde=True, color='#8e44ad',
                 edgecolor='#6c3483', ax=ax)
    ax.axvline(salary_clean.mean(), color='red', linestyle='--', linewidth=2,
               label=f'Mean: Rs.{salary_clean.mean():.1f}L/yr')
    ax.axvline(salary_clean.median(), color='#e67e22', linestyle='--', linewidth=2,
               label=f'Median: Rs.{salary_clean.median():.1f}L/yr')
    ax.set_title('Distribution of Average Salary (Lakhs/Year)\nfor ~13 YOE Professionals', fontsize=14, pad=15)
    ax.set_xlabel('Avg Salary (Lakhs/Year)', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.legend(fontsize=10)
    save_plot(plt, "46_salary_distribution_hist.png")
    
    # ── 8.47 ── Top Companies by Average Salary (Bar Chart) ──
    top_salary = company_salary.dropna(subset=['avg_salary_lyr']).nlargest(20, 'avg_salary_lyr').sort_values('avg_salary_lyr')
    
    fig, ax = plt.subplots(figsize=(12, 8))
    sal_colors = plt.cm.RdYlGn(0.2 + 0.7 * np.linspace(0, 1, len(top_salary)))
    bars = ax.barh(top_salary['Company'], top_salary['avg_salary_lyr'],
                   color=sal_colors, edgecolor='white')
    ax.set_xlabel('Average Salary (Lakhs/Year)', fontsize=12)
    ax.set_title('Top 20 Companies by Average Salary\n(for ~13 YOE professionals)', fontsize=14, pad=15)
    ax.grid(axis='x', linestyle='--', alpha=0.4)
    for bar, (_, row) in zip(bars, top_salary.iterrows()):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                f'Rs.{row["avg_salary_lyr"]:.1f}L  *{row["avg_rating"]:.1f}',
                va='center', fontsize=9, fontweight='bold')
    save_plot(plt, "47_top_companies_by_salary.png")
    
    # ── 8.48 ── Salary vs Overall Rating (Scatter with regression) ──
    sal_rating_data = company_salary.dropna(subset=['avg_salary_lyr', 'avg_rating'])
    
    fig, ax = plt.subplots(figsize=(11, 7))
    scatter = ax.scatter(sal_rating_data['avg_rating'], sal_rating_data['avg_salary_lyr'],
                         s=sal_rating_data['total_reviews'] / 10 + 60,
                         c=sal_rating_data['company_age'].fillna(20), cmap='viridis',
                         alpha=0.8, edgecolors='#2c3e50', linewidth=1)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Company Age (years)', fontsize=11)
    ax.set_xlabel('Average Overall Rating', fontsize=12)
    ax.set_ylabel('Average Salary (Lakhs/Year)', fontsize=12)
    ax.set_title('Salary vs Overall Rating\n(size = total reviews, color = company age)', fontsize=14, pad=15)
    ax.grid(True, linestyle='--', alpha=0.4)
    
    # Regression line
    mask = sal_rating_data['avg_rating'].notna() & sal_rating_data['avg_salary_lyr'].notna()
    if mask.sum() > 2:
        z = np.polyfit(sal_rating_data.loc[mask, 'avg_rating'],
                       sal_rating_data.loc[mask, 'avg_salary_lyr'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(sal_rating_data['avg_rating'].min(),
                             sal_rating_data['avg_rating'].max(), 100)
        ax.plot(x_line, p(x_line), 'r--', linewidth=1.5, alpha=0.7,
                label=f'Slope: {z[0]:.1f} L/*')
        corr_val = sal_rating_data['avg_rating'].corr(sal_rating_data['avg_salary_lyr'])
        ax.text(0.95, 0.05, f'r={corr_val:.2f}', transform=ax.transAxes,
                fontsize=11, ha='right', va='bottom',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
    
    for _, row in sal_rating_data.iterrows():
        ax.annotate(row['Company'], (row['avg_rating'], row['avg_salary_lyr']),
                    textcoords="offset points", xytext=(5, 5),
                    fontsize=7, ha='left')
    ax.legend(fontsize=9)
    save_plot(plt, "48_salary_vs_rating.png")
    
    # ── 8.49 ── Salary vs Revenue (Scatter, bubble = global employees) ──
    sal_rev_data = company_salary.dropna(subset=['avg_salary_lyr', 'revenue_usd'])
    
    fig, ax = plt.subplots(figsize=(12, 7))
    scatter = ax.scatter(sal_rev_data['revenue_usd'], sal_rev_data['avg_salary_lyr'],
                         s=sal_rev_data['global_emp'].fillna(1000) / 30 + 80,
                         c=sal_rev_data['avg_rating'], cmap='RdYlGn', alpha=0.8,
                         edgecolors='#2c3e50', linewidth=1.2, vmin=2, vmax=5)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Average Rating', fontsize=11)
    ax.set_xscale('log')
    ax.set_xlabel('Annual Revenue (USD, log scale)', fontsize=12)
    ax.set_ylabel('Average Salary (Lakhs/Year)', fontsize=12)
    ax.set_title('Salary vs Company Revenue\n(size = global employees, color = rating)', fontsize=14, pad=15)
    ax.grid(True, linestyle='--', alpha=0.4)
    
    mask = sal_rev_data['revenue_usd'].notna() & sal_rev_data['avg_salary_lyr'].notna()
    if mask.sum() > 2:
        z = np.polyfit(np.log10(sal_rev_data.loc[mask, 'revenue_usd']),
                       sal_rev_data.loc[mask, 'avg_salary_lyr'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(np.log10(sal_rev_data['revenue_usd'].min()),
                             np.log10(sal_rev_data['revenue_usd'].max()), 100)
        ax.plot(10 ** x_line, p(x_line), 'r--', linewidth=1.5, alpha=0.7, label='Trend')
    
    for _, row in sal_rev_data.iterrows():
        ax.annotate(row['Company'], (row['revenue_usd'], row['avg_salary_lyr']),
                    textcoords="offset points", xytext=(5, 5),
                    fontsize=7, ha='left')
    ax.legend(fontsize=9)
    save_plot(plt, "49_salary_vs_revenue.png")
    
    # ── 8.50 ── Salary vs India Employee Count ──
    sal_india_data = company_salary.dropna(subset=['avg_salary_lyr', 'india_emp'])
    
    fig, ax = plt.subplots(figsize=(11, 7))
    scatter = ax.scatter(sal_india_data['india_emp'], sal_india_data['avg_salary_lyr'],
                         s=sal_india_data['total_reviews'] / 10 + 60,
                         c=sal_india_data['avg_rating'], cmap='RdYlGn', alpha=0.8,
                         edgecolors='white', linewidth=1, vmin=2, vmax=5)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Average Rating', fontsize=11)
    ax.set_xscale('log')
    ax.set_xlabel('India Employee Count (log scale)', fontsize=12)
    ax.set_ylabel('Average Salary (Lakhs/Year)', fontsize=12)
    ax.set_title('Salary vs India Workforce Scale\n(size = reviews, color = rating)', fontsize=14, pad=15)
    ax.grid(True, linestyle='--', alpha=0.4)
    
    mask = sal_india_data['india_emp'].notna() & sal_india_data['avg_salary_lyr'].notna()
    if mask.sum() > 2:
        z = np.polyfit(np.log10(sal_india_data.loc[mask, 'india_emp']),
                       sal_india_data.loc[mask, 'avg_salary_lyr'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(np.log10(sal_india_data['india_emp'].min()),
                             np.log10(sal_india_data['india_emp'].max()), 100)
        ax.plot(10 ** x_line, p(x_line), 'r--', linewidth=1.5, alpha=0.7, label='Trend')
    
    for _, row in sal_india_data.iterrows():
        ax.annotate(row['Company'], (row['india_emp'], row['avg_salary_lyr']),
                    textcoords="offset points", xytext=(5, 5),
                    fontsize=7, ha='left')
    ax.legend(fontsize=9)
    save_plot(plt, "50_salary_vs_india_employees.png")
    
    # ── 8.51 ── Salary vs Sub-Ratings (Small Multiples) ──
    salary_sub_map = {
        'avg_salary_sub': 'Salary (Sub-Rating)',
        'avg_wlb': 'Work-Life Balance',
        'avg_culture': 'Company Culture',
        'avg_satisfaction': 'Work Satisfaction',
        'avg_skill': 'Skill Development',
        'avg_security': 'Job Security',
        'avg_promotions': 'Promotions',
    }
    
    sal_sub_data = company_salary.dropna(subset=['avg_salary_lyr'])
    
    fig, axes = plt.subplots(3, 3, figsize=(18, 16))
    axes = axes.flatten()
    
    for i, (col, label) in enumerate(salary_sub_map.items()):
        ax = axes[i]
        sub_clean = sal_sub_data.dropna(subset=[col])
        scatter = ax.scatter(sub_clean[col], sub_clean['avg_salary_lyr'],
                             s=sub_clean['total_reviews'] / 15 + 50,
                             c=sub_clean['avg_rating'], cmap='RdYlGn', alpha=0.8,
                             edgecolors='#2c3e50', linewidth=0.8, vmin=2, vmax=5)
        ax.set_xlabel(f'{label} Rating', fontsize=10)
        ax.set_ylabel('Avg Salary (L/yr)', fontsize=10)
        ax.set_title(f'{label}', fontsize=12, fontweight='bold')
        ax.grid(True, linestyle='--', alpha=0.4)
        ax.set_xlim(sub_clean[col].min() - 0.3, sub_clean[col].max() + 0.4)
        ax.set_ylim(sub_clean['avg_salary_lyr'].min() - 5,
                    sub_clean['avg_salary_lyr'].max() + 5)
    
        # Regression
        mask = sub_clean[col].notna() & sub_clean['avg_salary_lyr'].notna()
        if mask.sum() > 2:
            z = np.polyfit(sub_clean.loc[mask, col],
                           sub_clean.loc[mask, 'avg_salary_lyr'], 1)
            p = np.poly1d(z)
            x_line = np.linspace(sub_clean[col].min(), sub_clean[col].max(), 100)
            ax.plot(x_line, p(x_line), 'r--', linewidth=1.2, alpha=0.6)
        corr_val = sub_clean[col].corr(sub_clean['avg_salary_lyr'])
        ax.text(0.95, 0.05, f'r={corr_val:.2f}', transform=ax.transAxes,
                fontsize=9, ha='right', va='bottom',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.6))
    
        for _, row in sub_clean.iterrows():
            ax.annotate(row['Company'], (row[col], row['avg_salary_lyr']),
                        textcoords="offset points", xytext=(4, 3),
                        fontsize=6, ha='left', alpha=0.85)
    
    for j in range(len(salary_sub_map), len(axes)):
        axes[j].set_visible(False)
    
    fig.suptitle('Salary vs Sub-Ratings\n(color = overall rating, size = total reviews)',
                 fontsize=16, y=1.01)
    plt.tight_layout()
    save_plot(plt, "51_salary_vs_sub_ratings.png")
    
    # ── 8.52 ── Salary vs Industry Deviation ──
    sal_dev_data = company_salary.dropna(subset=['avg_salary_lyr', 'industry_deviation'])
    
    fig, ax = plt.subplots(figsize=(11, 7))
    scatter = ax.scatter(sal_dev_data['industry_deviation'], sal_dev_data['avg_salary_lyr'],
                         s=sal_dev_data['total_reviews'] / 10 + 60,
                         c=sal_dev_data['avg_rating'], cmap='RdYlGn', alpha=0.8,
                         edgecolors='white', linewidth=1, vmin=2, vmax=5)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Average Rating', fontsize=11)
    ax.axvline(0, color='gray', linestyle='--', alpha=0.5, linewidth=1)
    ax.set_xlabel('Industry Deviation (%)', fontsize=12)
    ax.set_ylabel('Average Salary (Lakhs/Year)', fontsize=12)
    ax.set_title('Salary vs Industry Deviation\n(size = reviews, color = rating)', fontsize=14, pad=15)
    ax.grid(True, linestyle='--', alpha=0.4)
    
    # Annotate all points
    for _, row in sal_dev_data.iterrows():
        ax.annotate(row['Company'], (row['industry_deviation'], row['avg_salary_lyr']),
                    textcoords="offset points", xytext=(5, 5),
                    fontsize=7, ha='left')
    
    # Annotate quadrants
    ax.text(0.98, 0.98, 'Above Industry\nHigh Salary -> *',
            transform=ax.transAxes, fontsize=9, ha='right', va='top',
            bbox=dict(boxstyle='round', facecolor='#2ecc71', alpha=0.3))
    ax.text(0.02, 0.98, 'Below Industry\nHigh Salary',
            transform=ax.transAxes, fontsize=9, ha='left', va='top',
            bbox=dict(boxstyle='round', facecolor='#f39c12', alpha=0.3))
    ax.text(0.98, 0.02, 'Above Industry\nLow Salary',
            transform=ax.transAxes, fontsize=9, ha='right', va='bottom',
            bbox=dict(boxstyle='round', facecolor='#3498db', alpha=0.3))
    ax.text(0.02, 0.02, 'Below Industry\nLow Salary',
            transform=ax.transAxes, fontsize=9, ha='left', va='bottom',
            bbox=dict(boxstyle='round', facecolor='#e74c3c', alpha=0.3))
    
    save_plot(plt, "52_salary_vs_industry_deviation.png")
    
    # ── 8.53 ── Salary/YOE Ratio by Company (Top 20) ──
    # (Since YOE is constant at 13, this is effectively salary ÷ 13, but
    #  placed here so the metric is readily interpretable if YOE varies later)
    top_salary_per_yoe = company_salary.dropna(subset=['salary_per_yoe']).nlargest(20, 'salary_per_yoe').sort_values('salary_per_yoe')
    
    fig, ax = plt.subplots(figsize=(12, 8))
    bars = ax.barh(top_salary_per_yoe['Company'], top_salary_per_yoe['salary_per_yoe'],
                   color=plt.cm.Blues(0.3 + 0.7 * np.linspace(0, 1, len(top_salary_per_yoe))),
                   edgecolor='white')
    ax.set_xlabel('Salary per Year of Experience (Lakhs/YOE)', fontsize=12)
    ax.set_title('Top 20 Companies by Salary per Year of Experience\n(Avg Salary ÷ Years of Experience)', fontsize=14, pad=15)
    ax.grid(axis='x', linestyle='--', alpha=0.4)
    for bar, (_, row) in zip(bars, top_salary_per_yoe.iterrows()):
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
                f'Rs.{row["salary_per_yoe"]:.1f}L/YOE  (Rs.{row["avg_salary_lyr"]:.0f}L @ 13yr)',
                va='center', fontsize=8.5, fontweight='bold')
    save_plot(plt, "53_salary_per_yoe_by_company.png")
    
    # ── 8.54 ── Salary Distribution by Revenue Tier (Violin Plot) ──
    rev_tier_sal = company_salary.dropna(subset=['avg_salary_lyr', 'revenue_usd']).copy()
    rev_tier_sal['revenue_tier'] = pd.cut(
        rev_tier_sal['revenue_usd'],
        bins=[0, 1e9, 10e9, 50e9, 200e9, np.inf],
        labels=['<$1B', '$1B–$10B', '$10B–$50B', '$50B–$200B', '>$200B'],
        right=False,
    )
    
    fig, ax = plt.subplots(figsize=(12, 7))
    tier_order = ['<$1B', '$1B–$10B', '$10B–$50B', '$50B–$200B', '>$200B']
    tier_palette = sns.color_palette("YlOrRd", len(tier_order))
    sns.violinplot(data=rev_tier_sal, x='revenue_tier', y='avg_salary_lyr',
                   hue='revenue_tier', palette=tier_palette, legend=False,
                   order=tier_order, inner='quartile', ax=ax)
    sns.stripplot(data=rev_tier_sal, x='revenue_tier', y='avg_salary_lyr',
                  color='black', alpha=0.3, size=5, jitter=True, ax=ax)
    # Annotate company names on stripplot points
    for _, row in rev_tier_sal.iterrows():
        tier_idx = tier_order.index(row['revenue_tier']) if row['revenue_tier'] in tier_order else -1
        if tier_idx >= 0:
            ax.annotate(row['Company'], (tier_idx, row['avg_salary_lyr']),
                        textcoords="offset points", xytext=(0, 8),
                        fontsize=6, ha='center', alpha=0.7)
    
    ax.set_title('Salary Distribution by Company Revenue Tier\n(for ~13 YOE professionals)', fontsize=14, pad=15)
    ax.set_xlabel('Revenue Tier', fontsize=12)
    ax.set_ylabel('Average Salary (Lakhs/Year)', fontsize=12)
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    save_plot(plt, "54_salary_by_revenue_tier_violin.png")
    
    # ── 8.55 ── Salary vs Total Reviews (Scatter) ──
    sal_rev_count = company_salary.dropna(subset=['avg_salary_lyr', 'total_reviews'])
    
    fig, ax = plt.subplots(figsize=(11, 7))
    scatter = ax.scatter(sal_rev_count['total_reviews'], sal_rev_count['avg_salary_lyr'],
                         s=sal_rev_count['avg_rating'] * 50 + 30,
                         c=sal_rev_count['company_age'].fillna(20), cmap='plasma',
                         alpha=0.8, edgecolors='white', linewidth=1)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Company Age (years)', fontsize=11)
    ax.set_xscale('log')
    ax.set_xlabel('Total Reviews (log scale)', fontsize=12)
    ax.set_ylabel('Average Salary (Lakhs/Year)', fontsize=12)
    ax.set_title('Salary vs Review Volume\n(size = rating, color = company age)', fontsize=14, pad=15)
    ax.grid(True, linestyle='--', alpha=0.4)
    
    mask = sal_rev_count['total_reviews'].notna() & sal_rev_count['avg_salary_lyr'].notna()
    if mask.sum() > 2:
        z = np.polyfit(np.log10(sal_rev_count.loc[mask, 'total_reviews']),
                       sal_rev_count.loc[mask, 'avg_salary_lyr'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(np.log10(sal_rev_count['total_reviews'].min()),
                             np.log10(sal_rev_count['total_reviews'].max()), 100)
        ax.plot(10 ** x_line, p(x_line), 'r--', linewidth=1.5, alpha=0.7, label='Trend')
    
    for _, row in sal_rev_count.iterrows():
        ax.annotate(row['Company'], (row['total_reviews'], row['avg_salary_lyr']),
                    textcoords="offset points", xytext=(5, 5),
                    fontsize=7, ha='left')
    ax.legend(fontsize=9)
    save_plot(plt, "55_salary_vs_reviews.png")
    
    # ── 8.56 ── Salary vs Company Age ──
    sal_age_data = company_salary.dropna(subset=['avg_salary_lyr', 'company_age'])
    
    fig, ax = plt.subplots(figsize=(11, 7))
    scatter = ax.scatter(sal_age_data['company_age'], sal_age_data['avg_salary_lyr'],
                         s=sal_age_data['global_emp'].fillna(1000) / 30 + 60,
                         c=sal_age_data['avg_rating'], cmap='RdYlGn', alpha=0.8,
                         edgecolors='white', linewidth=1.2, vmin=2, vmax=5)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Average Rating', fontsize=11)
    ax.set_xlabel('Company Age (years since founding)', fontsize=12)
    ax.set_ylabel('Average Salary (Lakhs/Year)', fontsize=12)
    ax.set_title('Salary vs Company Age\n(size = global employees, color = rating)', fontsize=14, pad=15)
    ax.grid(True, linestyle='--', alpha=0.4)
    
    mask = sal_age_data['company_age'].notna() & sal_age_data['avg_salary_lyr'].notna()
    if mask.sum() > 2:
        z = np.polyfit(sal_age_data.loc[mask, 'company_age'],
                       sal_age_data.loc[mask, 'avg_salary_lyr'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(sal_age_data['company_age'].min(),
                             sal_age_data['company_age'].max(), 100)
        ax.plot(x_line, p(x_line), 'r--', linewidth=1.5, alpha=0.7, label='Trend')
        corr_val = sal_age_data['company_age'].corr(sal_age_data['avg_salary_lyr'])
        ax.text(0.95, 0.05, f'r={corr_val:.2f}', transform=ax.transAxes,
                fontsize=11, ha='right', va='bottom',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
    
    for _, row in sal_age_data.iterrows():
        ax.annotate(row['Company'], (row['company_age'], row['avg_salary_lyr']),
                    textcoords="offset points", xytext=(5, 5),
                    fontsize=7, ha='left')
    ax.legend(fontsize=9)
    save_plot(plt, "56_salary_vs_company_age.png")
    
    # ── 8.57 ── Salary vs Work-Life Balance (colored by Rating, bubble = revenue) ──
    sal_wlb_data = company_salary.dropna(subset=['avg_salary_lyr', 'avg_wlb'])
    
    fig, ax = plt.subplots(figsize=(11, 7))
    bubble_sizes = sal_wlb_data['revenue_usd'].fillna(1e9).apply(
        lambda x: np.log10(x + 1) * 25 + 40
    )
    scatter = ax.scatter(sal_wlb_data['avg_wlb'], sal_wlb_data['avg_salary_lyr'],
                         s=bubble_sizes,
                         c=sal_wlb_data['avg_rating'], cmap='RdYlGn', alpha=0.8,
                         edgecolors='white', linewidth=1, vmin=2, vmax=5)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Average Rating', fontsize=11)
    ax.set_xlabel('Work-Life Balance Rating', fontsize=12)
    ax.set_ylabel('Average Salary (Lakhs/Year)', fontsize=12)
    ax.set_title('Salary vs Work-Life Balance\n(size = revenue, color = rating)\n"Can you have both high salary AND good WLB?"',
                 fontsize=14, pad=15)
    ax.grid(True, linestyle='--', alpha=0.4)
    
    # Quadrant reference lines
    ax.axvline(sal_wlb_data['avg_wlb'].median(), color='gray', linestyle='--',
               alpha=0.4, linewidth=1)
    ax.axhline(sal_wlb_data['avg_salary_lyr'].median(), color='gray', linestyle='--',
               alpha=0.4, linewidth=1)
    
    # Quadrant labels
    ax.text(0.98, 0.98, 'HIGH Salary\nGOOD WLB [BEST]', transform=ax.transAxes,
            fontsize=9, ha='right', va='top', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='#2ecc71', alpha=0.25))
    ax.text(0.02, 0.98, 'LOW Salary\nGOOD WLB', transform=ax.transAxes,
            fontsize=9, ha='left', va='top',
            bbox=dict(boxstyle='round', facecolor='#f39c12', alpha=0.25))
    ax.text(0.98, 0.02, 'HIGH Salary\nPOOR WLB [!]', transform=ax.transAxes,
            fontsize=9, ha='right', va='bottom',
            bbox=dict(boxstyle='round', facecolor='#e74c3c', alpha=0.25))
    ax.text(0.02, 0.02, 'LOW Salary\nPOOR WLB', transform=ax.transAxes,
            fontsize=9, ha='left', va='bottom',
            bbox=dict(boxstyle='round', facecolor='#95a5a6', alpha=0.25))
    
    for _, row in sal_wlb_data.iterrows():
        ax.annotate(row['Company'], (row['avg_wlb'], row['avg_salary_lyr']),
                    textcoords="offset points", xytext=(5, 5),
                    fontsize=7, ha='left')
    # Correlation
    corr_val = sal_wlb_data['avg_wlb'].corr(sal_wlb_data['avg_salary_lyr'])
    ax.text(0.5, 0.01, f'Correlation (WLB vs Salary): r={corr_val:.2f}',
            transform=ax.transAxes, fontsize=10, ha='center', fontstyle='italic',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
    save_plot(plt, "57_salary_vs_wlb_quadrant.png")
    
    # ── 8.58 ── Comprehensive Correlation Heatmap with Salary ──
    salary_corr_cols = [
        'avg_salary_lyr', 'avg_rating', 'total_reviews',
        'avg_salary_sub', 'avg_wlb', 'avg_culture', 'avg_satisfaction',
        'avg_skill', 'avg_security', 'avg_promotions',
        'industry_deviation', 'global_emp', 'india_emp', 'company_age',
    ]
    salary_corr_labels = [
        'Salary (L/Yr)', 'Rating', 'Reviews',
        'Salary *', 'WLB *', 'Culture *', 'Satisfaction *',
        'Skill *', 'Security *', 'Promotions *',
        'Ind. Dev%', 'Global Emp', 'India Emp', 'Age (yrs)',
    ]
    
    salary_corr_df = company_salary[salary_corr_cols].copy()
    # Log-transform scale variables
    for col in ['global_emp', 'india_emp', 'total_reviews']:
        salary_corr_df[col] = np.log10(salary_corr_df[col].replace(0, np.nan))
    salary_corr_df.columns = salary_corr_labels
    salary_corr = salary_corr_df.corr()
    
    fig, ax = plt.subplots(figsize=(14, 12))
    mask = np.triu(np.ones_like(salary_corr, dtype=bool), k=1)
    sns.heatmap(salary_corr, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
                square=True, ax=ax, mask=mask, vmin=-1, vmax=1,
                annot_kws={'fontsize': 8}, linewidths=0.5,
                cbar_kws={'label': 'Pearson r (log₁₀ for scale vars)'})
    ax.set_title('Salary & Experience: Comprehensive Correlation Matrix\n(log₁₀ transformed for employee count & review variables)',
                 fontsize=14, pad=18)
    ax.tick_params(axis='both', labelsize=9)
    save_plot(plt, "58_salary_correlation_heatmap.png")
    
    print(f"\nSalary & Experience section plots saved (46–58).")
    print(f"  ✓ Section 8 complete — 13 plots saved.")

if __name__ == "__main__":
    run()
