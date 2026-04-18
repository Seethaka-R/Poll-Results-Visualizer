"""
dashboard.py
------------
Streamlit interactive dashboard for Poll Results Visualizer.

To run:
    streamlit run dashboard.py

Features:
- Sidebar filters (Region, Age Group, Gender)
- KPI cards (Total respondents, Leading platform, NSS)
- Interactive Plotly charts
- Downloadable filtered data
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from analysis import (
    overall_vote_share, region_wise_breakdown, age_group_breakdown,
    satisfaction_by_platform, usage_distribution, net_satisfaction_score,
    monthly_trend, reason_distribution
)

# ── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Poll Results Visualizer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #F8FAFC; }
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border-left: 4px solid #2563EB;
    }
    .metric-label { font-size: 0.8rem; color: #64748B; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
    .metric-value { font-size: 2rem; font-weight: 700; color: #1E293B; margin-top: 0.2rem; }
    .metric-delta { font-size: 0.85rem; color: #22C55E; margin-top: 0.2rem; }
    .section-title { font-size: 1.1rem; font-weight: 600; color: #1E293B; margin-bottom: 0.5rem; }
    div[data-testid="stMetricValue"] { font-size: 2rem; }
</style>
""", unsafe_allow_html=True)

CLEAN_PATH = os.path.join(os.path.dirname(__file__), "data", "poll_data_clean.csv")
PALETTE = ["#2563EB", "#7C3AED", "#DB2777", "#D97706", "#059669", "#DC2626"]
CHART_TEXT = "#0F172A"
CHART_GRID = "#CBD5E1"


@st.cache_data
def load_data():
    return pd.read_csv(CLEAN_PATH, parse_dates=["response_date"])


df_full = load_data()

# ── SIDEBAR FILTERS ─────────────────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/color/96/combo-chart--v1.png", width=60)
st.sidebar.title("🔍 Filters")
st.sidebar.markdown("---")

regions = ["All"] + sorted(df_full["region"].unique().tolist())
age_groups = ["All"] + sorted(df_full["age_group"].unique().tolist())
genders = ["All"] + sorted(df_full["gender"].unique().tolist())

sel_region = st.sidebar.selectbox("Region", regions)
sel_age = st.sidebar.selectbox("Age Group", age_groups)
sel_gender = st.sidebar.selectbox("Gender", genders)

st.sidebar.markdown("---")
st.sidebar.markdown("**Survey:** Social Media Preferences 2024")
st.sidebar.markdown("**Data:** Synthetic · N=1,200")
st.sidebar.markdown("**Built with:** Python · Streamlit · Plotly")

# ── Apply Filters ─────────────────────────────────────────────────────────
df = df_full.copy()
if sel_region != "All":
    df = df[df["region"] == sel_region]
if sel_age != "All":
    df = df[df["age_group"] == sel_age]
if sel_gender != "All":
    df = df[df["gender"] == sel_gender]

# ── HEADER ────────────────────────────────────────────────────────────────
st.title("📊 Poll Results Visualizer")
st.markdown("**Social Media Preference Survey 2024** · Interactive Analysis Dashboard")
st.markdown("---")

# ── KPI CARDS ─────────────────────────────────────────────────────────────
vote_share = overall_vote_share(df)
top_platform = vote_share.iloc[0]["Option"]
top_pct = vote_share.iloc[0]["Percentage"]
nss_data = net_satisfaction_score(df)
nss = nss_data["net_satisfaction_score"]

col1, col2, col3, col4 = st.columns(4)
col1.metric("👥 Total Respondents", f"{len(df):,}", f"{len(df)/len(df_full)*100:.0f}% of all")
col2.metric("🏆 Leading Platform", top_platform, f"{top_pct:.1f}% share")
col3.metric("😊 Net Satisfaction Score", f"{nss:+.1f}", "Positive > 0")
col4.metric("📅 Survey Period", "Jan–Jun 2024", "6 months")

st.markdown("---")

# ── ROW 1: Vote Share + Donut ─────────────────────────────────────────────
col_a, col_b = st.columns([3, 2])

with col_a:
    st.markdown("##### Q1 — Platform Preference (Vote Share)")
    fig1 = px.bar(
        vote_share, x="Percentage", y="Option", orientation="h",
        color="Option", color_discrete_sequence=PALETTE,
        text=vote_share["Percentage"].apply(lambda x: f"{x:.1f}%"),
        labels={"Percentage": "Share (%)", "Option": ""},
    )
    fig1.update_traces(textposition="outside", marker_line_color="white", marker_line_width=1)
    fig1.update_layout(
        showlegend=False,
        height=320,
        paper_bgcolor="white",
        plot_bgcolor="#F8FAFC",
        font=dict(color=CHART_TEXT),
        margin=dict(l=90, r=80, t=10, b=30),
    )
    fig1.update_yaxes(autorange="reversed", automargin=True, tickfont=dict(size=11, color=CHART_TEXT))
    fig1.update_xaxes(automargin=True, tickfont=dict(color=CHART_TEXT), title_font=dict(color=CHART_TEXT))
    st.plotly_chart(fig1, use_container_width=True)

with col_b:
    st.markdown("##### Q4 — Satisfaction Distribution")
    sat_data = df["Q4_satisfaction"].value_counts().reset_index()
    sat_data.columns = ["Satisfaction", "Count"]
    order = ["Very Satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very Dissatisfied"]
    sat_colors = ["#22C55E", "#86EFAC", "#FCD34D", "#F87171", "#DC2626"]
    sat_data["Satisfaction"] = pd.Categorical(sat_data["Satisfaction"], categories=order, ordered=True)
    sat_data = sat_data.sort_values("Satisfaction")

    fig2 = go.Figure(go.Pie(
        labels=sat_data["Satisfaction"], values=sat_data["Count"],
        hole=0.55, marker_colors=sat_colors[:len(sat_data)],
        textinfo="percent", textfont_size=11,
        hovertemplate="%{label}: %{value} (%{percent})<extra></extra>"
    ))
    fig2.add_annotation(text=f"NSS<br><b>{nss:+.0f}</b>",
                        x=0.5, y=0.5, font_size=16, showarrow=False)
    fig2.update_layout(
        showlegend=True,
        height=320,
        paper_bgcolor="white",
        font=dict(color=CHART_TEXT),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.08,
            xanchor="center",
            x=0.5,
            font=dict(size=10, color=CHART_TEXT),
        ),
        margin=dict(l=10, r=10, t=10, b=60),
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── ROW 2: Region Stacked + Monthly Trend ────────────────────────────────
col_c, col_d = st.columns(2)

with col_c:
    st.markdown("##### Region-wise Platform Preference")
    region_data = region_wise_breakdown(df).reset_index()
    region_melted = region_data.melt(id_vars="region", var_name="Platform", value_name="Percentage")

    fig3 = px.bar(
        region_melted, x="region", y="Percentage", color="Platform",
        color_discrete_sequence=PALETTE, barmode="stack",
        labels={"region": "Region", "Percentage": "Share (%)"},
        text=region_melted["Percentage"].apply(lambda x: f"{x:.0f}%" if x > 6 else "")
    )
    fig3.update_traces(textposition="inside", textfont_size=9)
    fig3.update_layout(
        height=330,
        paper_bgcolor="white",
        plot_bgcolor="#F8FAFC",
        font=dict(color=CHART_TEXT),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.18,
            xanchor="center",
            x=0.5,
            font=dict(size=10, color=CHART_TEXT),
        ),
        margin=dict(l=60, r=10, t=10, b=80),
    )
    fig3.update_xaxes(automargin=True, tickangle=-15, tickfont=dict(color=CHART_TEXT), title_font=dict(color=CHART_TEXT))
    fig3.update_yaxes(automargin=True, tickfont=dict(color=CHART_TEXT), title_font=dict(color=CHART_TEXT), gridcolor=CHART_GRID)
    st.plotly_chart(fig3, use_container_width=True)

with col_d:
    st.markdown("##### Monthly Response Trend (Top 3 Platforms)")
    trend_data = monthly_trend(df, top_n=3).reset_index()
    trend_melted = trend_data.melt(id_vars="response_month", var_name="Platform", value_name="Count")

    fig4 = px.line(
        trend_melted, x="response_month", y="Count", color="Platform",
        color_discrete_sequence=PALETTE, markers=True,
        labels={"response_month": "Month", "Count": "Responses"},
    )
    fig4.update_traces(line_width=2.5, marker_size=7)
    fig4.update_layout(
        height=330,
        paper_bgcolor="white",
        plot_bgcolor="#F8FAFC",
        font=dict(color=CHART_TEXT),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.18,
            xanchor="center",
            x=0.5,
            font=dict(size=10, color=CHART_TEXT),
        ),
        margin=dict(l=60, r=10, t=10, b=80),
    )
    fig4.update_xaxes(automargin=True, tickangle=-20, tickfont=dict(color=CHART_TEXT), title_font=dict(color=CHART_TEXT))
    fig4.update_yaxes(automargin=True, tickfont=dict(color=CHART_TEXT), title_font=dict(color=CHART_TEXT), gridcolor=CHART_GRID)
    st.plotly_chart(fig4, use_container_width=True)

# ── ROW 3: Satisfaction per platform + Usage ──────────────────────────────
col_e, col_f = st.columns(2)

with col_e:
    st.markdown("##### Average Satisfaction Score per Platform")
    sat_plat = satisfaction_by_platform(df)
    fig5 = px.bar(
        sat_plat, x="Platform", y="Avg_Satisfaction_Score",
        color="Avg_Satisfaction_Score", color_continuous_scale="Blues",
        text=sat_plat["Avg_Satisfaction_Score"].apply(lambda x: f"{x:.2f}"),
        labels={"Avg_Satisfaction_Score": "Score (1–5)"},
        range_y=[0, 5.5]
    )
    fig5.update_traces(textposition="outside")
    fig5.update_layout(
        height=320,
        paper_bgcolor="white",
        plot_bgcolor="#F8FAFC",
        font=dict(color=CHART_TEXT),
        showlegend=False,
        margin=dict(l=60, r=10, t=10, b=80),
    )
    fig5.update_xaxes(automargin=True, tickangle=-20, tickfont=dict(color=CHART_TEXT), title_font=dict(color=CHART_TEXT))
    fig5.update_yaxes(automargin=True, tickfont=dict(color=CHART_TEXT), title_font=dict(color=CHART_TEXT), gridcolor=CHART_GRID)
    st.plotly_chart(fig5, use_container_width=True)

with col_f:
    st.markdown("##### Daily Usage Hours Distribution")
    usage_data = usage_distribution(df)
    fig6 = px.bar(
        usage_data, x="Percentage", y="Usage_Hours", orientation="h",
        color="Usage_Hours", color_discrete_sequence=["#BFDBFE", "#60A5FA", "#3B82F6", "#1D4ED8"],
        text=usage_data["Percentage"].apply(lambda x: f"{x:.1f}%"),
        labels={"Percentage": "Share (%)", "Usage_Hours": ""},
    )
    fig6.update_traces(textposition="outside")
    fig6.update_layout(
        showlegend=False,
        height=320,
        paper_bgcolor="white",
        plot_bgcolor="#F8FAFC",
        font=dict(color=CHART_TEXT),
        margin=dict(l=110, r=80, t=10, b=30),
    )
    fig6.update_yaxes(autorange="reversed", automargin=True, tickfont=dict(size=11, color=CHART_TEXT))
    fig6.update_xaxes(automargin=True, tickfont=dict(color=CHART_TEXT), title_font=dict(color=CHART_TEXT))
    st.plotly_chart(fig6, use_container_width=True)

# ── DATA TABLE ────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("##### 🗂 Filtered Raw Data Preview")
col_show, col_dl = st.columns([4, 1])
with col_show:
    st.dataframe(df.head(50), use_container_width=True)
with col_dl:
    st.markdown("<br><br>", unsafe_allow_html=True)
    csv = df.to_csv(index=False)
    st.download_button("⬇️ Download Filtered Data", csv, "filtered_poll_data.csv", "text/csv")

st.markdown("---")
st.caption("Poll Results Visualizer · Built for Data Analysis Portfolio · Python + Streamlit + Plotly")
