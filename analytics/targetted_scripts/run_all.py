#!/usr/bin/env python3
"""
run_all.py — Master runner for all analytics section scripts.

Usage:
    python run_all.py              # run all sections
    python run_all.py --skip 6 7   # skip sections 6 and 7

Each section script exposes a `run()` function. This runner imports and
calls them in order.  All output images land in a single timestamped
folder under analytics/imgs/.

The shared_config module is imported FIRST (by this runner) so that
data is loaded once and reused by every section.
"""

import sys
import time as _time

# -------------------------------------------------------------------
# 0. Load shared config (data, helpers, constants) — once for all
# -------------------------------------------------------------------
_runner_start = _time.time()
print("═" * 70)
print("  🚀 ANALYTICS RUNNER — starting shared config load …")
print("═" * 70)

import shared_config  # noqa: E402 — side-effect imports are intentional here

print(f"  ✅ Shared config loaded in {_time.time() - _runner_start:.1f}s\n")

# -------------------------------------------------------------------
# 1. Import all section modules
# -------------------------------------------------------------------
from section_03_mandatory_plots import run as run_s03
from section_04_insightful_plots import run as run_s04
from section_05_sub_ratings import run as run_s05
from section_06_demographics import run as run_s06
from section_07_revenue import run as run_s07
from section_08_salary import run as run_s08
from section_09_tenure import run as run_s09
from section_10_growth_hiring import run as run_s10

# -------------------------------------------------------------------
# 2. Ordered pipeline
# -------------------------------------------------------------------
PIPELINE = [
    ("03 — Mandatory Plots (1-4)",              run_s03),
    ("04 — Additional Insightful Plots (5-12)",  run_s04),
    ("05 — Sub-Rating Analysis (13-22)",         run_s05),
    ("06 — Demographics & Scale (23-34)",        run_s06),
    ("07 — Revenue Analysis (35-45)",            run_s07),
    ("08 — Salary & Experience (46-58)",         run_s08),
    ("09 — Employee Tenure (59-74)",             run_s09),
    ("10 — Growth & Hiring Trends (75-91)",      run_s10),
]

# -------------------------------------------------------------------
# 3. Handle optional --skip argument
# -------------------------------------------------------------------
skip_sections = set()
args = sys.argv[1:]
i = 0
while i < len(args):
    if args[i] == '--skip':
        i += 1
        while i < len(args) and args[i].isdigit():
            skip_sections.add(args[i])
            i += 1
    else:
        i += 1

if skip_sections:
    print(f"  ⏭  Skipping sections: {sorted(skip_sections)}\n")

# -------------------------------------------------------------------
# 4. Execute pipeline
# -------------------------------------------------------------------
section_times = {}
passed = 0
failed = 0

for label, func in PIPELINE:
    sec_id = label.split('—')[0].strip().lstrip('0')
    if sec_id in skip_sections:
        print(f"  ⏭  SKIPPED: {label}\n")
        continue

    t0 = _time.time()
    try:
        func()
        elapsed = _time.time() - t0
        section_times[label] = elapsed
        passed += 1
        print(f"  ✅ {label}  — completed in {elapsed:.1f}s\n")
    except Exception as e:
        elapsed = _time.time() - t0
        failed += 1
        print(f"  ❌ {label}  — FAILED after {elapsed:.1f}s")
        print(f"     Error: {e}")
        import traceback
        traceback.print_exc()
        print()

# -------------------------------------------------------------------
# 5. Final summary
# -------------------------------------------------------------------
_total = _time.time() - _runner_start
print("═" * 70)
print(f"  🏁 RUNNER FINISHED in {_total:.1f}s")
print(f"     Passed: {passed}/{len(PIPELINE)}  |  Failed: {failed}")
if section_times:
    print(f"     Slowest section: {max(section_times, key=section_times.get)} "
          f"({section_times[max(section_times, key=section_times.get)]:.1f}s)")
print(f"  📁 Output: {shared_config.OUTPUT_DIR}")
print("═" * 70)
