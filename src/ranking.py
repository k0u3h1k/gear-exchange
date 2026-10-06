import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any

def normalize_series(s: pd.Series) -> pd.Series:
    """Min-max normalizes a series to 0-100."""
    min_v = s.min()
    max_v = s.max()
    if max_v - min_v == 0:
        return pd.Series([50.0] * len(s), index=s.index)
    return ((s - min_v) / (max_v - min_v)) * 100.0

def generate_individual_rankings(profiles_df: pd.DataFrame) -> pd.DataFrame:
    """Generates 10 distinct, transparent, single-dimension rankings."""
    dimensions = [
        ("Most Semantically Convergent", "semantic_convergence", False),
        ("Most Lexically Diverse (MTLD)", "lexical_diversity_mtld", False),
        ("Most Informative (Richness)", "information_richness_score", False),
        ("Highest Unique Contribution", "unique_contribution_pct", False),
        ("Highest Information Density", "information_density_per_100w", False),
        ("Most Comprehensive Argumentation", "argument_completeness_score", False),
        ("Most Balanced & Qualified", "behavioral_balance_score", False),
        ("Most Concise", "mean_word_count", True), # True = lower is ranked higher
        ("Highest Evidence Support", "evidence_support_score", False),
        ("Highest Technical Vocabulary", "technical_vocab_ratio", False)
    ]
    
    records = []
    for dim_name, col, ascending in dimensions:
        sorted_df = profiles_df.sort_values(by=col, ascending=ascending).reset_index(drop=True)
        winner = sorted_df.iloc[0]["model_name"]
        second = sorted_df.iloc[1]["model_name"]
        third = sorted_df.iloc[2]["model_name"]
        val_winner = sorted_df.iloc[0][col]
        val_second = sorted_df.iloc[1][col]
        val_third = sorted_df.iloc[2][col]
        
        records.append({
            "ranking_dimension": dim_name,
            "metric_evaluated": col,
            "rank_1_winner": f"{winner} ({val_winner})",
            "rank_2": f"{second} ({val_second})",
            "rank_3": f"{third} ({val_third})",
            "winner_model": winner
        })
        
    return pd.DataFrame(records)

def compute_composite_scores(profiles_df: pd.DataFrame, weights: Dict[str, float]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Computes the overall Composite Evaluation Score with sensitivity analysis."""
    df = profiles_df.copy()
    
    # Normalization of core components to 0-100
    norm_richness = normalize_series(df["information_richness_score"])
    norm_unique = normalize_series(df["unique_contribution_pct"])
    norm_argument = normalize_series(df["argument_completeness_score"])
    norm_evidence = normalize_series(df["evidence_support_score"])
    norm_balance = normalize_series(df["behavioral_balance_score"])
    # Clarity / Efficiency: high lexical diversity + good readability (lower fog = clearer)
    norm_clarity = normalize_series(df["lexical_diversity_mtld"] - df["gunning_fog_readability"])
    norm_density = normalize_series(df["information_density_per_100w"])
    
    # Default weighting
    w_rich = weights.get("information_richness", 0.25)
    w_uniq = weights.get("unique_information_contribution", 0.15)
    w_arg = weights.get("argument_completeness", 0.15)
    w_ev = weights.get("evidence_support", 0.15)
    w_bal = weights.get("behavioral_balance", 0.10)
    w_clar = weights.get("vocabulary_clarity_efficiency", 0.10)
    w_dens = weights.get("information_density", 0.10)
    
    composite = (
        w_rich * norm_richness +
        w_uniq * norm_unique +
        w_arg * norm_argument +
        w_ev * norm_evidence +
        w_bal * norm_balance +
        w_clar * norm_clarity +
        w_dens * norm_density
    )
    
    score_df = pd.DataFrame({
        "model_name": df["model_name"],
        "norm_richness": round(norm_richness, 2),
        "norm_unique_contrib": round(norm_unique, 2),
        "norm_argument": round(norm_argument, 2),
        "norm_evidence": round(norm_evidence, 2),
        "norm_balance": round(norm_balance, 2),
        "norm_clarity": round(norm_clarity, 2),
        "norm_density": round(norm_density, 2),
        "composite_score": round(composite, 2)
    }).sort_values(by="composite_score", ascending=False).reset_index(drop=True)
    score_df["rank"] = score_df.index + 1
    
    # Sensitivity Analysis across alternative weighting profiles
    scenarios = [
        ("Default Configured", weights),
        ("Equal Weights", {k: 1.0/7.0 for k in weights}),
        ("Evidence & Argument Heavy", {
            "information_richness": 0.15, "unique_information_contribution": 0.10,
            "argument_completeness": 0.25, "evidence_support": 0.25,
            "behavioral_balance": 0.10, "vocabulary_clarity_efficiency": 0.05,
            "information_density": 0.10
        }),
        ("Information & Density Heavy", {
            "information_richness": 0.35, "unique_information_contribution": 0.20,
            "argument_completeness": 0.10, "evidence_support": 0.10,
            "behavioral_balance": 0.05, "vocabulary_clarity_efficiency": 0.05,
            "information_density": 0.15
        }),
        ("Balanced & Nuance Heavy", {
            "information_richness": 0.15, "unique_information_contribution": 0.10,
            "argument_completeness": 0.20, "evidence_support": 0.10,
            "behavioral_balance": 0.30, "vocabulary_clarity_efficiency": 0.10,
            "information_density": 0.05
        })
    ]
    
    sensitivity_records = []
    for s_name, w_dict in scenarios:
        s_comp = (
            w_dict.get("information_richness", 0) * norm_richness +
            w_dict.get("unique_information_contribution", 0) * norm_unique +
            w_dict.get("argument_completeness", 0) * norm_argument +
            w_dict.get("evidence_support", 0) * norm_evidence +
            w_dict.get("behavioral_balance", 0) * norm_balance +
            w_dict.get("vocabulary_clarity_efficiency", 0) * norm_clarity +
            w_dict.get("information_density", 0) * norm_density
        )
        s_res = pd.DataFrame({"model": df["model_name"], "score": s_comp}).sort_values(by="score", ascending=False)
        w_model = s_res.iloc[0]["model"]
        sensitivity_records.append({
            "weighting_scenario": s_name,
            "winner_model": w_model,
            "top_score": round(s_res.iloc[0]["score"], 2),
            "second_model": s_res.iloc[1]["model"],
            "second_score": round(s_res.iloc[1]["score"], 2),
            "spread_points": round(s_res.iloc[0]["score"] - s_res.iloc[1]["score"], 2)
        })
        
    sensitivity_df = pd.DataFrame(sensitivity_records)
    return score_df, sensitivity_df
