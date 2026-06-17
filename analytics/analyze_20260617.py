import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
EXCEL_PATH = "/home/jain/Desktop/ws/public/company_and_job_market_research/ratings_and_reviews_at_ambitionbox.xlsx"
SAVE_DIR_BASE = "/home/jain/Desktop/ws/public/company_and_job_market_research/analytics/imgs"

# Create a timestamped output folder
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_DIR = os.path.join(SAVE_DIR_BASE, f"img_{timestamp}")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------------------------------------------------
# 1. Data Loading & Preprocessing
# -------------------------------------------------------------------
df = pd.read_excel(EXCEL_PATH)

# Parse dates (format: "Jan / 16 / 2026")
df['Date'] = pd.to_datetime(df['Date'], format='%b / %d / %Y')

# Extract month/year for later trends
df['YearMonth'] = df['Date'].dt.to_period('M')

# Summary statistics
print("Data loaded successfully. Shape:", df.shape)
print(df.head())

# -------------------------------------------------------------------
# 2. Visualization Settings
# -------------------------------------------------------------------
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("Set2")
COLORS = sns.color_palette("husl", 10)

# Helper to save plots
def save_plot(plt, filename):
    path = os.path.join(OUTPUT_DIR, filename)
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")

# -------------------------------------------------------------------
# 3. Mandatory Plots (with enhancements)
# -------------------------------------------------------------------

# --- 3.1 Bar Chart: Company Ratings (Top 20 by rating) ---
top_rated = df.groupby('Company')['Rating'].mean().sort_values(ascending=False).head(20)
fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(top_rated.index, top_rated.values, color=COLORS[0])
ax.set_title('Top 20 Companies by Average Rating', fontsize=14, pad=15)
ax.set_xlabel('Company', fontsize=12)
ax.set_ylabel('Rating (out of 5)', fontsize=12)
ax.set_ylim(0, 5.5)
ax.tick_params(axis='x', rotation=45, labelsize=9)
for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, yval + 0.05, round(yval, 2), ha='center', va='bottom', fontsize=8)
save_plot(plt, "01_company_ratings_bar.png")

# --- 3.2 Bar Chart: Industry Level Insights (Top/Bottom 10 deviation) ---
# Aggregate mean deviation per company
deviation = df.groupby('Company')['Industry level insights (%: -100 (below industry\'s average) to 100)'].mean().sort_values()
worst10 = deviation.head(10)
best10 = deviation.tail(10)
combined = pd.concat([worst10, best10])

fig, ax = plt.subplots(figsize=(12, 6))
colors = ['#d9534f' if x < 0 else '#5cb85c' for x in combined.values]
bars = ax.barh(combined.index, combined.values, color=colors)
ax.axvline(0, color='black', linewidth=0.8)
ax.set_title('Companies with Most Extreme Industry Deviation (%)', fontsize=14)
ax.set_xlabel('Deviation from Industry Average (%)', fontsize=12)
for i, (bar, val) in enumerate(zip(bars, combined.values)):
    ax.text(val + (2 if val >=0 else -5), bar.get_y() + bar.get_height()/2,
            f'{val:.1f}%', va='center', fontsize=9)
save_plot(plt, "02_industry_insights_bar.png")

# --- 3.3 Distribution Plot: Rating Distribution ---
fig, ax = plt.subplots(figsize=(10, 5))
sns.histplot(df['Rating'], bins=20, kde=True, color='#3498db', ax=ax)
ax.set_title('Distribution of Company Ratings', fontsize=14)
ax.set_xlabel('Rating (0-5)', fontsize=12)
ax.set_ylabel('Frequency', fontsize=12)
ax.axvline(df['Rating'].mean(), color='red', linestyle='dashed', linewidth=2, label=f'Mean: {df["Rating"].mean():.2f}')
ax.legend()
save_plot(plt, "03_rating_distribution.png")

# --- 3.4 Scatter Plot: Rating vs Number of Reviews (log scale) ---
fig, ax = plt.subplots(figsize=(10, 6))
# Slight jitter to avoid overlapping points (optional)
scatter = ax.scatter(df['Rating'], df['#Reviews'], alpha=0.6, c='#e67e22', edgecolors='w', s=30)
ax.set_yscale('log')
ax.set_title('Rating vs Number of Reviews (Log Scale)', fontsize=14)
ax.set_xlabel('Rating', fontsize=12)
ax.set_ylabel('Number of Reviews (log scale)', fontsize=12)
ax.grid(True, linestyle='--', alpha=0.5)
# Add a trend line (optional)
z = np.polyfit(df['Rating'], np.log10(df['#Reviews']+1), 1)
p = np.poly1d(z)
ax.plot(df['Rating'].sort_values(), 10**p(df['Rating'].sort_values()), "r--", alpha=0.7)
save_plot(plt, "04_rating_vs_reviews_scatter.png")

# -------------------------------------------------------------------
# 4. Additional Insightful Plots
# -------------------------------------------------------------------

# --- 4.5 Box Plot: Rating spread per company (Top 15 by review count) ---
top_companies = df.groupby('Company')['#Reviews'].sum().nlargest(15).index
df_top = df[df['Company'].isin(top_companies)]

fig, ax = plt.subplots(figsize=(14, 6))
sns.boxplot(data=df_top, x='Company', y='Rating', hue='Company',
            palette='viridis', legend=False, ax=ax)
ax.set_title('Rating Distribution per Company (Top 15 by Total Reviews)', fontsize=14)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=9)
ax.set_ylabel('Rating', fontsize=12)
save_plot(plt, "05_rating_boxplot_per_company.png")

# --- 4.6 Bar Chart: Total Number of Reviews per Company (Top 15) ---
review_counts = df.groupby('Company')['#Reviews'].sum().nlargest(15)
fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(review_counts.index, review_counts.values, color=COLORS[2])
ax.set_title('Total Number of Reviews per Company (Top 15)', fontsize=14)
ax.set_ylabel('Total Reviews', fontsize=12)
ax.tick_params(axis='x', rotation=45, labelsize=9)
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, height + 50, str(height), ha='center', va='bottom', fontsize=9)
save_plot(plt, "06_review_count_per_company.png")

# --- 4.7 Scatter: Average Rating vs Industry Deviation ---
avg_stats = df.groupby('Company').agg(
    avg_rating=('Rating', 'mean'),
    avg_deviation=('Industry level insights (%: -100 (below industry\'s average) to 100)', 'mean'),
    total_reviews=('#Reviews', 'sum')
).reset_index()

fig, ax = plt.subplots(figsize=(10, 6))
scatter = ax.scatter(avg_stats['avg_rating'], avg_stats['avg_deviation'],
                     s=avg_stats['total_reviews']/10, alpha=0.6, c='#8e44ad', edgecolors='w')
ax.axhline(0, color='gray', linestyle='--', alpha=0.5)
ax.axvline(avg_stats['avg_rating'].mean(), color='red', linestyle='--', alpha=0.5)
ax.set_title('Average Rating vs Industry Deviation (bubble size = total reviews)', fontsize=14)
ax.set_xlabel('Average Rating', fontsize=12)
ax.set_ylabel('Average Industry Deviation (%)', fontsize=12)
ax.grid(True)
# Annotate a few outliers
for i, row in avg_stats.iterrows():
    if abs(row['avg_deviation']) > 15 or row['avg_rating'] < 2.5 or row['avg_rating'] > 4.5:
        ax.annotate(row['Company'], (row['avg_rating'], row['avg_deviation']),
                    textcoords="offset points", xytext=(5,5), ha='left', fontsize=8)
save_plot(plt, "07_rating_vs_deviation_scatter.png")

# --- 4.8 Pie Chart: Review Distribution among Top 8 Companies ---
top8_reviews = review_counts.nlargest(8)
others = review_counts.sum() - top8_reviews.sum()
pie_data = top8_reviews.copy()
pie_data['Others'] = others

fig, ax = plt.subplots(figsize=(8, 8))
wedges, texts, autotexts = ax.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%',
                                  startangle=90, colors=sns.color_palette('Set3', len(pie_data)))
ax.set_title('Review Distribution Among Top Companies', fontsize=14)
save_plot(plt, "08_review_distribution_pie.png")

# --- 4.9 Time Series: Monthly Average Rating ---
monthly_avg = df.groupby('YearMonth')['Rating'].mean().reset_index()
monthly_avg['YearMonth'] = monthly_avg['YearMonth'].astype(str)

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(monthly_avg['YearMonth'], monthly_avg['Rating'], marker='o', color='#2c3e50', linewidth=2)
ax.set_title('Monthly Average Rating Over Time', fontsize=14)
ax.set_xlabel('Month', fontsize=12)
ax.set_ylabel('Average Rating', fontsize=12)
ax.tick_params(axis='x', rotation=45)
ax.grid(True, linestyle='--', alpha=0.7)
# Add trend line
x = range(len(monthly_avg))
z = np.polyfit(x, monthly_avg['Rating'], 1)
p = np.poly1d(z)
ax.plot(monthly_avg['YearMonth'], p(x), "r--", label='Trend')
ax.legend()
save_plot(plt, "09_monthly_avg_rating_line.png")

# --- 4.10 Correlation Heatmap ---
corr_df = df[['Rating', '#Reviews', 'Industry level insights (%: -100 (below industry\'s average) to 100)']].corr()
fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(corr_df, annot=True, cmap='coolwarm', center=0, square=True, ax=ax)
ax.set_title('Correlation Matrix of Numeric Features', fontsize=14)
save_plot(plt, "10_correlation_heatmap.png")

# --- 4.11 Violin Plot: Rating distribution by Review Count Bracket ---
# Categorize number of reviews into brackets
bins = [0, 10, 50, 200, 1000, np.inf]
labels = ['0-10', '11-50', '51-200', '201-1000', '1000+']
df['Review_bracket'] = pd.cut(df['#Reviews'], bins=bins, labels=labels, right=False)

fig, ax = plt.subplots(figsize=(10, 6))
sns.violinplot(data=df, x='Review_bracket', y='Rating', hue='Review_bracket',
               palette='muted', legend=False, ax=ax)
ax.set_title('Rating Distribution by Number of Reviews', fontsize=14)
ax.set_xlabel('Review Count Bracket', fontsize=12)
ax.set_ylabel('Rating', fontsize=12)
save_plot(plt, "11_rating_violin_by_review_bracket.png")

# --- 4.12 Stacked Bar: Companies Above/Below Industry Average ---
df['above_industry'] = df['Industry level insights (%: -100 (below industry\'s average) to 100)'] >= 0
counts = df.groupby(['Company', 'above_industry']).size().unstack(fill_value=0)
counts.columns = ['Below Industry Avg', 'Above Industry Avg']
# Sort by total count of above, take top 15
counts['Total'] = counts.sum(axis=1)
counts = counts.sort_values('Total', ascending=False).head(15).drop('Total', axis=1)

fig, ax = plt.subplots(figsize=(12, 6))
counts.plot(kind='bar', stacked=True, ax=ax, color=['#e74c3c', '#2ecc71'])
ax.set_title('Companies: Above/Below Industry Average (Top 15 by Total Reviews)', fontsize=14)
ax.set_ylabel('Number of Data Points', fontsize=12)
ax.set_xlabel('Company', fontsize=12)
ax.tick_params(axis='x', rotation=45)
ax.legend(title='')
save_plot(plt, "12_above_below_industry_stacked_bar.png")

# -------------------------------------------------------------------
# 5. Sub-Rating Analysis Plots
#    Columns: Company Culture, Salary, Work-Life Balance,
#             Work Satisfaction, Skill Development, Job Security, Promotions
# -------------------------------------------------------------------

SUB_RATINGS = [
    'Company Culture', 'Salary', 'Work-Life Balance',
    'Work Satisfaction', 'Skill Development', 'Job Security', 'Promotions'
]

# --- 5.13 Radar Chart: Sub-Rating Profiles of Top 6 Companies ---
from math import pi

top6_companies = df.groupby('Company')['Rating'].mean().nlargest(6).index
radar_data = df[df['Company'].isin(top6_companies)].groupby('Company')[SUB_RATINGS].mean()

# Normalize to 0-1 for better visual spread (optional, but ratings are already 0-5)
N = len(SUB_RATINGS)
angles = [n / float(N) * 2 * pi for n in range(N)]
angles += angles[:1]  # close the circle

fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
palette = sns.color_palette("husl", len(radar_data))
for idx, (company, row) in enumerate(radar_data.iterrows()):
    values = row.values.flatten().tolist()
    values += values[:1]
    ax.plot(angles, values, 'o-', linewidth=2, label=company, color=palette[idx])
    ax.fill(angles, values, alpha=0.1, color=palette[idx])

ax.set_xticks(angles[:-1])
ax.set_xticklabels(SUB_RATINGS, fontsize=10)
ax.set_ylim(0, 5.5)
ax.set_yticks([1, 2, 3, 4, 5])
ax.set_yticklabels(['1', '2', '3', '4', '5'], fontsize=8)
ax.set_title('Sub-Rating Profiles: Top 6 Companies by Overall Rating', fontsize=15, pad=30)
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=9)
save_plot(plt, "13_radar_top6_companies.png")

# --- 5.14 Average Sub-Ratings Across All Companies (Grouped Bar) ---
avg_sub = df[SUB_RATINGS].mean().sort_values()

fig, ax = plt.subplots(figsize=(10, 6))
bar_colors = sns.color_palette("RdYlGn", len(SUB_RATINGS))
bars = ax.barh(range(len(avg_sub)), avg_sub.values, color=bar_colors)
ax.set_yticks(range(len(avg_sub)))
ax.set_yticklabels(avg_sub.index, fontsize=11)
ax.set_xlim(0, 5.5)
ax.set_title('Average Sub-Rating Across All Companies', fontsize=14)
ax.set_xlabel('Average Rating (out of 5)', fontsize=12)
for i, (bar, val) in enumerate(zip(bars, avg_sub.values)):
    ax.text(val + 0.05, bar.get_y() + bar.get_height()/2, f'{val:.2f}',
            va='center', fontsize=10, fontweight='bold')
save_plot(plt, "14_avg_sub_ratings_bar.png")

# --- 5.15 Full Correlation Heatmap (Overall Rating + Sub-Ratings + Reviews) ---
corr_cols = ['Rating', '#Reviews'] + SUB_RATINGS
full_corr = df[corr_cols].corr()

fig, ax = plt.subplots(figsize=(12, 10))
mask = np.triu(np.ones_like(full_corr, dtype=bool), k=1)
sns.heatmap(full_corr, annot=True, fmt='.2f', cmap='coolwarm', center=0,
            square=True, ax=ax, mask=mask, vmin=-1, vmax=1,
            annot_kws={'fontsize': 9})
ax.set_title('Correlation Matrix: Overall Rating, Reviews & Sub-Ratings', fontsize=14, pad=15)
save_plot(plt, "15_full_correlation_heatmap.png")

# --- 5.16 Box Plots: Distribution of Each Sub-Rating ---
df_melted_sub = df[SUB_RATINGS].melt(var_name='Sub-Rating', value_name='Score')

fig, ax = plt.subplots(figsize=(14, 7))
sns.boxplot(data=df_melted_sub, x='Sub-Rating', y='Score', hue='Sub-Rating',
            palette='Set3', legend=False, ax=ax)
sns.stripplot(data=df_melted_sub, x='Sub-Rating', y='Score', color='black',
              alpha=0.15, size=2, ax=ax, jitter=True)
ax.set_title('Distribution of Sub-Rating Scores', fontsize=14)
ax.set_ylabel('Score (out of 5)', fontsize=12)
ax.set_xlabel('')
ax.tick_params(axis='x', rotation=30, labelsize=10)
# Add mean markers
means = df[SUB_RATINGS].mean()
for i, (col, mean_val) in enumerate(means.items()):
    ax.plot(i, mean_val, 'D', color='red', markersize=8, zorder=5)
ax.axhline(y=df[SUB_RATINGS].mean().mean(), color='gray', linestyle='--',
           alpha=0.5, label='Grand Mean')
ax.legend(['Grand Mean'], fontsize=9)
save_plot(plt, "16_sub_ratings_boxplot.png")

# --- 5.17 Scatter Facets: Overall Rating vs Each Sub-Rating ---
fig, axes = plt.subplots(3, 3, figsize=(16, 14))
axes = axes.flatten()

for i, sub in enumerate(SUB_RATINGS):
    ax = axes[i]
    ax.scatter(df[sub], df['Rating'], alpha=0.2, c='#3498db', edgecolors='none', s=20)
    # Regression line
    mask = df[sub].notna() & df['Rating'].notna()
    if mask.sum() > 2:
        z = np.polyfit(df.loc[mask, sub], df.loc[mask, 'Rating'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(df[sub].min(), df[sub].max(), 100)
        ax.plot(x_line, p(x_line), 'r-', linewidth=1.5, alpha=0.8)
    ax.set_title(f'{sub}', fontsize=11)
    ax.set_xlabel('Score', fontsize=9)
    ax.set_ylabel('Overall Rating', fontsize=9)
    ax.set_xlim(-0.2, 5.2)
    ax.set_ylim(-0.2, 5.2)
    ax.grid(True, linestyle='--', alpha=0.4)
    # Annotate correlation
    corr_val = df[sub].corr(df['Rating'])
    ax.text(0.95, 0.05, f'r={corr_val:.2f}', transform=ax.transAxes,
            fontsize=10, ha='right', va='bottom',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# Hide extra subplots if any
for j in range(len(SUB_RATINGS), len(axes)):
    axes[j].set_visible(False)

fig.suptitle('Overall Rating vs Each Sub-Rating (with Regression Line)', fontsize=16, y=1.01)
plt.tight_layout()
save_plot(plt, "17_rating_vs_sub_ratings_facets.png")

# --- 5.18 Monthly Trend of Sub-Ratings ---
monthly_sub = df.groupby('YearMonth')[SUB_RATINGS].mean()
monthly_sub.index = monthly_sub.index.astype(str)

fig, ax = plt.subplots(figsize=(14, 7))
palette = sns.color_palette("tab10", len(SUB_RATINGS))
for i, sub in enumerate(SUB_RATINGS):
    ax.plot(monthly_sub.index, monthly_sub[sub], marker='o', linewidth=2,
            label=sub, color=palette[i], markersize=5)

ax.set_title('Monthly Average Sub-Ratings Over Time', fontsize=14)
ax.set_xlabel('Month', fontsize=12)
ax.set_ylabel('Average Score', fontsize=12)
ax.tick_params(axis='x', rotation=45)
ax.legend(loc='upper left', bbox_to_anchor=(1.01, 1), fontsize=9)
ax.grid(True, linestyle='--', alpha=0.5)
ax.set_ylim(0, 5.5)
save_plot(plt, "18_monthly_sub_ratings_line.png")

# --- 5.19 Heatmap: Companies × Sub-Ratings (Top 20 by total reviews) ---
top20_by_reviews = df.groupby('Company')['#Reviews'].sum().nlargest(20).index
heatmap_data = df[df['Company'].isin(top20_by_reviews)].groupby('Company')[SUB_RATINGS].mean()

fig, ax = plt.subplots(figsize=(14, 10))
sns.heatmap(heatmap_data, annot=True, fmt='.1f', cmap='YlOrRd', ax=ax,
            linewidths=0.5, vmin=0, vmax=5, annot_kws={'fontsize': 8})
ax.set_title('Sub-Rating Heatmap: Top 20 Companies by Total Reviews', fontsize=14, pad=12)
ax.set_xlabel('Sub-Rating Category', fontsize=12)
ax.set_ylabel('Company', fontsize=12)
ax.tick_params(axis='y', labelsize=9)
save_plot(plt, "19_companies_sub_ratings_heatmap.png")

# --- 5.20 Grouped Bar: Sub-Ratings of Top 10 Companies ---
top10_overall = df.groupby('Company')['Rating'].mean().nlargest(10).index
grouped_bar_data = df[df['Company'].isin(top10_overall)].groupby('Company')[SUB_RATINGS].mean()

x = np.arange(len(SUB_RATINGS))
width = 0.08
n_companies = len(grouped_bar_data)

fig, ax = plt.subplots(figsize=(18, 8))
palette = sns.color_palette("tab10", n_companies)
for i, (company, row) in enumerate(grouped_bar_data.iterrows()):
    offset = (i - n_companies/2 + 0.5) * width
    ax.bar(x + offset, row.values, width, label=company, color=palette[i])

ax.set_xticks(x)
ax.set_xticklabels(SUB_RATINGS, fontsize=10)
ax.set_ylabel('Average Score (out of 5)', fontsize=12)
ax.set_title('Sub-Rating Comparison: Top 10 Companies by Overall Rating', fontsize=14)
ax.set_ylim(0, 5.5)
ax.legend(loc='upper left', bbox_to_anchor=(1.01, 1), fontsize=9, title='Company')
ax.grid(axis='y', linestyle='--', alpha=0.4)
save_plot(plt, "20_top10_sub_ratings_grouped_bar.png")

# --- 5.21 Scatter: Salary vs Work-Life Balance (colored by Overall Rating) ---
fig, ax = plt.subplots(figsize=(10, 7))
scatter = ax.scatter(df['Salary'], df['Work-Life Balance'],
                     c=df['Rating'], cmap='RdYlGn', alpha=0.5,
                     s=df['#Reviews']/20 + 5, edgecolors='w', linewidth=0.3)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Overall Rating', fontsize=11)
ax.set_xlabel('Salary Rating', fontsize=12)
ax.set_ylabel('Work-Life Balance Rating', fontsize=12)
ax.set_title('Salary vs Work-Life Balance\n(color = overall rating, size = #reviews)', fontsize=14)
ax.set_xlim(-0.2, 5.2)
ax.set_ylim(-0.2, 5.2)
ax.grid(True, linestyle='--', alpha=0.4)

# Annotate companies with extreme trade-offs
company_agg = df.groupby('Company').agg(
    avg_salary=('Salary', 'mean'),
    avg_wlb=('Work-Life Balance', 'mean'),
    avg_rating=('Rating', 'mean')
).reset_index()

# Highlight: companies where salary >> WLB or WLB >> salary
company_agg['diff'] = abs(company_agg['avg_salary'] - company_agg['avg_wlb'])
extreme = company_agg.nlargest(8, 'diff')
for _, row in extreme.iterrows():
    ax.annotate(row['Company'], (row['avg_salary'], row['avg_wlb']),
                textcoords="offset points", xytext=(6, 6),
                fontsize=8, ha='left',
                arrowprops=dict(arrowstyle='->', color='gray', alpha=0.6))
save_plot(plt, "21_salary_vs_wlb_scatter.png")

# --- 5.22 Stacked Area: Sub-Rating Composition Over Time ---
fig, ax = plt.subplots(figsize=(14, 7))
ax.stackplot(monthly_sub.index, *[monthly_sub[c] for c in SUB_RATINGS],
             labels=SUB_RATINGS, colors=sns.color_palette("Set3", len(SUB_RATINGS)), alpha=0.85)
ax.set_title('Sub-Rating Composition Over Time (Stacked Area)', fontsize=14)
ax.set_xlabel('Month', fontsize=12)
ax.set_ylabel('Cumulative Average Score', fontsize=12)
ax.tick_params(axis='x', rotation=45)
ax.legend(loc='upper left', bbox_to_anchor=(1.01, 1), fontsize=9)
ax.set_ylim(0, 35)
save_plot(plt, "22_sub_ratings_stacked_area.png")

print(f"\nAll plots saved in: {OUTPUT_DIR}")
print("Done.")