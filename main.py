"""
main.py
-------
Entry point for Poll Results Visualizer.
Runs the full pipeline:
  1. Generate synthetic poll data
  2. Preprocess and clean
  3. Analyze
  4. Visualize
  5. Print executive summary
  6. Export report
"""

import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from analysis import generate_summary, load_clean, overall_vote_share, satisfaction_by_platform
from generate_data import generate_dataset
from preprocess import preprocess_pipeline
from visualize import generate_all_charts


RAW_PATH = os.path.join("data", "poll_data_raw.csv")
CLEAN_PATH = os.path.join("data", "poll_data_clean.csv")
REPORT_PATH = os.path.join("outputs", "reports", "summary_report.txt")
os.makedirs(os.path.join("outputs", "reports"), exist_ok=True)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("\n" + "=" * 62)
    print("        POLL RESULTS VISUALIZER - FULL PIPELINE")
    print("=" * 62 + "\n")

    # STEP 1: Generate raw data if it does not already exist.
    if not os.path.exists(RAW_PATH):
        print(">>> STEP 1: Generating synthetic poll dataset...")
        df_raw = generate_dataset(n=1200)
        df_raw.to_csv(RAW_PATH, index=False)
        print(f"    Raw data saved to: {RAW_PATH}\n")
    else:
        print(f">>> STEP 1: Raw data found at {RAW_PATH} - skipping generation.\n")

    # STEP 2: Clean and enrich the data for downstream analysis.
    print(">>> STEP 2: Preprocessing data...")
    preprocess_pipeline(RAW_PATH, CLEAN_PATH)
    print()

    # STEP 3: Load the clean dataset and generate a short summary.
    print(">>> STEP 3: Running analysis...\n")
    df = load_clean(CLEAN_PATH)
    summary = generate_summary(df)
    print(summary)

    # STEP 4: Export the chart pack.
    print("\n>>> STEP 4: Generating charts...")
    generate_all_charts(df)

    # STEP 5: Save the text report.
    print(f"\n>>> STEP 5: Saving text report to {REPORT_PATH}...")
    with open(REPORT_PATH, "w", encoding="utf-8") as file:
        file.write(summary)
        file.write("\n\n=== VOTE SHARE DETAIL ===\n")
        file.write(overall_vote_share(df).to_string(index=False))
        file.write("\n\n=== SATISFACTION BY PLATFORM ===\n")
        file.write(satisfaction_by_platform(df).to_string(index=False))

    print("\n" + "=" * 62)
    print("  PIPELINE COMPLETE")
    print("  Charts  -> outputs/charts/")
    print("  Report  -> outputs/reports/summary_report.txt")
    print("  Dataset -> data/poll_data_clean.csv")
    print("=" * 62 + "\n")


if __name__ == "__main__":
    main()
