"""
preprocess.py
-------------
Loads raw poll data, cleans it, validates it,
and saves a clean version for downstream analysis.
"""

import os

import pandas as pd


RAW_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "poll_data_raw.csv")
CLEAN_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "poll_data_clean.csv")

QUESTION_COLS = [
    "Q1_preferred_platform",
    "Q2_daily_usage_hours",
    "Q3_primary_reason",
    "Q4_satisfaction",
]

ORDINAL_MAP = {
    # Q4 satisfaction - for numeric encoding
    "Very Satisfied": 5,
    "Satisfied": 4,
    "Neutral": 3,
    "Dissatisfied": 2,
    "Very Dissatisfied": 1,
    # Q2 usage hours - for numeric encoding
    "Less than 1 hr": 1,
    "1-2 hrs": 2,
    "2-4 hrs": 3,
    "More than 4 hrs": 4,
}


def load_data(path=RAW_PATH):
    """Load raw CSV into DataFrame."""
    print(f"[STEP 1] Loading data from: {path}")
    df = pd.read_csv(path)
    print(f"         Shape: {df.shape}")
    return df


def inspect_data(df):
    """Print a data quality report."""
    print("\n[STEP 2] Data Quality Report")
    print("=" * 50)
    print(f"Total rows     : {len(df)}")
    print(f"Total columns  : {df.shape[1]}")
    print(f"\nNull counts:\n{df.isnull().sum()}")
    print(f"\nDtypes:\n{df.dtypes}")
    print(f"\nDuplicate rows : {df.duplicated().sum()}")
    return df


def drop_duplicates(df):
    """Remove any exact duplicate rows."""
    print("\n[STEP 3] Removing duplicates...")
    before = len(df)
    df = df.drop_duplicates()
    after = len(df)
    print(f"         Removed {before - after} duplicate(s). Remaining: {after}")
    return df


def handle_missing_values(df):
    """
    Strategy:
    - For categorical question columns: fill with mode (most common answer)
    - For demographic columns: fill with 'Unknown'
    """
    print("\n[STEP 4] Handling missing values...")

    for col in QUESTION_COLS:
        if df[col].isnull().sum() > 0:
            mode_val = df[col].mode()[0]
            filled = df[col].isnull().sum()
            df[col] = df[col].fillna(mode_val)
            print(f"         '{col}': filled {filled} nulls with mode -> '{mode_val}'")

    demo_cols = ["region", "age_group", "gender", "education", "occupation"]
    for col in demo_cols:
        if df[col].isnull().sum() > 0:
            df[col] = df[col].fillna("Unknown")
            print(f"         '{col}': filled nulls with 'Unknown'")

    return df


def standardize_columns(df):
    """
    - Strip whitespace from string columns
    - Parse response_date as datetime
    - Add derived columns: month, day_of_week
    """
    print("\n[STEP 5] Standardizing columns...")

    str_cols = df.select_dtypes(include="object").columns
    for col in str_cols:
        df[col] = df[col].str.strip()

    df["response_date"] = pd.to_datetime(df["response_date"], errors="coerce")
    df["response_month"] = df["response_date"].dt.to_period("M").astype(str)
    df["response_day_of_week"] = df["response_date"].dt.day_name()
    df["response_week"] = df["response_date"].dt.isocalendar().week.astype(int)

    print("         Date parsed -> month, day_of_week, week columns added.")
    return df


def add_encoded_columns(df):
    """
    Add numeric ordinal encodings for Q2 and Q4
    for correlation / heatmap analysis.
    """
    print("\n[STEP 6] Adding encoded columns...")
    df["Q2_usage_numeric"] = df["Q2_daily_usage_hours"].map(ORDINAL_MAP)
    df["Q4_satisfaction_numeric"] = df["Q4_satisfaction"].map(ORDINAL_MAP)
    print("         Q2_usage_numeric and Q4_satisfaction_numeric added.")
    return df


def validate_data(df):
    """Final validation: check no critical nulls remain."""
    print("\n[STEP 7] Final validation...")
    critical_nulls = df[QUESTION_COLS].isnull().sum().sum()
    if critical_nulls == 0:
        print(f"         [OK] No nulls in question columns. Clean shape: {df.shape}")
    else:
        print(f"         [WARN] {critical_nulls} nulls remain in question columns!")
    return df


def save_clean(df, path=CLEAN_PATH):
    """Save clean DataFrame to CSV."""
    df.to_csv(path, index=False)
    print(f"\n[SUCCESS] Clean data saved -> {path}")


def preprocess_pipeline(raw_path=RAW_PATH, clean_path=CLEAN_PATH):
    """Run the full preprocessing pipeline."""
    print("\n" + "=" * 60)
    print("  PREPROCESSING PIPELINE - Poll Results Visualizer")
    print("=" * 60)
    df = load_data(raw_path)
    df = inspect_data(df)
    df = drop_duplicates(df)
    df = handle_missing_values(df)
    df = standardize_columns(df)
    df = add_encoded_columns(df)
    df = validate_data(df)
    save_clean(df, clean_path)
    return df


if __name__ == "__main__":
    preprocess_pipeline()
