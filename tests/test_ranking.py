import pytest
import pandas as pd
import numpy as np
from src.ranking import normalize_series, compute_composite_scores

def test_normalize_series():
    s = pd.Series([10.0, 20.0, 30.0])
    norm = normalize_series(s)
    assert norm.iloc[0] == 0.0
    assert norm.iloc[1] == 50.0
    assert norm.iloc[2] == 100.0

def test_composite_score_bounds():
    mock_profiles = pd.DataFrame([
        {
            "model_name": "ChatGPT", "information_richness_score": 60.0,
            "unique_contribution_pct": 25.0, "argument_completeness_score": 75.0,
            "evidence_support_score": 50.0, "behavioral_balance_score": 80.0,
            "lexical_diversity_mtld": 70.0, "gunning_fog_readability": 12.0,
            "information_density_per_100w": 7.0
        },
        {
            "model_name": "Claude", "information_richness_score": 55.0,
            "unique_contribution_pct": 20.0, "argument_completeness_score": 85.0,
            "evidence_support_score": 60.0, "behavioral_balance_score": 85.0,
            "lexical_diversity_mtld": 75.0, "gunning_fog_readability": 13.0,
            "information_density_per_100w": 6.8
        },
        {
            "model_name": "Gemini", "information_richness_score": 70.0,
            "unique_contribution_pct": 30.0, "argument_completeness_score": 70.0,
            "evidence_support_score": 65.0, "behavioral_balance_score": 75.0,
            "lexical_diversity_mtld": 80.0, "gunning_fog_readability": 12.5,
            "information_density_per_100w": 7.5
        }
    ])
    
    weights = {
        "information_richness": 0.25, "unique_information_contribution": 0.15,
        "argument_completeness": 0.15, "evidence_support": 0.15,
        "behavioral_balance": 0.10, "vocabulary_clarity_efficiency": 0.10,
        "information_density": 0.10
    }
    
    score_df, sens_df = compute_composite_scores(mock_profiles, weights)
    assert len(score_df) == 3
    assert not score_df["composite_score"].isna().any()
    assert (score_df["composite_score"] >= 0.0).all()
    assert (score_df["composite_score"] <= 100.0).all()
    assert len(sens_df) == 5
