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
sns.boxplot(data=df_top, x='Company', y='Rating', palette='viridis', ax=ax)
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
sns.violinplot(data=df, x='Review_bracket', y='Rating', palette='muted', ax=ax)
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

print(f"\nAll plots saved in: {OUTPUT_DIR}")
print("Done.")