"""
analysis.py
-----------
Core analysis helpers for the Poll Results Visualizer notebook and scripts.
"""

from __future__ import annotations

import os

import pandas as pd


PLATFORM_COL = "Q1_preferred_platform"
USAGE_COL = "Q2_daily_usage_hours"
USAGE_NUMERIC_COL = "Q2_usage_numeric"
REASON_COL = "Q3_primary_reason"
SATISFACTION_COL = "Q4_satisfaction"
SATISFACTION_NUMERIC_COL = "Q4_satisfaction_numeric"
MONTH_COL = "response_month"
DEFAULT_CLEAN_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "poll_data_clean.csv"
)

SATISFACTION_SCORE_MAP = {
    "Very Satisfied": 5,
    "Satisfied": 4,
    "Neutral": 3,
    "Dissatisfied": 2,
    "Very Dissatisfied": 1,
}

SATISFACTION_ORDER = [
    "Very Satisfied",
    "Satisfied",
    "Neutral",
    "Dissatisfied",
    "Very Dissatisfied",
]

USAGE_ORDER = [
    "Less than 1 hr",
    "1-2 hrs",
    "2-4 hrs",
    "More than 4 hrs",
]


def _validate_columns(df: pd.DataFrame, required_columns: list[str]) -> None:
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def load_clean(path: str = DEFAULT_CLEAN_PATH) -> pd.DataFrame:
    """Load the cleaned poll dataset."""
    return pd.read_csv(path, parse_dates=["response_date"])


def overall_vote_share(df: pd.DataFrame) -> pd.DataFrame:
    """Return platform vote counts and percentages."""
    _validate_columns(df, [PLATFORM_COL])

    counts = df[PLATFORM_COL].value_counts(dropna=False)
    result = counts.rename_axis("Option").reset_index(name="Count")
    result["Percentage"] = (result["Count"] / result["Count"].sum() * 100).round(2)
    return result


def region_wise_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Return percentage platform share within each region."""
    _validate_columns(df, ["region", PLATFORM_COL])

    breakdown = pd.crosstab(
        df["region"],
        df[PLATFORM_COL],
        normalize="index",
    ).mul(100).round(2)
    return breakdown.sort_index()


def age_group_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Return percentage platform share within each age group."""
    _validate_columns(df, ["age_group", PLATFORM_COL])

    ordered_age_groups = ["13-17", "18-24", "25-34", "35-44", "45-54", "55+"]
    breakdown = pd.crosstab(
        df["age_group"],
        df[PLATFORM_COL],
        normalize="index",
    ).mul(100).round(2)

    present_order = [age for age in ordered_age_groups if age in breakdown.index]
    remaining = [age for age in breakdown.index if age not in present_order]
    return breakdown.reindex(present_order + remaining)


def satisfaction_by_platform(df: pd.DataFrame) -> pd.DataFrame:
    """Return average satisfaction score by preferred platform."""
    _validate_columns(df, [PLATFORM_COL, SATISFACTION_COL])

    working_df = df.copy()
    if SATISFACTION_NUMERIC_COL not in working_df.columns:
        working_df[SATISFACTION_NUMERIC_COL] = working_df[SATISFACTION_COL].map(
            SATISFACTION_SCORE_MAP
        )

    summary = (
        working_df.groupby(PLATFORM_COL, as_index=False)[SATISFACTION_NUMERIC_COL]
        .agg(["mean", "count"])
        .reset_index()
        .rename(
            columns={
                PLATFORM_COL: "Platform",
                "mean": "Avg_Satisfaction_Score",
                "count": "Responses",
            }
        )
        .sort_values("Avg_Satisfaction_Score", ascending=False)
    )

    summary["Avg_Satisfaction_Score"] = summary["Avg_Satisfaction_Score"].round(2)
    summary["Responses"] = summary["Responses"].astype(int)
    return summary.reset_index(drop=True)


def satisfaction_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Return ordered satisfaction counts and percentages."""
    _validate_columns(df, [SATISFACTION_COL])

    counts = (
        df[SATISFACTION_COL]
        .value_counts()
        .reindex(SATISFACTION_ORDER, fill_value=0)
        .rename_axis("Satisfaction")
        .reset_index(name="Count")
    )
    counts["Percentage"] = (counts["Count"] / counts["Count"].sum() * 100).round(2)
    return counts


def usage_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Return ordered daily usage counts and percentages."""
    _validate_columns(df, [USAGE_COL])

    counts = (
        df[USAGE_COL]
        .value_counts()
        .reindex(USAGE_ORDER, fill_value=0)
        .rename_axis("Usage_Hours")
        .reset_index(name="Count")
    )
    counts["Percentage"] = (counts["Count"] / counts["Count"].sum() * 100).round(2)
    return counts


def avg_usage_by_platform(df: pd.DataFrame) -> pd.DataFrame:
    """Return average encoded usage hours by preferred platform."""
    _validate_columns(df, [PLATFORM_COL, USAGE_COL])

    working_df = df.copy()
    if USAGE_NUMERIC_COL not in working_df.columns:
        usage_map = {label: i + 1 for i, label in enumerate(USAGE_ORDER)}
        working_df[USAGE_NUMERIC_COL] = working_df[USAGE_COL].map(usage_map)

    summary = (
        working_df.groupby(PLATFORM_COL, as_index=False)[USAGE_NUMERIC_COL]
        .agg(["mean", "count"])
        .reset_index()
        .rename(
            columns={
                PLATFORM_COL: "Platform",
                "mean": "Avg_Usage_Score",
                "count": "Responses",
            }
        )
        .sort_values("Avg_Usage_Score", ascending=False)
    )
    summary["Avg_Usage_Score"] = summary["Avg_Usage_Score"].round(2)
    summary["Responses"] = summary["Responses"].astype(int)
    return summary.reset_index(drop=True)


def reason_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Return overall primary-reason counts and percentages."""
    _validate_columns(df, [REASON_COL])

    counts = df[REASON_COL].value_counts().rename_axis("Reason").reset_index(name="Count")
    counts["Percentage"] = (counts["Count"] / counts["Count"].sum() * 100).round(2)
    return counts


def reason_by_platform(df: pd.DataFrame) -> pd.DataFrame:
    """Return percentage reason breakdown within each platform."""
    _validate_columns(df, [PLATFORM_COL, REASON_COL])

    breakdown = pd.crosstab(
        df[PLATFORM_COL],
        df[REASON_COL],
        normalize="index",
    ).mul(100).round(2)
    return breakdown.sort_index()


def net_satisfaction_score(df: pd.DataFrame) -> dict[str, float]:
    """
    Net satisfaction score = % positive - % negative.
    Positive: Very Satisfied, Satisfied
    Negative: Dissatisfied, Very Dissatisfied
    """
    _validate_columns(df, [SATISFACTION_COL])

    total = len(df)
    if total == 0:
        return {
            "positive_pct": 0.0,
            "negative_pct": 0.0,
            "neutral_pct": 0.0,
            "net_satisfaction_score": 0.0,
        }

    positive_pct = (
        df[SATISFACTION_COL].isin(["Very Satisfied", "Satisfied"]).sum() / total * 100
    )
    negative_pct = (
        df[SATISFACTION_COL]
        .isin(["Dissatisfied", "Very Dissatisfied"])
        .sum()
        / total
        * 100
    )
    neutral_pct = (df[SATISFACTION_COL].eq("Neutral").sum() / total * 100)

    return {
        "positive_pct": round(float(positive_pct), 2),
        "negative_pct": round(float(negative_pct), 2),
        "neutral_pct": round(float(neutral_pct), 2),
        "net_satisfaction_score": round(float(positive_pct - negative_pct), 2),
    }


def monthly_trend(df: pd.DataFrame, top_n: int = 3) -> pd.DataFrame:
    """Return monthly response counts for the top N preferred platforms."""
    _validate_columns(df, [MONTH_COL, PLATFORM_COL])

    top_platforms = df[PLATFORM_COL].value_counts().head(top_n).index.tolist()
    trend = pd.crosstab(df[MONTH_COL], df[PLATFORM_COL])[top_platforms]
    return trend.sort_index()


def generate_summary(df: pd.DataFrame) -> str:
    """Generate a concise text summary for notebook conclusions."""
    _validate_columns(df, ["region", "age_group", PLATFORM_COL, SATISFACTION_COL])

    vote = overall_vote_share(df)
    top_platform = vote.iloc[0]

    age_breakdown = age_group_breakdown(df)
    top_age_group = age_breakdown[top_platform["Option"]].idxmax()

    region_breakdown = region_wise_breakdown(df)
    top_region = region_breakdown[top_platform["Option"]].idxmax()

    nss = net_satisfaction_score(df)

    summary_lines = [
        f"Top platform overall: {top_platform['Option']} with {top_platform['Percentage']:.2f}% of responses.",
        f"Strongest support for {top_platform['Option']} appears in the {top_age_group} age group.",
        f"{top_platform['Option']} is most dominant in {top_region}.",
        (
            "Net satisfaction score is "
            f"{nss['net_satisfaction_score']:+.2f}, based on {nss['positive_pct']:.2f}% positive "
            f"and {nss['negative_pct']:.2f}% negative responses."
        ),
    ]
    return "\n".join(summary_lines)
