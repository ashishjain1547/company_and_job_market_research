#!/usr/bin/env python3
"""
get_annual_revenue.py

Populates a new column "Annual Revenue as of Jun 2026" in the AmbitionBox Excel
file using a multi-tier fallback strategy:

    Tier 1 – yfinance      (free, fast, reliable for public companies)
    Tier 2 – Wikipedia      (scrapes infobox for private + public companies)
    Tier 3 – DeepSeek API   (LLM-based lookup for hard-to-find companies)
    Tier 4 – "Not available" (final fallback)

Uses a local JSON cache so interrupted runs can resume without re-querying.
Each cache entry records {revenue, source} for auditability.
"""

import json
import os
import re
import time
from pathlib import Path

import pandas as pd
import requests
import yfinance as yf
from openai import OpenAI

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
EXCEL_PATH = "/home/jain/Desktop/ws/public/company_and_job_market_research/ratings_and_reviews_at_ambitionbox.xlsx"
API_KEYS_PATH = "/home/jain/Desktop/ws/api_keys_in_laptop.json"
API_KEY_NAME = "deepseek_ashishjain1547"
CACHE_PATH = "/home/jain/Desktop/ws/public/company_and_job_market_research/data engineering/revenue_cache.json"

# DeepSeek API (OpenAI-compatible)
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

# Column name to add
NEW_COLUMN = "Annual Revenue as of Jun 2026"

# ---------------------------------------------------------------------------
# Ticker map — company name → Yahoo Finance ticker
# Covers all 37 unique companies in the Excel file.
# ---------------------------------------------------------------------------
TICKER_MAP: dict[str, str] = {
    "Accenture":                                          "ACN",
    "Altimetrik":                                         None,       # private
    "Amazon":                                             "AMZN",
    "American Express":                                   "AXP",
    "Axtria":                                             None,       # private
    "Boston Consulting Group":                            None,       # private
    "Bounteous x Accolite (Accolite Digital India Pvt. Ltd.)": None,  # private
    "Capgemini":                                          "CAP.PA",   # Euronext Paris
    "Chegg":                                              "CHGG",
    "Cognizant":                                          "CTSH",
    "Deeplearning.ai":                                    None,       # private / edu
    "Dentsu Global Services":                             "4324.T",   # Tokyo (Dentsu Group)
    "EXL Service":                                        "EXLS",
    "GSPANN":                                             None,       # private
    "Genpact":                                            "G",
    "Google":                                             "GOOGL",
    "HCLTech":                                            "HCLTECH.NS",
    "HMH Technology Private Limited":                     None,       # private
    "IBM":                                                "IBM",
    "IBM Consulting":                                     "IBM",      # subsidiary of IBM
    "Infosys":                                            "INFY",
    "KPMG India":                                         None,       # private partnership
    "Khan Academy":                                       None,       # non-profit
    "Lumen Technologies":                                 "LUMN",
    "Mindlance":                                          None,       # private
    "Nagarro":                                            "NA9.DE",   # Frankfurt
    "Optum Global Solutions ":                             "UNH",      # subsidiary of UnitedHealth
    "Procore":                                            "PCOR",
    "PwC":                                                None,       # private partnership
    "S&P Global":                                         "SPGI",
    "Siemens Energy":                                     "ENR.DE",   # Xetra
    "Statusneo":                                          None,       # private
    "TCS":                                                "TCS.NS",
    "TECHPINNACLE BIT SOLUTIONS":                         None,       # private
    "Tredence":                                           None,       # private
    "ZS":                                                 None,       # private
}

# ---------------------------------------------------------------------------
# Cache helpers — each entry is {"revenue": str, "source": str}
# ---------------------------------------------------------------------------


def load_cache() -> dict[str, dict]:
    """Load cached results (company → {revenue, source})."""
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r") as fh:
            return json.load(fh)
    return {}


def save_cache(cache: dict[str, dict]) -> None:
    """Persist cache to disk."""
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, "w") as fh:
        json.dump(cache, fh, indent=2, sort_keys=True)


# ---------------------------------------------------------------------------
# Tier 1 – yfinance
# ---------------------------------------------------------------------------

def _fmt_billion(val_usd: float) -> str:
    """Format a USD value into a readable string."""
    if abs(val_usd) >= 1e12:
        return f"USD {val_usd/1e12:.2f} trillion"
    if abs(val_usd) >= 1e9:
        return f"USD {val_usd/1e9:.2f} billion"
    if abs(val_usd) >= 1e6:
        return f"USD {val_usd/1e6:.0f} million"
    return f"USD {val_usd:,.0f}"


def _usd_to_inr_crore(val_usd: float) -> str:
    """Convert USD to INR crore (approx rate: 1 USD ≈ 85 INR, Jun 2026)."""
    usd_to_inr = 85.0
    inr = val_usd * usd_to_inr
    if inr >= 1e7:  # 1 crore = 1e7
        return f"~INR {inr/1e7:,.0f} crore"
    return f"~INR {inr:,.0f}"


def try_yfinance(company: str) -> tuple[str, str] | None:
    """
    Attempt to fetch annual revenue via Yahoo Finance.
    Returns (revenue_string, source_label) or None.
    """
    ticker_symbol = TICKER_MAP.get(company)
    if ticker_symbol is None:
        return None  # no ticker mapped → skip

    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info

        # Prefer totalRevenue from financials; fall back to info dict
        revenue = info.get("totalRevenue") or info.get("revenue")

        if revenue and revenue > 0:
            fy = ""
            mf = info.get("mostRecentQuarter")
            if mf:
                fy = f" (as of {mf.strftime('%b %Y')})" if hasattr(mf, "strftime") else ""
            else:
                # Try to extract from financials
                try:
                    fin = ticker.financials
                    if not fin.empty and "Total Revenue" in fin.index:
                        latest_col = fin.columns[0]
                        fy = f" (FY{latest_col.year})" if hasattr(latest_col, "year") else ""
                except Exception:
                    pass

            result = _fmt_billion(revenue) + fy
            return (result, f"yfinance:{ticker_symbol}")

        # fallback: try financials DataFrame directly
        try:
            fin = ticker.financials
            if not fin.empty and "Total Revenue" in fin.index:
                rev = fin.loc["Total Revenue"].iloc[0]
                if rev and rev > 0:
                    latest_col = fin.columns[0]
                    fy = f" (FY{latest_col.year})" if hasattr(latest_col, "year") else ""
                    result = _fmt_billion(rev) + fy
                    return (result, f"yfinance:{ticker_symbol} (financials)")
        except Exception:
            pass

    except Exception as exc:
        print(f"  ⚠ yfinance error for {ticker_symbol}: {exc}")

    return None


# ---------------------------------------------------------------------------
# Tier 2 – Wikipedia
# ---------------------------------------------------------------------------

# Regex patterns to extract revenue from Wikipedia infobox text
_RE_REVENUE_USD = re.compile(
    r"(?:US\$|USD\s*|US\s*\$\s*|\\?US\s*\$|\\?US\s*\$\s*|US\$)([\d,.]+)\s*(trillion|billion|million|T|B|M)",
    re.IGNORECASE,
)
_RE_REVENUE_INR = re.compile(
    r"(?:₹|INR\s*|Rs\.?\s*)([\d,.]+\s*(?:lakh|crore|trillion|billion|million))",
    re.IGNORECASE,
)
_RE_REVENUE_CROre = re.compile(
    r"([\d,]+)\s*crore",
    re.IGNORECASE,
)
_RE_PLAIN_USD = re.compile(
    r"revenue.*?(?:US|USD?\s*\$?\s*|\\?US\s*\$?)([\d,.]+)\s*(trillion|billion|million)",
    re.IGNORECASE,
)

# Wikipedia pages to try for companies not matching their exact name
WIKI_OVERRIDES: dict[str, str] = {
    "Boston Consulting Group": "Boston_Consulting_Group",
    "Bounteous x Accolite (Accolite Digital India Pvt. Ltd.)": None,
    "Deeplearning.ai": "DeepLearning.AI",
    "Dentsu Global Services": "Dentsu",
    "EXL Service": "EXL_Service",
    "GSPANN": "GSPANN_Technologies",
    "HCLTech": "HCLTech",
    "HMH Technology Private Limited": "Houghton_Mifflin_Harcourt",
    "IBM Consulting": "IBM_Consulting",
    "KPMG India": "KPMG",
    "Khan Academy": "Khan_Academy",
    "Mindlance": None,
    "Optum Global Solutions ": "Optum",
    "PwC": "PricewaterhouseCoopers",
    "S&P Global": "S%26P_Global",
    "Statusneo": None,
    "TECHPINNACLE BIT SOLUTIONS": None,
    "Tredence": None,
    "ZS": "ZS_Associates",
}


def _wiki_page_name(company: str) -> str | None:
    """Resolve Wikipedia page name for a company."""
    if company in WIKI_OVERRIDES:
        return WIKI_OVERRIDES[company]
    return company.replace(" ", "_").replace("&", "%26")


def try_wikipedia(company: str) -> tuple[str, str] | None:
    """
    Attempt to scrape annual revenue from the Wikipedia infobox.
    Returns (revenue_string, source_label) or None.
    """
    page_name = _wiki_page_name(company)
    if page_name is None:
        return None

    url = f"https://en.wikipedia.org/wiki/{page_name}"
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "RevenueBot/1.0"})
        if resp.status_code != 200:
            return None

        html = resp.text

        # Strategy 1: Look for "Revenue" row in infobox table
        # Pattern: <th>Revenue</th><td>...US$12.3 billion...</td>
        revenue_pattern = re.compile(
            r'<th[^>]*>\s*Revenue\s*</th>\s*<td[^>]*>(.*?)</td>',
            re.DOTALL | re.IGNORECASE,
        )
        match = revenue_pattern.search(html)
        if match:
            td_content = match.group(1)
            # Strip HTML tags
            td_text = re.sub(r"<[^>]+>", " ", td_content)
            td_text = re.sub(r"\[.*?\]", "", td_text)  # remove citations
            td_text = re.sub(r"&nbsp;", " ", td_text)
            td_text = re.sub(r"\s+", " ", td_text).strip()

            # Try USD match
            usd = _RE_REVENUE_USD.search(td_text)
            if usd:
                return (f"USD {usd.group(1)} {usd.group(2).lower()}", f"wikipedia:{page_name}")

            # Try INR crore match
            inr = _RE_REVENUE_CROre.search(td_text)
            if inr:
                return (f"₹{inr.group(1)} crore", f"wikipedia:{page_name}")

            # Return raw text if nothing matched
            if td_text and len(td_text) < 120:
                return (td_text, f"wikipedia:{page_name}")

        # Strategy 2: Broader search in the whole infobox
        infobox_pattern = re.compile(
            r'<table[^>]*class="[^"]*infobox[^"]*"[^>]*>(.*?)</table>',
            re.DOTALL | re.IGNORECASE,
        )
        infobox_match = infobox_pattern.search(html)
        if infobox_match:
            infobox_text = infobox_match.group(1)
            infobox_text = re.sub(r"<[^>]+>", " ", infobox_text)
            infobox_text = re.sub(r"\[.*?\]", "", infobox_text)
            infobox_text = re.sub(r"&nbsp;", " ", infobox_text)
            infobox_text = re.sub(r"\s+", " ", infobox_text)

            # Look for revenue keyword + USD amount
            m = _RE_PLAIN_USD.search(infobox_text)
            if m:
                return (f"USD {m.group(1)} {m.group(2).lower()}", f"wikipedia:{page_name}")

    except requests.RequestException as exc:
        print(f"  ⚠ Wikipedia error for '{company}': {exc}")
    except Exception as exc:
        print(f"  ⚠ Wikipedia parse error for '{company}': {exc}")

    return None


# ---------------------------------------------------------------------------
# Tier 3 – DeepSeek API
# ---------------------------------------------------------------------------


def try_deepseek(client: OpenAI, company: str) -> tuple[str, str] | None:
    """
    Ask DeepSeek for the company's most recent annual revenue.
    Returns (revenue_string, source_label) or None.
    """
    system_prompt = (
        "You are a financial data assistant. "
        "For the given company, return ONLY the most recent annual revenue "
        "as of mid-2026 (fiscal year ending in 2025 or early 2026).\n\n"
        "Format your answer EXACTLY like one of these examples:\n"
        "- USD 61.9 billion (FY2025)\n"
        "- USD 350 million (FY2024, est.)\n"
        "- ~INR 1,200 crore (FY2025, est.)\n"
        "- Not publicly disclosed\n"
        "- Not available\n\n"
        "Rules:\n"
        "1. Prefer the latest fiscal year available (FY2025 or FY2026).\n"
        "2. If only an estimate exists, mark it with '(est.)'.\n"
        "3. Give ONE line only — no explanation, no markdown, no extra text.\n"
        "4. If the company is a subsidiary, give the subsidiary's own revenue "
        "if known, otherwise the parent's.\n"
        "5. For private companies that don't disclose revenue, say "
        "'Not publicly disclosed'."
    )

    user_prompt = f"Annual revenue for: {company}"

    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
            max_tokens=80,
        )
        text = response.choices[0].message.content.strip()
        text = text.strip('"').strip("'").strip("`")
        if text:
            return (text, "deepseek")
    except Exception as exc:
        print(f"  ⚠ DeepSeek API error for '{company}': {exc}")

    return None


# ---------------------------------------------------------------------------
# Orchestrator — tries each tier in order
# ---------------------------------------------------------------------------


def get_revenue(client: OpenAI, company: str) -> tuple[str, str]:
    """
    Try each data source in priority order until one succeeds.
    Returns (revenue_string, source_label).
    """
    # Tier 1 – yfinance
    result = try_yfinance(company)
    if result:
        revenue, source = result
        print(f"[yfinance] {revenue}")
        return (revenue, source)

    # Tier 2 – Wikipedia
    result = try_wikipedia(company)
    if result:
        revenue, source = result
        print(f"[wikipedia] {revenue}")
        return (revenue, source)

    # Tier 3 – DeepSeek
    result = try_deepseek(client, company)
    if result:
        revenue, source = result
        print(f"[deepseek]  {revenue}")
        return (revenue, source)

    # Tier 4 – Final fallback
    print("[none]     Not available")
    return ("Not available", "none")


# ---------------------------------------------------------------------------
# API key loader
# ---------------------------------------------------------------------------


def load_api_key() -> str:
    """Load the DeepSeek API key from the local JSON file."""
    with open(API_KEYS_PATH, "r") as fh:
        keys = json.load(fh)
    key = keys.get(API_KEY_NAME)
    if not key:
        raise KeyError(f"Key '{API_KEY_NAME}' not found in {API_KEYS_PATH}")
    return key


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    # 1. Load data
    print("=" * 60)
    print("Loading Excel …")
    df = pd.read_excel(EXCEL_PATH)
    print(f"  Rows: {df.shape[0]} | Columns: {df.shape[1]}")
    print(f"  Unique companies: {df['Company'].nunique()}")

    unique_companies = sorted(df["Company"].dropna().unique())
    print(f"  Companies ({len(unique_companies)}):")
    for c in unique_companies:
        ticker = TICKER_MAP.get(c)
        has_wiki = _wiki_page_name(c) is not None
        flags = []
        if ticker:
            flags.append(f"yf:{ticker}")
        if has_wiki:
            flags.append("wiki")
        print(f"    {c:50s}  {', '.join(flags) if flags else '(manual/deepseek only)'}")

    # 2. Load cache
    cache = load_cache()
    print(f"\nCache hits: {len(cache)}")

    # 3. Set up DeepSeek client (only if needed)
    deepseek_client = None
    missing = [c for c in unique_companies if c not in cache]

    # Count how many need DeepSeek (no yfinance + no wikipedia)
    need_deepseek = sum(
        1 for c in missing
        if TICKER_MAP.get(c) is None and _wiki_page_name(c) is None
    )
    if need_deepseek > 0:
        print(f"  Companies needing DeepSeek (no ticker, no wiki): {need_deepseek}")
        api_key = load_api_key()
        deepseek_client = OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)
    else:
        print("  DeepSeek not needed — all companies have ticker/wiki coverage.")

    # 4. Query missing companies with fallback chain
    print(f"\nCompanies to query: {len(missing)}")
    if missing:
        print("-" * 40)

    yf_count = wiki_count = ds_count = none_count = 0

    for i, company in enumerate(missing, 1):
        print(f"  [{i:02d}/{len(missing):02d}] {company:45s} ", end="", flush=True)
        revenue, source = get_revenue(deepseek_client, company)

        # Count sources
        if source.startswith("yfinance"):
            yf_count += 1
        elif source.startswith("wikipedia"):
            wiki_count += 1
        elif source == "deepseek":
            ds_count += 1
        else:
            none_count += 1

        cache[company] = {"revenue": revenue, "source": source}
        save_cache(cache)

        # Rate-limit for DeepSeek tier
        if source == "deepseek" and i < len(missing):
            time.sleep(1.2)

    # 5. Map revenue to every row
    print("\n" + "=" * 60)
    print("Mapping revenue to DataFrame …")
    df[NEW_COLUMN] = df["Company"].map(lambda c: cache[c]["revenue"])

    # 6. Write back
    print(f"Writing to: {EXCEL_PATH}")
    df.to_excel(EXCEL_PATH, index=False)

    # 7. Summary
    print(f"\nDone.  Source breakdown:")
    print(f"  yfinance:      {yf_count}")
    print(f"  Wikipedia:     {wiki_count}")
    print(f"  DeepSeek:      {ds_count}")
    print(f"  Not available: {none_count}")
    print(f"\n  Revenue summary:")
    for company in unique_companies:
        entry = cache.get(company, {})
        rev = entry.get("revenue", "???")
        src = entry.get("source", "???")
        print(f"  {company:45s} → {rev:45s} [{src}]")

    print(f"\nCache saved to: {CACHE_PATH}")


if __name__ == "__main__":
    main()
