"""
visualize.py
------------
Full visualization engine for Poll Results Visualizer.
Generates 8 high-quality charts covering:
  - Vote share bar chart
  - Vote share pie/donut chart
  - Region-wise stacked bar
  - Age-group heatmap
  - Monthly trend line chart
  - Satisfaction gauge/bar
  - Usage hours distribution
  - Satisfaction vs Usage scatter
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import seaborn as sns
import os
import warnings
warnings.filterwarnings("ignore")

# ── Paths ──────────────────────────────────────────────────────────────────
CLEAN_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "poll_data_clean.csv")
CHARTS_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs", "charts")
os.makedirs(CHARTS_DIR, exist_ok=True)

# ── Import analysis functions ───────────────────────────────────────────────
from analysis import (
    overall_vote_share, region_wise_breakdown, age_group_breakdown,
    monthly_trend, satisfaction_distribution, satisfaction_by_platform,
    usage_distribution, avg_usage_by_platform, reason_distribution,
    net_satisfaction_score
)

# ── Style Configuration ─────────────────────────────────────────────────────
PALETTE = ["#2563EB", "#7C3AED", "#DB2777", "#D97706", "#059669", "#DC2626"]
BACKGROUND = "#F8FAFC"
GRID_COLOR = "#E2E8F0"
TEXT_COLOR = "#1E293B"
FONT_FAMILY = "DejaVu Sans"

plt.rcParams.update({
    "font.family": FONT_FAMILY,
    "axes.facecolor": BACKGROUND,
    "figure.facecolor": "white",
    "axes.edgecolor": "#CBD5E1",
    "axes.labelcolor": TEXT_COLOR,
    "xtick.color": TEXT_COLOR,
    "ytick.color": TEXT_COLOR,
    "text.color": TEXT_COLOR,
    "axes.grid": True,
    "grid.color": GRID_COLOR,
    "grid.linestyle": "--",
    "grid.alpha": 0.7,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

DPI = 150
SAVE_KWARGS = dict(dpi=DPI, bbox_inches="tight", facecolor="white")


def save_fig(fig, name):
    path = os.path.join(CHARTS_DIR, f"{name}.png")
    fig.savefig(path, **SAVE_KWARGS)
    print(f"   ✅ Saved: {path}")
    plt.close(fig)


# ─────────────────────────────────────────────────────────────────────────────
# CHART 1 — Horizontal Bar Chart: Overall Vote Share
# ─────────────────────────────────────────────────────────────────────────────

def chart_vote_share_bar(df):
    print("[CHART 1] Overall Vote Share — Horizontal Bar")
    data = overall_vote_share(df)

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = PALETTE[:len(data)]
    bars = ax.barh(data["Option"], data["Percentage"], color=colors,
                   edgecolor="white", linewidth=0.8, height=0.6)

    # Value labels
    for bar, pct, count in zip(bars, data["Percentage"], data["Count"]):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                f"{pct:.1f}%  ({count:,} votes)", va="center", fontsize=10, color=TEXT_COLOR)

    ax.set_xlabel("Response Share (%)", fontsize=11)
    ax.set_title("Q1 — Most Preferred Social Media Platform", fontsize=14, fontweight="bold", pad=15)
    ax.invert_yaxis()
    ax.set_xlim(0, data["Percentage"].max() + 10)
    ax.axvline(x=data["Percentage"].iloc[0], color="#94A3B8", linestyle="--", alpha=0.5)
    fig.text(0.92, 0.01, "Poll Results Visualizer", ha="right", fontsize=7, color="#94A3B8")

    save_fig(fig, "01_vote_share_bar")


# ─────────────────────────────────────────────────────────────────────────────
# CHART 2 — Donut Chart: Vote Share
# ─────────────────────────────────────────────────────────────────────────────

def chart_vote_share_donut(df):
    print("[CHART 2] Vote Share — Donut Chart")
    data = overall_vote_share(df)

    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(
        data["Percentage"],
        labels=None,
        colors=PALETTE[:len(data)],
        autopct="%1.1f%%",
        startangle=90,
        pctdistance=0.82,
        wedgeprops=dict(width=0.55, edgecolor="white", linewidth=2),
    )

    for at in autotexts:
        at.set_fontsize(10)
        at.set_color("white")
        at.set_fontweight("bold")

    # Centre label
    ax.text(0, 0, f"{data['Count'].sum():,}\nRespondents",
            ha="center", va="center", fontsize=13, fontweight="bold", color=TEXT_COLOR)

    # Legend
    legend = ax.legend(
        wedges,
        [f"{row.Option} ({row.Percentage:.1f}%)" for _, row in data.iterrows()],
        loc="lower center", bbox_to_anchor=(0.5, -0.08), ncol=3,
        fontsize=9, frameon=False
    )

    ax.set_title("Q1 — Platform Preference Distribution", fontsize=14, fontweight="bold", pad=20)
    save_fig(fig, "02_vote_share_donut")


# ─────────────────────────────────────────────────────────────────────────────
# CHART 3 — Stacked Bar: Region-wise Breakdown
# ─────────────────────────────────────────────────────────────────────────────

def chart_region_stacked(df):
    print("[CHART 3] Region-wise Stacked Bar")
    data = region_wise_breakdown(df)

    fig, ax = plt.subplots(figsize=(12, 6))
    bottom = np.zeros(len(data))
    cols = data.columns.tolist()

    for i, col in enumerate(cols):
        bars = ax.bar(data.index, data[col], bottom=bottom,
                      color=PALETTE[i % len(PALETTE)], label=col,
                      edgecolor="white", linewidth=0.5)
        # Label if segment wide enough
        for bar, val in zip(bars, data[col]):
            if val > 6:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_y() + bar.get_height() / 2,
                    f"{val:.0f}%", ha="center", va="center",
                    fontsize=8, color="white", fontweight="bold"
                )
        bottom += data[col].values

    ax.set_xlabel("Region", fontsize=11)
    ax.set_ylabel("Percentage Share (%)", fontsize=11)
    ax.set_title("Q1 — Platform Preference by Region", fontsize=14, fontweight="bold", pad=15)
    ax.set_ylim(0, 105)
    ax.legend(loc="upper right", fontsize=9, framealpha=0.9, ncol=2)
    plt.xticks(rotation=15)
    save_fig(fig, "03_region_stacked_bar")


# ─────────────────────────────────────────────────────────────────────────────
# CHART 4 — Heatmap: Age-group vs Platform
# ─────────────────────────────────────────────────────────────────────────────

def chart_age_heatmap(df):
    print("[CHART 4] Age-group × Platform Heatmap")
    data = age_group_breakdown(df)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(
        data, annot=True, fmt=".1f", cmap="Blues",
        linewidths=0.5, linecolor="#E2E8F0",
        ax=ax, cbar_kws={"label": "% of Age Group"}
    )
    ax.set_title("Q1 — Platform Preference by Age Group (%)", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Platform", fontsize=11)
    ax.set_ylabel("Age Group", fontsize=11)
    plt.xticks(rotation=25, ha="right")
    save_fig(fig, "04_age_group_heatmap")


# ─────────────────────────────────────────────────────────────────────────────
# CHART 5 — Line Chart: Monthly Trend
# ─────────────────────────────────────────────────────────────────────────────

def chart_monthly_trend(df):
    print("[CHART 5] Monthly Trend — Line Chart")
    data = monthly_trend(df, top_n=3)

    fig, ax = plt.subplots(figsize=(12, 5))
    markers = ["o", "s", "D"]
    for i, col in enumerate(data.columns):
        ax.plot(data.index, data[col], marker=markers[i], linewidth=2.5,
                color=PALETTE[i], label=col, markersize=7)
        # Annotate last point
        ax.annotate(f"{data[col].iloc[-1]:.0f}",
                    (data.index[-1], data[col].iloc[-1]),
                    textcoords="offset points", xytext=(8, 2),
                    fontsize=9, color=PALETTE[i], fontweight="bold")

    ax.set_xlabel("Month", fontsize=11)
    ax.set_ylabel("Response Count", fontsize=11)
    ax.set_title("Monthly Response Trend — Top 3 Platforms", fontsize=14, fontweight="bold", pad=15)
    ax.legend(loc="upper left", fontsize=10, framealpha=0.9)
    plt.xticks(rotation=20)
    save_fig(fig, "05_monthly_trend")


# ─────────────────────────────────────────────────────────────────────────────
# CHART 6 — Grouped Bar: Satisfaction by Platform
# ─────────────────────────────────────────────────────────────────────────────

def chart_satisfaction_by_platform(df):
    print("[CHART 6] Satisfaction Score by Platform")
    data = satisfaction_by_platform(df)

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(data))]
    bars = ax.bar(data["Platform"], data["Avg_Satisfaction_Score"],
                  color=colors, edgecolor="white", linewidth=0.8, width=0.55)

    for bar, val in zip(bars, data["Avg_Satisfaction_Score"]):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.03, f"{val:.2f}",
                ha="center", fontsize=11, fontweight="bold", color=TEXT_COLOR)

    ax.axhline(y=data["Avg_Satisfaction_Score"].mean(), color="#94A3B8",
               linestyle="--", linewidth=1.5, label=f"Avg: {data['Avg_Satisfaction_Score'].mean():.2f}")
    ax.set_ylim(0, 5.5)
    ax.set_ylabel("Avg. Satisfaction Score (1–5)", fontsize=11)
    ax.set_title("Q4 — Average Satisfaction Score by Platform", fontsize=14, fontweight="bold", pad=15)
    ax.legend(fontsize=9)
    plt.xticks(rotation=15)
    save_fig(fig, "06_satisfaction_by_platform")


# ─────────────────────────────────────────────────────────────────────────────
# CHART 7 — Horizontal Bar: Usage Hours Distribution
# ─────────────────────────────────────────────────────────────────────────────

def chart_usage_distribution(df):
    print("[CHART 7] Daily Usage Hours Distribution")
    data = usage_distribution(df)

    gradient_colors = ["#BFDBFE", "#60A5FA", "#3B82F6", "#1D4ED8"]
    fig, ax = plt.subplots(figsize=(9, 4))
    bars = ax.barh(data["Usage_Hours"], data["Percentage"],
                   color=gradient_colors, edgecolor="white", height=0.55)

    for bar, pct, cnt in zip(bars, data["Percentage"], data["Count"]):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                f"{pct:.1f}%  ({cnt:,})", va="center", fontsize=10)

    ax.set_xlim(0, data["Percentage"].max() + 12)
    ax.set_xlabel("Percentage (%)", fontsize=11)
    ax.set_title("Q2 — Daily Social Media Usage Hours", fontsize=14, fontweight="bold", pad=15)
    ax.invert_yaxis()
    save_fig(fig, "07_usage_distribution")


# ─────────────────────────────────────────────────────────────────────────────
# CHART 8 — Dashboard: 4-panel Summary
# ─────────────────────────────────────────────────────────────────────────────

def chart_dashboard(df):
    print("[CHART 8] 4-Panel Summary Dashboard")

    fig = plt.figure(figsize=(18, 12), facecolor="white")
    fig.suptitle("Poll Results Visualizer — Executive Dashboard",
                 fontsize=20, fontweight="bold", y=0.98, color=TEXT_COLOR)

    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

    # ── Panel A: Vote share bar ─────────────────
    ax1 = fig.add_subplot(gs[0, :2])
    data1 = overall_vote_share(df)
    colors = PALETTE[:len(data1)]
    bars = ax1.barh(data1["Option"], data1["Percentage"], color=colors, height=0.6, edgecolor="white")
    for bar, pct in zip(bars, data1["Percentage"]):
        ax1.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height() / 2,
                 f"{pct:.1f}%", va="center", fontsize=10)
    ax1.invert_yaxis()
    ax1.set_xlim(0, data1["Percentage"].max() + 10)
    ax1.set_title("Platform Preference (Q1)", fontsize=13, fontweight="bold")
    ax1.set_xlabel("Share (%)")
    ax1.set_facecolor(BACKGROUND)
    ax1.grid(color=GRID_COLOR, linestyle="--", alpha=0.7)

    # ── Panel B: Satisfaction donut ──────────────
    ax2 = fig.add_subplot(gs[0, 2])
    data2 = satisfaction_distribution(df)
    sat_colors = ["#22C55E", "#86EFAC", "#FCD34D", "#F87171", "#DC2626"]
    wedges, _, autos = ax2.pie(
        data2["Percentage"], autopct="%1.0f%%",
        colors=sat_colors[:len(data2)],
        startangle=90, pctdistance=0.82,
        wedgeprops=dict(width=0.5, edgecolor="white", linewidth=1.5)
    )
    for at in autos:
        at.set_fontsize(8)
        at.set_color("white")
        at.set_fontweight("bold")
    nss = net_satisfaction_score(df)
    ax2.text(0, 0, f"NSS\n{nss['net_satisfaction_score']:+.0f}",
             ha="center", va="center", fontsize=11, fontweight="bold", color=TEXT_COLOR)
    ax2.set_title("Satisfaction (Q4)", fontsize=13, fontweight="bold")

    # ── Panel C: Region stacked ──────────────────
    ax3 = fig.add_subplot(gs[1, :2])
    data3 = region_wise_breakdown(df)
    bottom = np.zeros(len(data3))
    for i, col in enumerate(data3.columns):
        ax3.bar(data3.index, data3[col], bottom=bottom,
                color=PALETTE[i % len(PALETTE)], label=col, edgecolor="white", linewidth=0.4)
        bottom += data3[col].values
    ax3.set_title("Platform Preference by Region (Q1)", fontsize=13, fontweight="bold")
    ax3.set_ylabel("Share (%)")
    ax3.legend(loc="upper right", fontsize=7, ncol=2, framealpha=0.9)
    ax3.set_ylim(0, 108)
    ax3.set_facecolor(BACKGROUND)
    ax3.grid(color=GRID_COLOR, linestyle="--", alpha=0.7)
    plt.setp(ax3.get_xticklabels(), rotation=15)

    # ── Panel D: Usage distribution ──────────────
    ax4 = fig.add_subplot(gs[1, 2])
    data4 = usage_distribution(df)
    ax4.barh(data4["Usage_Hours"], data4["Percentage"],
             color=["#BFDBFE", "#60A5FA", "#3B82F6", "#1D4ED8"],
             edgecolor="white", height=0.55)
    ax4.set_title("Daily Usage Hours (Q2)", fontsize=13, fontweight="bold")
    ax4.set_xlabel("Share (%)")
    ax4.invert_yaxis()
    ax4.set_facecolor(BACKGROUND)
    ax4.grid(color=GRID_COLOR, linestyle="--", alpha=0.7)

    fig.text(0.5, 0.01, "Survey: Social Media Preferences 2024 · N=1,200 · Poll Results Visualizer",
             ha="center", fontsize=8, color="#94A3B8")

    save_fig(fig, "08_executive_dashboard")


# ─────────────────────────────────────────────────────────────────────────────
# CHART 9 — Heatmap: Reason by Platform
# ─────────────────────────────────────────────────────────────────────────────

def chart_reason_heatmap(df):
    print("[CHART 9] Primary Reason × Platform Heatmap")
    from analysis import reason_by_platform
    data = reason_by_platform(df)

    fig, ax = plt.subplots(figsize=(12, 5))
    sns.heatmap(
        data, annot=True, fmt=".1f", cmap="YlOrRd",
        linewidths=0.5, linecolor="white",
        ax=ax, cbar_kws={"label": "% of Platform Users"}
    )
    ax.set_title("Q3 — Primary Reason for Use by Platform (%)", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Primary Reason", fontsize=11)
    ax.set_ylabel("Platform", fontsize=11)
    plt.xticks(rotation=20, ha="right")
    save_fig(fig, "09_reason_by_platform_heatmap")


# ─────────────────────────────────────────────────────────────────────────────
# RUN ALL CHARTS
# ─────────────────────────────────────────────────────────────────────────────

def generate_all_charts(df):
    print("\n" + "=" * 60)
    print("  GENERATING ALL CHARTS")
    print("=" * 60 + "\n")
    chart_vote_share_bar(df)
    chart_vote_share_donut(df)
    chart_region_stacked(df)
    chart_age_heatmap(df)
    chart_monthly_trend(df)
    chart_satisfaction_by_platform(df)
    chart_usage_distribution(df)
    chart_dashboard(df)
    chart_reason_heatmap(df)
    print(f"\n✅ All charts saved to: {CHARTS_DIR}")


if __name__ == "__main__":
    from preprocess import preprocess_pipeline
    df = pd.read_csv(CLEAN_PATH, parse_dates=["response_date"])
    generate_all_charts(df)