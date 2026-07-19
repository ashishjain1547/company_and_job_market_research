"""
Section 7 script — auto-extracted from analyze_20260719.py.
Run standalone:  python section_07_revenue.py
Or via runner:   from section_07_revenue import run; run()
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from shared_config import (df, company_demo, save_plot, _section, COLORS, SUB_RATINGS, current_year, _rev_fmt, OUTPUT_DIR)

def run():
    _section("SECTION 7: Revenue Analysis (35-45)")

    # Revenue data already parsed & merged into company_demo by shared_config.
    # Build the working subset for Section 7 plots.
    rev_data = company_demo[company_demo['has_revenue']].copy()
    rev_data['revenue_per_employee'] = (
        rev_data['revenue_usd'] / rev_data['global_emp']
    )
    rev_data['revenue_per_india_employee'] = (
        rev_data['revenue_usd'] / rev_data['india_emp']
    )

    num_disclosed = company_demo['has_revenue'].sum()
    num_total = len(company_demo)
    print(
        f"\nRevenue parsed: {num_disclosed}/{num_total} companies "
        f"have disclosed revenue"
    )
    
    # ── 7.35 ── Revenue Distribution (Histogram, log scale) ──
    fig, ax = plt.subplots(figsize=(10, 6))
    log_rev = np.log10(rev_data['revenue_usd'].dropna())
    sns.histplot(log_rev, bins=15, kde=True, color='#2ecc71',
                 edgecolor='#1e8449', ax=ax)
    ax.set_title('Distribution of Annual Revenue (Log Scale)',
                 fontsize=14, pad=15)
    ax.set_xlabel('Log₁₀(Annual Revenue in USD)', fontsize=12)
    ax.set_ylabel('Number of Companies', fontsize=12)
    # Add original-scale annotations on the x-axis
    tick_positions = [6, 7, 8, 9, 10, 11, 12]
    tick_labels = ['$1M', '$10M', '$100M', '$1B', '$10B', '$100B', '$1T']
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, fontsize=9)
    ax.axvline(log_rev.median(), color='red', linestyle='--', linewidth=2,
               label=f'Median: {_rev_fmt(rev_data["revenue_usd"].median())}')
    ax.legend(fontsize=10)
    save_plot(plt, "35_revenue_distribution_hist.png")
    
    # ── 7.36 ── Top Companies by Annual Revenue (Horizontal Bar) ──
    top_rev = rev_data.nlargest(20, 'revenue_usd').sort_values('revenue_usd')
    
    fig, ax = plt.subplots(figsize=(12, 8))
    rev_colors = plt.cm.YlOrRd(0.2 + 0.7 * np.linspace(0, 1, len(top_rev)))
    bars = ax.barh(top_rev['Company'], top_rev['revenue_usd'],
                   color=rev_colors, edgecolor='white')
    ax.set_xscale('log')
    ax.set_xlabel('Annual Revenue (USD, log scale)', fontsize=12)
    ax.set_title('Top Companies by Annual Revenue (as of Jun 2026)',
                 fontsize=14, pad=15)
    ax.grid(axis='x', linestyle='--', alpha=0.4)
    for bar, (_, row) in zip(bars, top_rev.iterrows()):
        ax.text(bar.get_width() * 1.02, bar.get_y() + bar.get_height() / 2,
                f'{_rev_fmt(row["revenue_usd"]):>6s}  *{row["avg_rating"]:.1f}',
                va='center', fontsize=9, fontweight='bold')
    save_plot(plt, "36_top_companies_by_revenue.png")
    
    # ── 7.37 ── Revenue vs Rating (Scatter, bubble = global employees) ──
    fig, ax = plt.subplots(figsize=(12, 7))
    scatter = ax.scatter(
        rev_data['revenue_usd'], rev_data['avg_rating'],
        s=rev_data['global_emp'].fillna(1000) / 35 + 80,
        c=rev_data['company_age'].fillna(20), cmap='viridis',
        alpha=0.8, edgecolors='#2c3e50', linewidth=1.2,
    )
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Company Age (years)', fontsize=11)
    ax.set_xscale('log')
    ax.set_xlabel('Annual Revenue (USD, log scale)', fontsize=12)
    ax.set_ylabel('Average Rating', fontsize=12)
    ax.set_title(
        'Revenue vs Rating\n'
        '(bubble size = global employees, color = company age)',
        fontsize=14, pad=15,
    )
    ax.grid(True, linestyle='--', alpha=0.4)
    # Trend line
    mask = rev_data['revenue_usd'].notna() & rev_data['avg_rating'].notna()
    if mask.sum() > 2:
        z = np.polyfit(np.log10(rev_data.loc[mask, 'revenue_usd']),
                       rev_data.loc[mask, 'avg_rating'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(np.log10(rev_data['revenue_usd'].min()),
                             np.log10(rev_data['revenue_usd'].max()), 100)
        ax.plot(10 ** x_line, p(x_line), 'r--', linewidth=1.5, alpha=0.7,
                label='Trend')
    # Annotate all points
    for _, row in rev_data.iterrows():
        ax.annotate(row['Company'], (row['revenue_usd'], row['avg_rating']),
                    textcoords="offset points", xytext=(6, 6),
                    fontsize=7, ha='left')
    ax.legend(fontsize=9)
    ax.set_ylim(rev_data['avg_rating'].min() - 0.3,
                rev_data['avg_rating'].max() + 0.4)
    save_plot(plt, "37_revenue_vs_rating.png")
    
    # ── 7.38 ── Revenue vs Global Employee Count (Scatter with trend) ──
    both_data = rev_data[rev_data['global_emp'].notna()]
    
    fig, ax = plt.subplots(figsize=(10, 8))
    scatter = ax.scatter(
        both_data['global_emp'], both_data['revenue_usd'],
        s=both_data['avg_rating'] * 40 + 20,
        c=both_data['india_pct_of_global'].fillna(50), cmap='coolwarm',
        alpha=0.85, edgecolors='#2c3e50', linewidth=1,
        vmin=0, vmax=100,
    )
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('India Workforce %', fontsize=11)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Global Employee Count (log scale)', fontsize=12)
    ax.set_ylabel('Annual Revenue (USD, log scale)', fontsize=12)
    ax.set_title(
        'Revenue vs Global Employees\n'
        '(color = India workforce %, size = rating)',
        fontsize=14, pad=15,
    )
    ax.grid(True, linestyle='--', alpha=0.4)
    
    # Revenue-per-employee reference lines
    emp_min = both_data['global_emp'].min() * 0.8
    emp_max = both_data['global_emp'].max() * 1.2
    emp_range = np.logspace(np.log10(emp_min), np.log10(emp_max), 100)
    for rpe_usd, label, ls, col in [
        (50_000, '$50K/emp', ':', '#95a5a6'),
        (200_000, '$200K/emp', '--', '#7f8c8d'),
        (1_000_000, '$1M/emp', '-.', '#555'),
    ]:
        ax.plot(emp_range, rpe_usd * emp_range, ls, color=col, alpha=0.5,
                linewidth=1, label=label)
    
    for _, row in both_data.iterrows():
        ax.annotate(row['Company'], (row['global_emp'], row['revenue_usd']),
                    textcoords="offset points", xytext=(7, 5),
                    fontsize=7, ha='left')
    ax.legend(fontsize=9, title='Revenue/Emp')
    save_plot(plt, "38_revenue_vs_employees.png")
    
    # ── 7.39 ── Revenue per Employee (Bar Chart, efficiency metric) ──
    rpe_data = rev_data[
        rev_data['revenue_per_employee'].notna()
        & (rev_data['revenue_per_employee'] > 0)
    ].sort_values('revenue_per_employee')
    
    fig, ax = plt.subplots(figsize=(10, 7))
    rpe_colors = plt.cm.RdYlGn(
        0.15 + 0.7 * np.linspace(0, 1, len(rpe_data))
    )
    bars = ax.barh(rpe_data['Company'], rpe_data['revenue_per_employee'],
                   color=rpe_colors, edgecolor='white')
    ax.set_xscale('log')
    ax.set_xlabel('Revenue per Global Employee (USD, log scale)', fontsize=12)
    ax.set_title(
        'Revenue per Employee (Efficiency Proxy)\n'
        'Higher = more revenue generated per head',
        fontsize=14, pad=15,
    )
    ax.grid(axis='x', linestyle='--', alpha=0.4)
    ax.axvline(50_000, color='#e74c3c', linestyle='--', linewidth=1.5,
               alpha=0.6, label='$50K/emp (typical IT services)')
    for bar, (_, row) in zip(bars, rpe_data.iterrows()):
        rpe_k = row['revenue_per_employee'] / 1_000
        ax.text(row['revenue_per_employee'] * 1.05,
                bar.get_y() + bar.get_height() / 2,
                f'${rpe_k:,.0f}K', va='center', fontsize=9, fontweight='bold')
    ax.legend(fontsize=9, loc='lower right')
    save_plot(plt, "39_revenue_per_employee.png")
    
    # ── 7.40 ── Revenue vs Total Reviews (Scatter) ──
    fig, ax = plt.subplots(figsize=(10, 7))
    scatter = ax.scatter(
        rev_data['revenue_usd'], rev_data['total_reviews'],
        s=rev_data['avg_rating'] * 50 + 30,
        c=rev_data['company_age'].fillna(20), cmap='plasma',
        alpha=0.8, edgecolors='white', linewidth=1,
    )
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Company Age (years)', fontsize=11)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Annual Revenue (USD, log scale)', fontsize=12)
    ax.set_ylabel('Total Reviews (log scale)', fontsize=12)
    ax.set_title(
        'Revenue vs Review Volume\n'
        '(size = rating, color = company age)',
        fontsize=14, pad=15,
    )
    ax.grid(True, linestyle='--', alpha=0.4)
    # Trend line
    mask = (rev_data['revenue_usd'].notna()
            & (rev_data['total_reviews'] > 0))
    if mask.sum() > 2:
        z = np.polyfit(np.log10(rev_data.loc[mask, 'revenue_usd']),
                       np.log10(rev_data.loc[mask, 'total_reviews']), 1)
        p = np.poly1d(z)
        x_line = np.linspace(np.log10(rev_data['revenue_usd'].min()),
                             np.log10(rev_data['revenue_usd'].max()), 100)
        ax.plot(10 ** x_line, 10 ** p(x_line), 'k--', linewidth=1.5,
                alpha=0.6, label=f'Slope: {z[0]:.2f}')
    for _, row in rev_data.iterrows():
        ax.annotate(row['Company'],
                    (row['revenue_usd'], row['total_reviews']),
                    textcoords="offset points", xytext=(5, 5),
                    fontsize=7, ha='left')
    ax.legend(fontsize=9)
    save_plot(plt, "40_revenue_vs_reviews.png")
    
    # ── 7.41 ── Revenue per Employee vs India Workforce % ──
    rpe_pct_data = rev_data[
        rev_data['revenue_per_employee'].notna()
        & rev_data['india_pct_of_global'].notna()
    ]
    
    fig, ax = plt.subplots(figsize=(10, 7))
    scatter = ax.scatter(
        rpe_pct_data['india_pct_of_global'],
        rpe_pct_data['revenue_per_employee'],
        s=rpe_pct_data['total_reviews'] / 10 + 50,
        c=rpe_pct_data['avg_rating'], cmap='RdYlGn', alpha=0.8,
        edgecolors='#2c3e50', linewidth=1,
    )
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Average Rating', fontsize=11)
    ax.set_yscale('log')
    ax.set_xlabel('India Workforce as % of Global', fontsize=12)
    ax.set_ylabel('Revenue per Employee (USD, log scale)', fontsize=12)
    ax.set_title(
        'Revenue Efficiency vs India Workforce Concentration\n'
        '(size = reviews, color = rating)',
        fontsize=14, pad=15,
    )
    ax.axvline(50, color='#7f8c8d', linestyle='--', alpha=0.5,
               label='50% India workforce')
    ax.grid(True, linestyle='--', alpha=0.4)
    for _, row in rpe_pct_data.iterrows():
        ax.annotate(row['Company'],
                    (row['india_pct_of_global'],
                     row['revenue_per_employee']),
                    textcoords="offset points", xytext=(6, 5),
                    fontsize=7, ha='left')
    ax.legend(fontsize=9)
    save_plot(plt, "41_revenue_per_emp_vs_india_pct.png")
    
    # ── 7.42 ── Revenue vs Company Age ──
    age_rev_data = rev_data[rev_data['company_age'].notna()]
    
    fig, ax = plt.subplots(figsize=(10, 7))
    scatter = ax.scatter(
        age_rev_data['company_age'], age_rev_data['revenue_usd'],
        s=age_rev_data['global_emp'].fillna(1000) / 30 + 60,
        c=age_rev_data['avg_rating'], cmap='RdYlGn', alpha=0.8,
        edgecolors='white', linewidth=1.2,
    )
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Average Rating', fontsize=11)
    ax.set_yscale('log')
    ax.set_xlabel('Company Age (years since founding)', fontsize=12)
    ax.set_ylabel('Annual Revenue (USD, log scale)', fontsize=12)
    ax.set_title(
        'Revenue vs Company Age\n'
        '(size = global employees, color = rating)',
        fontsize=14, pad=15,
    )
    ax.grid(True, linestyle='--', alpha=0.4)
    # Trend line
    mask = (age_rev_data['company_age'].notna()
            & age_rev_data['revenue_usd'].notna())
    if mask.sum() > 2:
        z = np.polyfit(age_rev_data.loc[mask, 'company_age'],
                       np.log10(age_rev_data.loc[mask, 'revenue_usd']), 1)
        p = np.poly1d(z)
        x_line = np.linspace(age_rev_data['company_age'].min(),
                             age_rev_data['company_age'].max(), 100)
        ax.plot(x_line, 10 ** p(x_line), 'k--', linewidth=1.5, alpha=0.6,
                label='Trend')
    for _, row in age_rev_data.iterrows():
        ax.annotate(row['Company'],
                    (row['company_age'], row['revenue_usd']),
                    textcoords="offset points", xytext=(6, 5),
                    fontsize=7, ha='left')
    ax.legend(fontsize=9)
    save_plot(plt, "42_revenue_vs_company_age.png")
    
    # ── 7.43 ── Revenue Category Breakdown (Pie + Counts) ──
    bins_rev = [0, 1e9, 10e9, 50e9, 200e9, np.inf]
    labels_rev = ['<$1B', '$1B–$10B', '$10B–$50B', '$50B–$200B', '>$200B']
    rev_data['revenue_tier'] = pd.cut(
        rev_data['revenue_usd'], bins=bins_rev, labels=labels_rev, right=False,
    )
    tier_counts = (
        rev_data['revenue_tier'].value_counts()
        .reindex(labels_rev).fillna(0).astype(int)
    )
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    
    # Left: Pie chart
    tier_colors = sns.color_palette("YlOrRd", len(labels_rev))
    wedges, texts, autotexts = axes[0].pie(
        tier_counts.values, labels=None, autopct='%1.1f%%',
        startangle=90, colors=tier_colors,
        explode=[0.02] * len(labels_rev),
    )
    axes[0].set_title('Revenue Tier Distribution', fontsize=13)
    
    # Right: Bar chart with average rating per tier
    tier_avg_rating = (
        rev_data.groupby('revenue_tier', observed=False)['avg_rating']
        .mean().reindex(labels_rev)
    )
    bars = axes[1].bar(labels_rev, tier_counts.values, color=tier_colors,
                       edgecolor='white')
    axes[1].set_title('Companies per Revenue Tier', fontsize=13)
    axes[1].set_xlabel('Revenue Tier', fontsize=11)
    axes[1].set_ylabel('Number of Companies', fontsize=11)
    for bar, count, rating in zip(bars, tier_counts.values,
                                   tier_avg_rating.values):
        if count > 0:
            axes[1].text(bar.get_x() + bar.get_width() / 2,
                         bar.get_height() + 0.15,
                         f'n={count}\n*{rating:.1f}',
                         ha='center', fontsize=10, fontweight='bold')
    
    # Combined legend
    axes[0].legend(
        wedges,
        [f'{lbl} (n={cnt})' for lbl, cnt in zip(labels_rev, tier_counts.values)],
        title="Revenue Tier", loc="center left",
        bbox_to_anchor=(1, 0.5), fontsize=9,
    )
    
    fig.suptitle('Revenue Segmentation Analysis', fontsize=15, y=1.02)
    plt.tight_layout()
    save_plot(plt, "43_revenue_tier_breakdown.png")
    
    # ── 7.44 ── Revenue vs Sub-Ratings (Small Multiples) ──
    sub_rating_cols_map = {
        'avg_culture': 'Culture',
        'avg_salary': 'Salary',
        'avg_wlb': 'Work-Life Balance',
        'avg_satisfaction': 'Work Satisfaction',
        'avg_skill': 'Skill Development',
        'avg_security': 'Job Security',
        'avg_promotions': 'Promotions',
    }
    
    fig, axes = plt.subplots(3, 3, figsize=(18, 16))
    axes = axes.flatten()
    
    for i, (col, label) in enumerate(sub_rating_cols_map.items()):
        ax = axes[i]
        sub_data = rev_data[rev_data[col].notna()]
        scatter = ax.scatter(
            sub_data['revenue_usd'], sub_data[col],
            s=sub_data['total_reviews'] / 25 + 40,
            c=sub_data['avg_rating'], cmap='RdYlGn', alpha=0.8,
            edgecolors='#2c3e50', linewidth=0.8, vmin=2, vmax=5,
        )
        ax.set_xscale('log')
        ax.set_xlabel('Revenue (USD, log)', fontsize=9)
        ax.set_ylabel(f'{label} Rating', fontsize=9)
        ax.set_title(f'{label}', fontsize=11, fontweight='bold')
        ax.grid(True, linestyle='--', alpha=0.4)
        ax.set_ylim(sub_data[col].min() - 0.4, sub_data[col].max() + 0.5)
    
        # Trend line
        mask = sub_data['revenue_usd'].notna() & sub_data[col].notna()
        if mask.sum() > 2:
            z = np.polyfit(np.log10(sub_data.loc[mask, 'revenue_usd']),
                           sub_data.loc[mask, col], 1)
            p = np.poly1d(z)
            x_line = np.linspace(np.log10(sub_data['revenue_usd'].min()),
                                 np.log10(sub_data['revenue_usd'].max()), 100)
            ax.plot(10 ** x_line, p(x_line), 'r--', linewidth=1, alpha=0.6)
    
        # Correlation annotation
        corr_val = np.log10(sub_data['revenue_usd']).corr(sub_data[col])
        ax.text(0.95, 0.05, f'r={corr_val:.2f}', transform=ax.transAxes,
                fontsize=9, ha='right', va='bottom',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.6))
    
        # Annotate outliers
        for _, row in sub_data.iterrows():
            ax.annotate(row['Company'], (row['revenue_usd'], row[col]),
                        textcoords="offset points", xytext=(4, 3),
                        fontsize=6, ha='left', alpha=0.9)
    
    # Hide extra subplots
    for j in range(len(sub_rating_cols_map), len(axes)):
        axes[j].set_visible(False)
    
    fig.suptitle(
        'Revenue vs Sub-Ratings\n'
        '(color = overall rating, size = total reviews)',
        fontsize=16, y=1.01,
    )
    plt.tight_layout()
    save_plot(plt, "44_revenue_vs_sub_ratings.png")
    
    # ── 7.45 ── Summary: Revenue Correlation Heatmap ──
    rev_corr_cols = [
        'revenue_usd', 'avg_rating', 'total_reviews',
        'global_emp', 'india_emp', 'india_pct_of_global', 'company_age',
    ]
    rev_corr_labels = [
        'Revenue', 'Rating', 'Reviews', 'Global Emp',
        'India Emp', 'India %', 'Age (yrs)',
    ]
    
    rev_corr_data = company_demo[rev_corr_cols].copy()
    # Log-transform revenue and employee counts for correlation
    for col in ['revenue_usd', 'global_emp', 'india_emp', 'total_reviews']:
        rev_corr_data[col] = np.log10(rev_corr_data[col].replace(0, np.nan))
    rev_corr_data.columns = rev_corr_labels
    rev_corr = rev_corr_data.corr()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    mask = np.triu(np.ones_like(rev_corr, dtype=bool), k=1)
    sns.heatmap(rev_corr, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
                square=True, ax=ax, mask=mask, vmin=-1, vmax=1,
                annot_kws={'fontsize': 10}, linewidths=0.5,
                cbar_kws={'label': 'Pearson r (log-transformed)'})
    ax.set_title(
        'Revenue & Business Scale Correlation Matrix\n'
        '(log₁₀ transformed for scale variables)',
        fontsize=13, pad=15,
    )
    ax.tick_params(axis='both', labelsize=10)
    save_plot(plt, "45_revenue_correlation_heatmap.png")
    
    print(f"\nRevenue section plots saved (35–45).")
    print(f"  ✓ Section 7 complete — 11 plots saved.")

if __name__ == "__main__":
    run()
