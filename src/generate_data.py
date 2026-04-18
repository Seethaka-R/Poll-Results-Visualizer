"""
generate_data.py
----------------
Generates a realistic synthetic poll dataset for the Poll Results Visualizer project.
Simulates a "Preferred Social Media Platform" survey with demographic breakdowns.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────
SEED = 42
np.random.seed(SEED)
random.seed(SEED)

N_RESPONDENTS = 1200  # Total survey respondents

QUESTIONS = {
    "Q1": {
        "text": "Which social media platform do you use most?",
        "options": ["Instagram", "YouTube", "Twitter/X", "LinkedIn", "Facebook", "Snapchat"],
        "weights": [0.28, 0.25, 0.18, 0.12, 0.10, 0.07],  # overall distribution
    },
    "Q2": {
        "text": "How many hours per day do you spend on social media?",
        "options": ["Less than 1 hr", "1-2 hrs", "2-4 hrs", "More than 4 hrs"],
        "weights": [0.15, 0.35, 0.30, 0.20],
    },
    "Q3": {
        "text": "What is your primary reason for using social media?",
        "options": ["Entertainment", "Networking", "News & Updates", "Business/Marketing", "Staying in touch"],
        "weights": [0.30, 0.22, 0.20, 0.15, 0.13],
    },
    "Q4": {
        "text": "How satisfied are you with your primary social media platform?",
        "options": ["Very Satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very Dissatisfied"],
        "weights": [0.22, 0.38, 0.25, 0.10, 0.05],
    },
}

REGIONS = ["North India", "South India", "East India", "West India", "Central India"]
AGE_GROUPS = ["13-17", "18-24", "25-34", "35-44", "45-54", "55+"]
GENDERS = ["Male", "Female", "Non-binary / Prefer not to say"]
EDUCATION = ["High School", "Undergraduate", "Postgraduate", "PhD", "Other"]
OCCUPATIONS = ["Student", "Working Professional", "Freelancer", "Business Owner", "Other"]

# Regional bias for platform preference (makes data more realistic)
REGIONAL_WEIGHTS = {
    "North India":   [0.26, 0.22, 0.20, 0.14, 0.10, 0.08],
    "South India":   [0.24, 0.30, 0.18, 0.16, 0.08, 0.04],
    "East India":    [0.30, 0.20, 0.16, 0.10, 0.14, 0.10],
    "West India":    [0.28, 0.26, 0.16, 0.12, 0.10, 0.08],
    "Central India": [0.32, 0.24, 0.14, 0.08, 0.14, 0.08],
}

# Age-group bias for platform preference
AGE_WEIGHTS = {
    "13-17":  [0.40, 0.28, 0.18, 0.02, 0.04, 0.08],
    "18-24":  [0.32, 0.26, 0.22, 0.10, 0.04, 0.06],
    "25-34":  [0.26, 0.24, 0.20, 0.18, 0.08, 0.04],
    "35-44":  [0.18, 0.22, 0.18, 0.20, 0.18, 0.04],
    "45-54":  [0.12, 0.20, 0.14, 0.14, 0.36, 0.04],
    "55+":    [0.08, 0.18, 0.10, 0.10, 0.52, 0.02],
}


def generate_date(start="2024-01-01", end="2024-06-30"):
    """Generate a random date between start and end."""
    start_dt = datetime.strptime(start, "%Y-%m-%d")
    end_dt = datetime.strptime(end, "%Y-%m-%d")
    delta = (end_dt - start_dt).days
    return (start_dt + timedelta(days=random.randint(0, delta))).strftime("%Y-%m-%d")


def generate_respondent(resp_id):
    """Generate one synthetic respondent's full survey response."""
    region = np.random.choice(REGIONS)
    age_group = np.random.choice(AGE_GROUPS, p=[0.08, 0.28, 0.30, 0.18, 0.10, 0.06])
    gender = np.random.choice(GENDERS, p=[0.48, 0.48, 0.04])
    education = np.random.choice(EDUCATION, p=[0.15, 0.40, 0.30, 0.08, 0.07])
    occupation = np.random.choice(OCCUPATIONS, p=[0.30, 0.40, 0.12, 0.10, 0.08])

    # Blend regional + age weights for Q1 (platform choice)
    rw = np.array(REGIONAL_WEIGHTS[region])
    aw = np.array(AGE_WEIGHTS[age_group])
    blended = (rw + aw) / 2
    blended = blended / blended.sum()  # Normalize

    q1_options = QUESTIONS["Q1"]["options"]
    q1_answer = np.random.choice(q1_options, p=blended)

    # Other questions use default weights
    q2_answer = np.random.choice(QUESTIONS["Q2"]["options"], p=QUESTIONS["Q2"]["weights"])
    q3_answer = np.random.choice(QUESTIONS["Q3"]["options"], p=QUESTIONS["Q3"]["weights"])
    q4_answer = np.random.choice(QUESTIONS["Q4"]["options"], p=QUESTIONS["Q4"]["weights"])

    # Introduce ~3% missing values for realism
    def maybe_null(val, prob=0.03):
        return np.nan if random.random() < prob else val

    return {
        "respondent_id": f"R{resp_id:04d}",
        "response_date": generate_date(),
        "region": region,
        "age_group": age_group,
        "gender": gender,
        "education": education,
        "occupation": occupation,
        "Q1_preferred_platform": maybe_null(q1_answer),
        "Q2_daily_usage_hours": maybe_null(q2_answer),
        "Q3_primary_reason": maybe_null(q3_answer),
        "Q4_satisfaction": maybe_null(q4_answer),
    }


def generate_dataset(n=N_RESPONDENTS):
    """Generate full poll dataset."""
    print(f"[INFO] Generating {n} synthetic respondents...")
    records = [generate_respondent(i + 1) for i in range(n)]
    df = pd.DataFrame(records)
    return df


if __name__ == "__main__":
    df = generate_dataset()
    out_path = os.path.join(os.path.dirname(__file__), "..", "data", "poll_data_raw.csv")
    df.to_csv(out_path, index=False)
    print(f"[SUCCESS] Dataset saved → {out_path}")
    print(f"[INFO] Shape: {df.shape}")
    print(df.head())