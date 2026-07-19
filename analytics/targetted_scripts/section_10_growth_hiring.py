"""
Section 10 script — auto-extracted from analyze_20260719.py.
Run standalone:  python section_10_growth_hiring.py
Or via runner:   from section_10_growth_hiring import run; run()
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from shared_config import df, company_demo, save_plot, _section, COLORS, SUB_RATINGS, current_year, OUTPUT_DIR

def run():
    _section("SECTION 10: Employee Growth & Hiring Trends (75-91)")
    
    # These names match the aggregated columns (right side of .agg call below)
    GROWTH_COLS = ['growth_6m', 'growth_1y', 'growth_2y']
    HIRING_COLS = ['hiring_trend_6m', 'new_hires_6m']
    
    # Build company-level growth aggregates (latest snapshot per company)
    company_growth = df.groupby('Company').agg(
        growth_6m=('Employee Count Growth 6M %', 'first'),
        growth_1y=('Employee Count Growth 1Y %', 'first'),
        growth_2y=('Employee Count Growth 2Y %', 'first'),
        hiring_trend_6m=('Hiring Trend (6M)', 'first'),
        new_hires_6m=('New Hires (6M)', 'first'),
        avg_rating=('Rating', 'mean'),
        total_reviews=('#Reviews', 'sum'),
        global_emp=('Global Employee Count', 'first'),
        india_emp=('India Employee Count', 'first'),
        company_age=('Founded in', 'first'),
        avg_salary_lyr=('Avg Salary (L/Yr)', 'mean'),
        avg_culture=('Company Culture', 'mean'),
        avg_salary_sub=('Salary', 'mean'),
        avg_wlb=('Work-Life Balance', 'mean'),
        avg_satisfaction=('Work Satisfaction', 'mean'),
        avg_skill=('Skill Development', 'mean'),
        avg_security=('Job Security', 'mean'),
        avg_promotions=('Promotions', 'mean'),
        median_tenure=('Median current employee tenure (in years)', 'first'),
        industry_deviation=('Industry level insights (%: -100 (below industry\'s average) to 100)', 'mean'),
    ).reset_index()
    
    # Merge revenue
    company_growth['revenue_usd'] = company_growth['Company'].map(
        lambda c: company_demo.set_index('Company')['revenue_usd'].get(c)
    )
    company_growth['company_age'] = current_year - company_growth['company_age']
    
    # Print summary stats (use aggregated column names, not original Excel names)
    growth_agg_cols = ['growth_6m', 'growth_1y', 'growth_2y', 'hiring_trend_6m', 'new_hires_6m']
    for col in growth_agg_cols:
        clean = company_growth[col].dropna()
        if len(clean) > 0:
            print(f"  {col}: n={len(clean)}, "
                  f"min={clean.min():.1f}, max={clean.max():.1f}, "
                  f"median={clean.median():.1f}, mean={clean.mean():.1f}")
    
    # ── 10.75 ── Employee Growth Distribution: 6M vs 1Y vs 2Y (Overlaid KDE) ──
    fig, ax = plt.subplots(figsize=(11, 6))
    growth_palette = ['#e74c3c', '#f39c12', '#2ecc71']
    growth_labels = ['6-Month Growth %', '1-Year Growth %', '2-Year Growth %']
    
    for col, color, label in zip(GROWTH_COLS, growth_palette, growth_labels):
        clean = company_growth[col].dropna()
        if len(clean) > 1:
            sns.kdeplot(clean, color=color, linewidth=2.5, label=label, ax=ax, fill=True, alpha=0.12)
    
    ax.axvline(0, color='black', linestyle='-', linewidth=1, alpha=0.3)
    ax.set_title('Distribution of Employee Count Growth Rates\n(6-Month, 1-Year, 2-Year Horizons)', fontsize=14, pad=15)
    ax.set_xlabel('Employee Count Growth (%)', fontsize=12)
    ax.set_ylabel('Density', fontsize=12)
    ax.legend(fontsize=11)
    
    # Add median markers
    for col, color, label, y_offset in zip(GROWTH_COLS, growth_palette, growth_labels, [0.85, 0.78, 0.71]):
        med = company_growth[col].median()
        if not pd.isna(med):
            ax.axvline(med, color=color, linestyle='--', linewidth=1.5, alpha=0.7)
            ax.text(med, ax.get_ylim()[1] * y_offset, f'{label.split()[0]} median: {med:+.1f}%',
                    color=color, fontsize=9, fontweight='bold', rotation=90, va='top')
    
    ax.grid(True, linestyle='--', alpha=0.3)
    save_plot(plt, "75_employee_growth_distribution.png")
    
    # ── 10.76 ── Top Companies by Employee Growth (Grouped Bar: 6M, 1Y, 2Y) ──
    growth_ranked = company_growth.dropna(subset=['growth_2y']).nlargest(15, 'growth_2y').sort_values('growth_2y')
    
    fig, ax = plt.subplots(figsize=(14, 8))
    x = np.arange(len(growth_ranked))
    width = 0.25
    bars1 = ax.barh(x - width, growth_ranked['growth_6m'], width,
                    label='6-Month Growth %', color='#e74c3c', edgecolor='white', alpha=0.85)
    bars2 = ax.barh(x, growth_ranked['growth_1y'], width,
                    label='1-Year Growth %', color='#f39c12', edgecolor='white', alpha=0.85)
    bars3 = ax.barh(x + width, growth_ranked['growth_2y'], width,
                    label='2-Year Growth %', color='#2ecc71', edgecolor='white', alpha=0.85)
    
    ax.set_yticks(x)
    ax.set_yticklabels(growth_ranked['Company'], fontsize=10)
    ax.set_xlabel('Employee Count Growth (%)', fontsize=12)
    ax.set_title('Top 15 Companies by Employee Headcount Growth\n(3 time horizons compared)', fontsize=14, pad=15)
    ax.legend(fontsize=10, loc='lower right')
    ax.axvline(0, color='black', linewidth=0.8)
    ax.grid(axis='x', linestyle='--', alpha=0.3)
    
    # Annotate 2Y growth values
    for bar, (_, row) in zip(bars3, growth_ranked.iterrows()):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                f'*{row["avg_rating"]:.1f}', va='center', fontsize=8, fontweight='bold', color='#2c3e50')
    save_plot(plt, "76_top_companies_by_growth.png")
    
    # ── 10.77 ── Employee Growth vs Overall Rating (Scatter, 3 horizons as small multiples) ──
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    growth_vs_rating_map = [
        ('growth_6m', '6-Month Growth %', axes[0]),
        ('growth_1y', '1-Year Growth %', axes[1]),
        ('growth_2y', '2-Year Growth %', axes[2]),
    ]
    
    for col, label, ax in growth_vs_rating_map:
        plot_data = company_growth.dropna(subset=[col, 'avg_rating'])
        scatter = ax.scatter(plot_data['avg_rating'], plot_data[col],
                             s=plot_data['total_reviews'] / 10 + 50,
                             c=plot_data['company_age'].fillna(20), cmap='viridis',
                             alpha=0.8, edgecolors='#2c3e50', linewidth=0.8)
        ax.axhline(0, color='gray', linestyle='--', alpha=0.4, linewidth=1)
        ax.set_xlabel('Average Overall Rating', fontsize=11)
        ax.set_ylabel(label, fontsize=11)
        ax.set_title(label, fontsize=13, fontweight='bold')
        ax.grid(True, linestyle='--', alpha=0.3)
    
        # Trend line
        mask = plot_data['avg_rating'].notna() & plot_data[col].notna()
        if mask.sum() > 2:
            z = np.polyfit(plot_data.loc[mask, 'avg_rating'], plot_data.loc[mask, col], 1)
            p = np.poly1d(z)
            x_line = np.linspace(plot_data['avg_rating'].min(), plot_data['avg_rating'].max(), 100)
            ax.plot(x_line, p(x_line), 'r--', linewidth=1.5, alpha=0.7)
        corr_val = plot_data['avg_rating'].corr(plot_data[col])
        ax.text(0.95, 0.05, f'r={corr_val:.2f}', transform=ax.transAxes,
                fontsize=10, ha='right', va='bottom',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.6))
    
        # Annotate outliers
        for _, row in plot_data.iterrows():
            if abs(row[col]) > plot_data[col].std() * 1.5 or row['avg_rating'] > 4.2 or row['avg_rating'] < 2.5:
                ax.annotate(row['Company'], (row['avg_rating'], row[col]),
                            textcoords="offset points", xytext=(5, 5),
                            fontsize=6, ha='left', alpha=0.85)
    
    # Shared colorbar
    cbar = fig.colorbar(scatter, ax=axes, orientation='vertical', fraction=0.02, pad=0.04)
    cbar.set_label('Company Age (years)', fontsize=11)
    
    fig.suptitle('Employee Growth vs Overall Rating\n(size = total reviews, color = company age)\n"Are higher-rated companies growing faster?"',
                 fontsize=16, y=1.03)
    plt.tight_layout()
    save_plot(plt, "77_growth_vs_rating_small_multiples.png")
    
    # ── 10.78 ── Growth Acceleration/Deceleration: 6M vs 2Y (Scatter) ──
    growth_compare = company_growth.dropna(subset=['growth_6m', 'growth_2y'])
    
    fig, ax = plt.subplots(figsize=(10, 8))
    # Reference line: identical growth
    all_vals = pd.concat([growth_compare['growth_6m'], growth_compare['growth_2y']])
    min_val, max_val = all_vals.min() - 5, all_vals.max() + 5
    ax.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.3, linewidth=1, label='Equal growth')
    ax.fill_between([min_val, max_val], [min_val, max_val], max_val + 20,
                    alpha=0.05, color='green', label='Accelerating (2Y > 6M)')
    ax.fill_between([min_val, max_val], min_val - 20, [min_val, max_val],
                    alpha=0.05, color='red', label='Decelerating (6M > 2Y)')
    
    scatter = ax.scatter(growth_compare['growth_2y'], growth_compare['growth_6m'],
                         s=growth_compare['global_emp'].fillna(1000) / 30 + 60,
                         c=growth_compare['avg_rating'], cmap='RdYlGn', alpha=0.8,
                         edgecolors='#2c3e50', linewidth=1, vmin=2, vmax=5)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Average Rating', fontsize=11)
    
    ax.set_xlabel('2-Year Employee Growth (%)', fontsize=12)
    ax.set_ylabel('6-Month Employee Growth (%)', fontsize=12)
    ax.set_title('Growth Momentum: Short-Term (6M) vs Long-Term (2Y)\n(size = global employees, color = rating)\n"Who is accelerating vs. decelerating?"',
                 fontsize=14, pad=15)
    ax.grid(True, linestyle='--', alpha=0.3)
    
    for _, row in growth_compare.iterrows():
        ax.annotate(row['Company'], (row['growth_2y'], row['growth_6m']),
                    textcoords="offset points", xytext=(5, 5),
                    fontsize=7, ha='left')
    ax.legend(fontsize=9, loc='upper left')
    save_plot(plt, "78_growth_momentum_6m_vs_2y.png")
    
    # ── 10.79 ── Hiring Trend Distribution ──
    hiring_trend_clean = company_growth['hiring_trend_6m'].dropna()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(hiring_trend_clean, bins=20, kde=True, color='#8e44ad',
                 edgecolor='#6c3483', ax=ax)
    ax.axvline(hiring_trend_clean.mean(), color='red', linestyle='--', linewidth=2,
               label=f'Mean: {hiring_trend_clean.mean():+.1f}%')
    ax.axvline(hiring_trend_clean.median(), color='#e67e22', linestyle='--', linewidth=2,
               label=f'Median: {hiring_trend_clean.median():+.1f}%')
    ax.axvline(0, color='black', linestyle='-', linewidth=1, alpha=0.4)
    ax.set_title('Distribution of Hiring Trend (6-Month)\n% Change in New Hires: 6 Months Ago vs Last Month', fontsize=14, pad=15)
    ax.set_xlabel('Hiring Trend (%)', fontsize=12)
    ax.set_ylabel('Number of Companies', fontsize=12)
    ax.legend(fontsize=10)
    save_plot(plt, "79_hiring_trend_distribution.png")
    
    # ── 10.80 ── Top & Bottom Companies by Hiring Trend ──
    hiring_ranked = company_growth.dropna(subset=['hiring_trend_6m']).sort_values('hiring_trend_6m')
    bottom_hiring = hiring_ranked.head(10)   # Most negative (declining hiring)
    top_hiring = hiring_ranked.tail(10)       # Most positive (increasing hiring)
    hiring_combined = pd.concat([bottom_hiring, top_hiring])
    
    fig, ax = plt.subplots(figsize=(12, 7))
    hiring_colors = ['#e74c3c' if x < 0 else '#2ecc71' for x in hiring_combined['hiring_trend_6m']]
    bars = ax.barh(hiring_combined['Company'], hiring_combined['hiring_trend_6m'],
                   color=hiring_colors, edgecolor='white')
    ax.axvline(0, color='black', linewidth=0.8)
    ax.set_xlabel('Hiring Trend 6M (%)', fontsize=12)
    ax.set_title('Hiring Momentum: Top 10 Increasing vs Bottom 10 Declining\n(% change in new hires rate, last month vs 6 months ago)',
                 fontsize=14, pad=15)
    ax.grid(axis='x', linestyle='--', alpha=0.3)
    for bar, (_, row) in zip(bars, hiring_combined.iterrows()):
        direction = '▲' if row['hiring_trend_6m'] > 0 else '▼'
        ax.text(bar.get_width() + (1.5 if bar.get_width() >= 0 else -8),
                bar.get_y() + bar.get_height() / 2,
                f'{direction} {row["hiring_trend_6m"]:+.1f}%  *{row["avg_rating"]:.1f}',
                va='center', fontsize=9, fontweight='bold')
    save_plot(plt, "80_hiring_trend_top_bottom.png")
    
    # ── 10.81 ── Hiring Trend vs Employee Growth (Scatter) ──
    ht_growth_data = company_growth.dropna(subset=['hiring_trend_6m', 'growth_6m'])
    
    fig, ax = plt.subplots(figsize=(11, 7))
    scatter = ax.scatter(ht_growth_data['growth_6m'], ht_growth_data['hiring_trend_6m'],
                         s=ht_growth_data['total_reviews'] / 10 + 60,
                         c=ht_growth_data['avg_rating'], cmap='RdYlGn', alpha=0.8,
                         edgecolors='white', linewidth=1, vmin=2, vmax=5)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Average Rating', fontsize=11)
    ax.axhline(0, color='gray', linestyle='--', alpha=0.4, linewidth=1)
    ax.axvline(0, color='gray', linestyle='--', alpha=0.4, linewidth=1)
    ax.set_xlabel('Employee Count Growth 6M (%)', fontsize=12)
    ax.set_ylabel('Hiring Trend 6M (%)', fontsize=12)
    ax.set_title('Hiring Trend vs Employee Growth\n(size = reviews, color = rating)\n"Are companies that hire more also growing headcount?"',
                 fontsize=14, pad=15)
    ax.grid(True, linestyle='--', alpha=0.3)
    
    # Quadrant labels
    ax.text(0.98, 0.98, 'Growing HC\n↑ Hiring [HOT]', transform=ax.transAxes,
            fontsize=9, ha='right', va='top', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='#2ecc71', alpha=0.25))
    ax.text(0.02, 0.98, 'Shrinking HC\n↑ Hiring', transform=ax.transAxes,
            fontsize=9, ha='left', va='top',
            bbox=dict(boxstyle='round', facecolor='#f39c12', alpha=0.25))
    ax.text(0.98, 0.02, 'Growing HC\n↓ Hiring', transform=ax.transAxes,
            fontsize=9, ha='right', va='bottom',
            bbox=dict(boxstyle='round', facecolor='#3498db', alpha=0.25))
    ax.text(0.02, 0.02, 'Shrinking HC\n↓ Hiring [COLD]', transform=ax.transAxes,
            fontsize=9, ha='left', va='bottom',
            bbox=dict(boxstyle='round', facecolor='#e74c3c', alpha=0.25))
    
    for _, row in ht_growth_data.iterrows():
        ax.annotate(row['Company'], (row['growth_6m'], row['hiring_trend_6m']),
                    textcoords="offset points", xytext=(5, 5),
                    fontsize=7, ha='left')
    corr_val = ht_growth_data['growth_6m'].corr(ht_growth_data['hiring_trend_6m'])
    ax.text(0.5, 0.01, f'Correlation: r={corr_val:.2f}',
            transform=ax.transAxes, fontsize=10, ha='center', fontstyle='italic',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
    save_plot(plt, "81_hiring_trend_vs_growth.png")
    
    # ── 10.82 ── New Hires (6M): Distribution + Top Companies ──
    new_hires_clean = company_growth['new_hires_6m'].dropna()
    
    fig, axes = plt.subplots(1, 2, figsize=(17, 7))
    
    # Left: Distribution
    ax = axes[0]
    sns.histplot(new_hires_clean, bins=20, kde=True, color='#1abc9c',
                 edgecolor='#16a085', ax=ax)
    ax.axvline(new_hires_clean.median(), color='#e74c3c', linestyle='--', linewidth=2,
               label=f'Median: {new_hires_clean.median():.0f}')
    ax.axvline(new_hires_clean.mean(), color='#f39c12', linestyle='--', linewidth=2,
               label=f'Mean: {new_hires_clean.mean():.0f}')
    ax.set_title('Distribution of New Hires (Past 6 Months)', fontsize=13)
    ax.set_xlabel('Number of New Hires', fontsize=11)
    ax.set_ylabel('Number of Companies', fontsize=11)
    ax.legend(fontsize=9)
    
    # Right: Top 15 by New Hires
    ax = axes[1]
    top_hires = company_growth.dropna(subset=['new_hires_6m']).nlargest(15, 'new_hires_6m').sort_values('new_hires_6m')
    hire_colors = plt.cm.Blues(0.3 + 0.7 * np.linspace(0, 1, len(top_hires)))
    bars = ax.barh(top_hires['Company'], top_hires['new_hires_6m'],
                   color=hire_colors, edgecolor='white')
    ax.set_xlabel('New Hires in Past 6 Months', fontsize=11)
    ax.set_title('Top 15 Companies by New Hires (6M)', fontsize=13)
    ax.grid(axis='x', linestyle='--', alpha=0.3)
    for bar, (_, row) in zip(bars, top_hires.iterrows()):
        ax.text(bar.get_width() + bar.get_width() * 0.01,
                bar.get_y() + bar.get_height() / 2,
                f'{row["new_hires_6m"]:,.0f}  *{row["avg_rating"]:.1f}',
                va='center', fontsize=9, fontweight='bold')
    
    fig.suptitle('New Hires Analysis (Past 6 Months)', fontsize=15, y=1.02)
    plt.tight_layout()
    save_plot(plt, "82_new_hires_distribution_and_top.png")
    
    # ── 10.83 ── New Hires vs Global Employee Count (Scatter) ──
    nh_emp_data = company_growth.dropna(subset=['new_hires_6m', 'global_emp'])
    
    fig, ax = plt.subplots(figsize=(11, 7))
    scatter = ax.scatter(nh_emp_data['global_emp'], nh_emp_data['new_hires_6m'],
                         s=nh_emp_data['avg_rating'] * 50 + 30,
                         c=nh_emp_data['company_age'].fillna(20), cmap='plasma',
                         alpha=0.8, edgecolors='white', linewidth=1)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Company Age (years)', fontsize=11)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Global Employee Count (log scale)', fontsize=12)
    ax.set_ylabel('New Hires in Past 6 Months (log scale)', fontsize=12)
    ax.set_title('New Hires vs Company Size\n(size = rating, color = company age)\n"Hiring volume vs headcount base"',
                 fontsize=14, pad=15)
    ax.grid(True, linestyle='--', alpha=0.3)
    
    # Trend line
    mask = nh_emp_data['global_emp'].notna() & nh_emp_data['new_hires_6m'].notna()
    if mask.sum() > 2:
        z = np.polyfit(np.log10(nh_emp_data.loc[mask, 'global_emp']),
                       np.log10(nh_emp_data.loc[mask, 'new_hires_6m']), 1)
        p = np.poly1d(z)
        x_line = np.linspace(np.log10(nh_emp_data['global_emp'].min()),
                             np.log10(nh_emp_data['global_emp'].max()), 100)
        ax.plot(10 ** x_line, 10 ** p(x_line), 'r--', linewidth=1.5, alpha=0.7,
                label=f'Slope: {z[0]:.2f}')
    
    # Hiring-rate reference lines
    emp_range_line = np.logspace(np.log10(nh_emp_data['global_emp'].min()),
                                  np.log10(nh_emp_data['global_emp'].max()), 100)
    for rate_pct, label, ls, col in [
        (0.50, '50% hiring rate', ':', '#95a5a6'),
        (0.20, '20% hiring rate', '--', '#7f8c8d'),
        (0.05, '5% hiring rate', '-.', '#555'),
    ]:
        ax.plot(emp_range_line, rate_pct * emp_range_line, ls, color=col,
                alpha=0.4, linewidth=1, label=label)
    
    for _, row in nh_emp_data.iterrows():
        if row['new_hires_6m'] > 0:
            ax.annotate(row['Company'], (row['global_emp'], row['new_hires_6m']),
                        textcoords="offset points", xytext=(5, 5),
                        fontsize=6, ha='left')
    
    ax.legend(fontsize=8, title='Hiring Rate = New Hires / Total Emp', title_fontsize=9,
              loc='lower right')
    save_plot(plt, "83_new_hires_vs_company_size.png")
    
    # ── 10.84 ── Growth + Hiring Dashboard Heatmap (Top 20 by 2Y Growth) ──
    dashboard_cols = [
        'growth_6m', 'growth_1y', 'growth_2y',
        'hiring_trend_6m', 'new_hires_6m',
        'avg_rating', 'company_age', 'global_emp',
    ]
    dashboard_labels = [
        'Growth 6M%', 'Growth 1Y%', 'Growth 2Y%',
        'Hiring Trend%', 'New Hires',
        'Rating', 'Age (yrs)', 'Global Emp',
    ]
    
    top20_growth = company_growth.dropna(subset=['growth_2y']).nlargest(20, 'growth_2y').set_index('Company')
    dashboard_raw = top20_growth[dashboard_cols].copy()
    dashboard_raw.columns = dashboard_labels
    
    # Normalize columns to 0-1 for colormap
    dashboard_norm = (dashboard_raw - dashboard_raw.min()) / \
                     (dashboard_raw.max() - dashboard_raw.min() + 1e-10)
    
    fig, ax = plt.subplots(figsize=(16, 10))
    sns.heatmap(dashboard_norm, annot=dashboard_raw.round(1), fmt='.1f',
                cmap='RdYlGn', ax=ax, linewidths=1, linecolor='white',
                annot_kws={'fontsize': 8}, center=0.5,
                cbar_kws={'label': 'Normalized Score (0–1)'})
    ax.set_title('Growth & Hiring Dashboard: Top 20 Companies by 2-Year Employee Growth\n(Green = high/better, Red = low/worse for each metric)',
                 fontsize=14, pad=18)
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.tick_params(axis='both', labelsize=9)
    save_plot(plt, "84_growth_hiring_dashboard_heatmap.png")
    
    # ── 10.85 ── Employee Growth vs Company Age (Small Multiples) ──
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    growth_age_map = [
        ('growth_6m', '6-Month Growth %', axes[0]),
        ('growth_1y', '1-Year Growth %', axes[1]),
        ('growth_2y', '2-Year Growth %', axes[2]),
    ]
    
    for col, label, ax in growth_age_map:
        plot_data = company_growth.dropna(subset=[col, 'company_age'])
        scatter = ax.scatter(plot_data['company_age'], plot_data[col],
                             s=plot_data['global_emp'].fillna(1000) / 30 + 50,
                             c=plot_data['avg_rating'], cmap='RdYlGn', alpha=0.8,
                             edgecolors='#2c3e50', linewidth=0.8, vmin=2, vmax=5)
        ax.axhline(0, color='gray', linestyle='--', alpha=0.4, linewidth=1)
        ax.set_xlabel('Company Age (years)', fontsize=11)
        ax.set_ylabel(label, fontsize=11)
        ax.set_title(label, fontsize=13, fontweight='bold')
        ax.grid(True, linestyle='--', alpha=0.3)
    
        # Trend line
        mask = plot_data['company_age'].notna() & plot_data[col].notna()
        if mask.sum() > 2:
            z = np.polyfit(plot_data.loc[mask, 'company_age'], plot_data.loc[mask, col], 1)
            p = np.poly1d(z)
            x_line = np.linspace(plot_data['company_age'].min(), plot_data['company_age'].max(), 100)
            ax.plot(x_line, p(x_line), 'r--', linewidth=1.5, alpha=0.7)
        corr_val = plot_data['company_age'].corr(plot_data[col])
        ax.text(0.95, 0.05, f'r={corr_val:.2f}', transform=ax.transAxes,
                fontsize=10, ha='right', va='bottom',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.6))
    
        for _, row in plot_data.iterrows():
            if abs(row[col]) > plot_data[col].std() * 1.5:
                ax.annotate(row['Company'], (row['company_age'], row[col]),
                            textcoords="offset points", xytext=(5, 5),
                            fontsize=6, ha='left', alpha=0.85)
    
    cbar = fig.colorbar(scatter, ax=axes, orientation='vertical', fraction=0.02, pad=0.04)
    cbar.set_label('Average Rating', fontsize=11)
    
    fig.suptitle('Employee Growth vs Company Age\n(size = global employees, color = rating)\n"Are younger companies growing faster?"',
                 fontsize=16, y=1.03)
    plt.tight_layout()
    save_plot(plt, "85_growth_vs_company_age.png")
    
    # ── 10.86 ── Employee Growth vs Revenue (Scatter, 2Y Growth) ──
    growth_rev_data = company_growth.dropna(subset=['growth_2y', 'revenue_usd'])
    
    fig, ax = plt.subplots(figsize=(12, 7))
    scatter = ax.scatter(growth_rev_data['revenue_usd'], growth_rev_data['growth_2y'],
                         s=growth_rev_data['global_emp'].fillna(1000) / 30 + 80,
                         c=growth_rev_data['avg_rating'], cmap='RdYlGn', alpha=0.8,
                         edgecolors='#2c3e50', linewidth=1.2, vmin=2, vmax=5)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Average Rating', fontsize=11)
    ax.set_xscale('log')
    ax.axhline(0, color='gray', linestyle='--', alpha=0.4, linewidth=1)
    ax.set_xlabel('Annual Revenue (USD, log scale)', fontsize=12)
    ax.set_ylabel('2-Year Employee Growth (%)', fontsize=12)
    ax.set_title('Employee Growth vs Company Revenue\n(size = global employees, color = rating)\n"Big revenue = big growth, or the opposite?"',
                 fontsize=14, pad=15)
    ax.grid(True, linestyle='--', alpha=0.3)
    
    mask = growth_rev_data['revenue_usd'].notna() & growth_rev_data['growth_2y'].notna()
    if mask.sum() > 2:
        z = np.polyfit(np.log10(growth_rev_data.loc[mask, 'revenue_usd']),
                       growth_rev_data.loc[mask, 'growth_2y'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(np.log10(growth_rev_data['revenue_usd'].min()),
                             np.log10(growth_rev_data['revenue_usd'].max()), 100)
        ax.plot(10 ** x_line, p(x_line), 'r--', linewidth=1.5, alpha=0.7, label='Trend')
    
    for _, row in growth_rev_data.iterrows():
        ax.annotate(row['Company'], (row['revenue_usd'], row['growth_2y']),
                    textcoords="offset points", xytext=(5, 5),
                    fontsize=7, ha='left')
    ax.legend(fontsize=9)
    save_plot(plt, "86_growth_vs_revenue.png")
    
    # ── 10.87 ── Employee Growth vs Sub-Ratings (Small Multiples, 2Y Growth) ──
    growth_sub_map = {
        'avg_culture': 'Culture',
        'avg_salary_sub': 'Salary',
        'avg_wlb': 'Work-Life Balance',
        'avg_satisfaction': 'Work Satisfaction',
        'avg_skill': 'Skill Development',
        'avg_security': 'Job Security',
        'avg_promotions': 'Promotions',
    }
    
    fig, axes = plt.subplots(3, 3, figsize=(18, 16))
    axes = axes.flatten()
    
    for i, (col, label) in enumerate(growth_sub_map.items()):
        ax = axes[i]
        sub_clean = company_growth.dropna(subset=['growth_2y', col])
        scatter = ax.scatter(sub_clean[col], sub_clean['growth_2y'],
                             s=sub_clean['total_reviews'] / 15 + 50,
                             c=sub_clean['avg_rating'], cmap='RdYlGn', alpha=0.8,
                             edgecolors='#2c3e50', linewidth=0.8, vmin=2, vmax=5)
        ax.axhline(0, color='gray', linestyle='--', alpha=0.4, linewidth=1)
        ax.set_xlabel(f'{label} Rating', fontsize=10)
        ax.set_ylabel('2Y Growth %', fontsize=10)
        ax.set_title(f'{label}', fontsize=12, fontweight='bold')
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.set_xlim(sub_clean[col].min() - 0.3, sub_clean[col].max() + 0.4)
    
        # Regression
        mask = sub_clean[col].notna() & sub_clean['growth_2y'].notna()
        if mask.sum() > 2:
            z = np.polyfit(sub_clean.loc[mask, col], sub_clean.loc[mask, 'growth_2y'], 1)
            p = np.poly1d(z)
            x_line = np.linspace(sub_clean[col].min(), sub_clean[col].max(), 100)
            ax.plot(x_line, p(x_line), 'r--', linewidth=1.2, alpha=0.6)
        corr_val = sub_clean[col].corr(sub_clean['growth_2y'])
        ax.text(0.95, 0.05, f'r={corr_val:.2f}', transform=ax.transAxes,
                fontsize=9, ha='right', va='bottom',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.6))
    
        for _, row in sub_clean.iterrows():
            ax.annotate(row['Company'], (row[col], row['growth_2y']),
                        textcoords="offset points", xytext=(4, 3),
                        fontsize=6, ha='left', alpha=0.85)
    
    for j in range(len(growth_sub_map), len(axes)):
        axes[j].set_visible(False)
    
    fig.suptitle('2-Year Employee Growth vs Sub-Ratings\n(color = overall rating, size = total reviews)',
                 fontsize=16, y=1.01)
    plt.tight_layout()
    save_plot(plt, "87_growth_vs_sub_ratings.png")
    
    # ── 10.88 ── New Hires per Employee (Hiring Intensity) vs Rating ──
    company_growth['hires_per_emp'] = (
        company_growth['new_hires_6m'] / company_growth['global_emp']
    )
    # Filter out extremes
    hires_intensity = company_growth.dropna(subset=['hires_per_emp', 'avg_rating'])
    hires_intensity = hires_intensity[hires_intensity['hires_per_emp'] < 5]  # Cap unrealistic ratios
    
    hires_intensity['hires_rate_pct'] = hires_intensity['hires_per_emp'] * 100
    
    fig, ax = plt.subplots(figsize=(11, 7))
    scatter = ax.scatter(hires_intensity['avg_rating'], hires_intensity['hires_rate_pct'],
                         s=hires_intensity['global_emp'].fillna(1000) / 30 + 60,
                         c=hires_intensity['growth_2y'], cmap='coolwarm', alpha=0.8,
                         edgecolors='#2c3e50', linewidth=1, vmin=-50, vmax=200)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('2-Year Growth %', fontsize=11)
    ax.set_xlabel('Average Overall Rating', fontsize=12)
    ax.set_ylabel('Hiring Rate: New Hires / Total Employees (%)', fontsize=12)
    ax.set_title('Hiring Intensity vs Rating\n(size = global employees, color = 2Y growth)\n"Are high-growth companies hiring more aggressively?"',
                 fontsize=14, pad=15)
    ax.grid(True, linestyle='--', alpha=0.3)
    
    for _, row in hires_intensity.iterrows():
        ax.annotate(row['Company'], (row['avg_rating'], row['hires_rate_pct']),
                    textcoords="offset points", xytext=(5, 5),
                    fontsize=7, ha='left')
    
    corr_val = hires_intensity['avg_rating'].corr(hires_intensity['hires_rate_pct'])
    ax.text(0.95, 0.05, f'r={corr_val:.2f}', transform=ax.transAxes,
            fontsize=10, ha='right', va='bottom',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.6))
    save_plot(plt, "88_hiring_intensity_vs_rating.png")
    
    # ── 10.89 ── Growth Metrics Correlation Heatmap ──
    growth_corr_cols = [
        'growth_6m', 'growth_1y', 'growth_2y',
        'hiring_trend_6m', 'new_hires_6m',
        'avg_rating', 'total_reviews', 'company_age',
        'global_emp', 'india_emp',
        'avg_culture', 'avg_salary_sub', 'avg_wlb',
        'avg_satisfaction', 'avg_skill', 'avg_security', 'avg_promotions',
        'median_tenure', 'avg_salary_lyr',
    ]
    growth_corr_labels = [
        'Growth 6M%', 'Growth 1Y%', 'Growth 2Y%',
        'Hiring Trend%', 'New Hires',
        'Rating', 'Reviews', 'Age (yrs)',
        'Global Emp', 'India Emp',
        'Culture', 'Salary*', 'WLB',
        'Satisfaction', 'Skill', 'Security', 'Promotions',
        'Tenure (yrs)', 'Salary (L/Yr)',
    ]
    
    growth_corr_df = company_growth[growth_corr_cols].copy()
    # Log-transform scale variables
    for col in ['global_emp', 'india_emp', 'total_reviews', 'new_hires_6m']:
        growth_corr_df[col] = np.log10(growth_corr_df[col].replace(0, np.nan))
    growth_corr_df.columns = growth_corr_labels
    growth_corr = growth_corr_df.corr()
    
    fig, ax = plt.subplots(figsize=(18, 15))
    mask = np.triu(np.ones_like(growth_corr, dtype=bool), k=1)
    sns.heatmap(growth_corr, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
                square=True, ax=ax, mask=mask, vmin=-1, vmax=1,
                annot_kws={'fontsize': 7}, linewidths=0.5,
                cbar_kws={'label': 'Pearson r (log₁₀ for scale vars)'})
    ax.set_title('Growth & Hiring: Comprehensive Correlation Matrix\n(First 5 rows/cols = growth metrics; log₁₀ for scale variables)',
                 fontsize=15, pad=20)
    ax.tick_params(axis='both', labelsize=9)
    save_plot(plt, "89_growth_correlation_heatmap.png")
    
    # ── 10.90 ── Growth by Revenue Tier (Box Plot, 2Y Growth) ──
    growth_rev_tier = company_growth.dropna(subset=['growth_2y', 'revenue_usd']).copy()
    growth_rev_tier['revenue_tier'] = pd.cut(
        growth_rev_tier['revenue_usd'],
        bins=[0, 1e9, 10e9, 50e9, 200e9, np.inf],
        labels=['<$1B', '$1B–$10B', '$10B–$50B', '$50B–$200B', '>$200B'],
        right=False,
    )
    
    fig, ax = plt.subplots(figsize=(12, 7))
    tier_order = ['<$1B', '$1B–$10B', '$10B–$50B', '$50B–$200B', '>$200B']
    tier_palette_growth = sns.color_palette("RdYlGn", len(tier_order))
    sns.boxplot(data=growth_rev_tier, x='revenue_tier', y='growth_2y',
                hue='revenue_tier', palette=tier_palette_growth, legend=False,
                order=tier_order, ax=ax)
    sns.stripplot(data=growth_rev_tier, x='revenue_tier', y='growth_2y',
                  color='black', alpha=0.3, size=5, jitter=True, ax=ax)
    # Annotate company names
    for _, row in growth_rev_tier.iterrows():
        tier_idx = tier_order.index(row['revenue_tier']) if row['revenue_tier'] in tier_order else -1
        if tier_idx >= 0:
            ax.annotate(row['Company'], (tier_idx, row['growth_2y']),
                        textcoords="offset points", xytext=(0, 8),
                        fontsize=6, ha='center', alpha=0.7)
    
    ax.axhline(0, color='gray', linestyle='--', alpha=0.4, linewidth=1)
    ax.set_title('2-Year Employee Growth by Revenue Tier\n"Which tier is expanding fastest?"', fontsize=14, pad=15)
    ax.set_xlabel('Revenue Tier', fontsize=12)
    ax.set_ylabel('2-Year Employee Growth (%)', fontsize=12)
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    save_plot(plt, "90_growth_by_revenue_tier.png")
    
    # ── 10.91 ── Growth vs India Workforce % ──
    growth_india_data = company_growth.dropna(subset=['growth_2y'])
    growth_india_data['india_pct'] = growth_india_data['india_emp'] / growth_india_data['global_emp'] * 100
    growth_india_data = growth_india_data.dropna(subset=['india_pct'])
    
    fig, ax = plt.subplots(figsize=(11, 7))
    scatter = ax.scatter(growth_india_data['india_pct'], growth_india_data['growth_2y'],
                         s=growth_india_data['total_reviews'] / 10 + 60,
                         c=growth_india_data['avg_rating'], cmap='RdYlGn', alpha=0.8,
                         edgecolors='white', linewidth=1, vmin=2, vmax=5)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Average Rating', fontsize=11)
    ax.axhline(0, color='gray', linestyle='--', alpha=0.4, linewidth=1)
    ax.axvline(50, color='#7f8c8d', linestyle='--', alpha=0.5, label='50% India workforce')
    ax.set_xlabel('India Workforce as % of Global', fontsize=12)
    ax.set_ylabel('2-Year Employee Growth (%)', fontsize=12)
    ax.set_title('Employee Growth vs India Workforce Concentration\n(size = reviews, color = rating)', fontsize=14, pad=15)
    ax.grid(True, linestyle='--', alpha=0.3)
    
    mask = growth_india_data['india_pct'].notna() & growth_india_data['growth_2y'].notna()
    if mask.sum() > 2:
        z = np.polyfit(growth_india_data.loc[mask, 'india_pct'],
                       growth_india_data.loc[mask, 'growth_2y'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(growth_india_data['india_pct'].min(),
                             growth_india_data['india_pct'].max(), 100)
        ax.plot(x_line, p(x_line), 'r--', linewidth=1.5, alpha=0.7, label='Trend')
    
    for _, row in growth_india_data.iterrows():
        ax.annotate(row['Company'], (row['india_pct'], row['growth_2y']),
                    textcoords="offset points", xytext=(5, 5),
                    fontsize=7, ha='left')
    ax.legend(fontsize=9)
    save_plot(plt, "91_growth_vs_india_pct.png")
    
    print(f"\nEmployee Growth & Hiring Trends section plots saved (75–91).")
    print(f"  ✓ Section 10 complete — 17 plots saved.")

if __name__ == "__main__":
    run()
