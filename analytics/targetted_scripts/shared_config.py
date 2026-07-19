"""
shared_config.py — Core shared module for all analytics scripts.

Loads data once; builds company_demo aggregation; provides
plotting helpers and constants consumed by every section script.

Usage in section scripts:
    from shared_config import (df, company_demo, save_plot, _section,
                                OUTPUT_DIR, COLORS, SUB_RATINGS,
                                current_year, _rev_fmt)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
import time as _time
import re
from math import pi  # used by radar charts

# ═══════════════════════════════════════════════════════════════════
# Progress tracking
# ═══════════════════════════════════════════════════════════════════
_script_start = _time.time()

def _section(name):
    """Print a section header with timestamp."""
    elapsed = _time.time() - _script_start
    print(f"\n{'='*70}")
    print(f"[{elapsed:6.1f}s] ═══ {name} ═══")
    print(f"{'='*70}")

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
EXCEL_PATH = "/home/jain/Desktop/ws/public/company_and_job_market_research/ratings_and_reviews_at_ambitionbox.xlsx"
SAVE_DIR_BASE = "/home/jain/Desktop/ws/public/company_and_job_market_research/analytics/imgs"
SHEET_NAME = "Sheet1"

# Create a timestamped output folder (shared across all scripts)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_DIR = os.path.join(SAVE_DIR_BASE, f"img_{timestamp}")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------------------------------------------------
# 1. Data Loading & Preprocessing
# -------------------------------------------------------------------
print("Loading data...")
df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME)

NUMERIC_COLS = [
    'Rating', '#Reviews',
    'Industry level insights (%: -100 (below industry\'s average) to 100)',
    'Sample Avg Insights',
    'Company Culture', 'Salary', 'Work-Life Balance',
    'Work Satisfaction', 'Skill Development', 'Job Security', 'Promotions',
    'Founded in', 'India Employee Count', 'Global Employee Count',
    'Avg Salary (L/Yr)', 'My YOE',
    'Median current employee tenure (in years)',
    'Employee Count Growth 6M %', 'Employee Count Growth 1Y %',
    'Employee Count Growth 2Y %',
    'Hiring Trend (6M)', 'New Hires (6M)',
]
for col in NUMERIC_COLS:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Parse dates (format: "Jan / 16 / 2026")
df['Date'] = pd.to_datetime(df['Date'], format='%b / %d / %Y')

# Sort descending by Date so that 'first()' aggregations
# pick the latest row for each company
df = df.sort_values('Date', ascending=False).reset_index(drop=True)

# Extract month/year for later trends
df['YearMonth'] = df['Date'].dt.to_period('M')

print(f"  Data loaded. Shape: {df.shape}")
print(f"  Companies: {df['Company'].nunique()}, "
      f"Date range: {df['Date'].min().date()} to {df['Date'].max().date()}")
print(f"  ⏱  Loading took {_time.time() - _script_start:.1f}s")

# -------------------------------------------------------------------
# 2. Visualization Settings
# -------------------------------------------------------------------
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("Set2")
COLORS = sns.color_palette("husl", 10)

# Helper to save plots (with progress logging)
def save_plot(plt, filename):
    path = os.path.join(OUTPUT_DIR, filename)
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    rel = os.path.relpath(path, SAVE_DIR_BASE)
    print(f"  └─ saved -> {rel}")

# -------------------------------------------------------------------
# 3. Shared Constants
# -------------------------------------------------------------------
SUB_RATINGS = [
    'Company Culture', 'Salary', 'Work-Life Balance',
    'Work Satisfaction', 'Skill Development', 'Job Security', 'Promotions'
]
current_year = 2026

# -------------------------------------------------------------------
# 4. Company-Level Aggregation (company_demo)
#    Used by Sections 6–10
# -------------------------------------------------------------------
company_demo = df.groupby('Company').agg(
    avg_rating=('Rating', 'mean'),
    total_reviews=('#Reviews', 'sum'),
    founded=('Founded in', 'first'),
    india_emp=('India Employee Count', 'first'),
    global_emp=('Global Employee Count', 'first'),
    industry=('Company Industry', 'first'),
    avg_culture=('Company Culture', 'mean'),
    avg_salary=('Salary', 'mean'),
    avg_wlb=('Work-Life Balance', 'mean'),
    avg_satisfaction=('Work Satisfaction', 'mean'),
    avg_skill=('Skill Development', 'mean'),
    avg_security=('Job Security', 'mean'),
    avg_promotions=('Promotions', 'mean'),
    median_tenure=('Median current employee tenure (in years)', 'first'),
).reset_index()

# Add derived metrics
company_demo['company_age'] = current_year - company_demo['founded']
company_demo['india_pct_of_global'] = (
    company_demo['india_emp'] / company_demo['global_emp'] * 100
).round(1)

# -------------------------------------------------------------------
# 5. Revenue Parsing (used by Sections 7–10)
# -------------------------------------------------------------------
def _parse_revenue_usd(rev_str):
    """
    Parse revenue strings into numeric USD.
    Handles: 'USD 73.10 billion', '$14.4 billion (2025)',
             'USD 2.0 billion (FY2025, est.)', 'Not publicly disclosed', etc.
    Returns float (USD) or None if undisclosed/unparseable.
    """
    if not isinstance(rev_str, str):
        return None
    if 'not publicly disclosed' in rev_str.lower() or 'not available' in rev_str.lower():
        return None

    clean = re.sub(r'&#91;.*?&#93;', '', rev_str)
    clean = re.sub(r'\(.*?\)', '', clean)
    clean = clean.replace('$', 'USD ').replace('\u20b9', 'INR ')
    clean = re.sub(r'\s+', ' ', clean).strip()

    pattern = re.compile(
        r'(?:USD|US\s*\$?|INR|Rs\.?)\s*([\d,.]+)\s*(trillion|billion|million|crore|lakh)?',
        re.IGNORECASE,
    )
    m = pattern.search(clean)
    if not m:
        return None

    num = float(m.group(1).replace(',', ''))
    scale = (m.group(2) or '').lower()

    multipliers = {
        'trillion': 1e12, 'billion': 1e9, 'million': 1e6,
        'crore': 1e7, 'lakh': 1e5,
    }
    mult = multipliers.get(scale, 1)

    inr_detected = bool(re.search(r'INR|Rs\.?|Rs.', rev_str, re.IGNORECASE))
    if inr_detected and scale == 'trillion':
        return (num * 1e12) / 85.0
    if inr_detected and scale == 'crore':
        return (num * 1e7) / 85.0

    return num * mult


def _rev_fmt(val_usd: float) -> str:
    """Format a USD float into a readable short string."""
    if val_usd >= 1e12:
        return f'${val_usd/1e12:.1f}T'
    if val_usd >= 1e9:
        return f'${val_usd/1e9:.1f}B'
    if val_usd >= 1e6:
        return f'${val_usd/1e6:.0f}M'
    return f'${val_usd:,.0f}'


# Merge revenue into company_demo (and df)
company_demo['revenue_usd'] = company_demo['Company'].map(
    lambda c: _parse_revenue_usd(
        df.loc[df['Company'] == c, 'Annual Revenue as of Jun 2026'].iloc[0]
    )
)
df['revenue_usd'] = df['Company'].map(
    company_demo.set_index('Company')['revenue_usd']
)

company_demo['has_revenue'] = company_demo['revenue_usd'].notna()

num_disclosed = company_demo['has_revenue'].sum()
print(f"  Revenue parsed: {num_disclosed}/{len(company_demo)} companies disclosed")
print(f"  ⏱  Shared config ready in {_time.time() - _script_start:.1f}s\n")
