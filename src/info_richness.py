import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

def compute_information_richness(
    parsed_df: pd.DataFrame, 
    claims_df: pd.DataFrame, 
    clusters_df: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Computes information richness metrics per response and per model."""
    records = []
    
    for _, row in parsed_df.iterrows():
        p_id = row["prompt_id"]
        model = row["model_name"]
        words = max(1, row["word_count"])
        
        # Claims for this response
        r_claims = claims_df[(claims_df["prompt_id"] == p_id) & (claims_df["model"] == model)]
        total_claims = len(r_claims)
        
        # Categorical counts
        type_counts = r_claims["claim_type"].value_counts().to_dict()
        factual_cnt = type_counts.get("FACTUAL", 0)
        causal_cnt = type_counts.get("CAUSAL", 0)
        normative_cnt = type_counts.get("NORMATIVE", 0)
        recomm_cnt = type_counts.get("RECOMMENDATION", 0)
        definitional_cnt = type_counts.get("DEFINITIONAL", 0)
        legal_cnt = type_counts.get("LEGAL/DOCTRINAL", 0)
        opinion_cnt = type_counts.get("OPINION", 0)
        predictive_cnt = type_counts.get("PREDICTIVE", 0)
        
        # Unique claims from clusters
        sub_c = clusters_df[clusters_df["prompt_id"] == p_id]
        uniq_class = f"UNIQUE_TO_{model.upper()}"
        unique_cnt = len(sub_c[sub_c["classification"] == uniq_class])
        
        # Information density per 100 words
        density = (total_claims / words) * 100.0
        
        # Raw richness index (weighted informational diversity)
        raw_richness = (
            1.0 * total_claims + 
            1.5 * unique_cnt + 
            1.2 * factual_cnt + 
            1.0 * causal_cnt + 
            1.2 * legal_cnt + 
            0.8 * recomm_cnt
        )
        
        records.append({
            "prompt_id": p_id,
            "model_name": model,
            "word_count": words,
            "total_claims": total_claims,
            "unique_claims": unique_cnt,
            "factual_claims": factual_cnt,
            "causal_claims": causal_cnt,
            "legal_claims": legal_cnt,
            "recommendation_claims": recomm_cnt,
            "definitional_claims": definitional_cnt,
            "normative_claims": normative_cnt,
            "opinion_claims": opinion_cnt,
            "predictive_claims": predictive_cnt,
            "information_density_per_100w": round(density, 2),
            "raw_richness_score": round(raw_richness, 2)
        })
        
    richness_df = pd.DataFrame(records)
    
    # Normalize richness score 0-100 across the dataset
    min_r = richness_df["raw_richness_score"].min()
    max_r = richness_df["raw_richness_score"].max()
    richness_df["information_richness_score"] = round(
        ((richness_df["raw_richness_score"] - min_r) / max(1e-5, (max_r - min_r))) * 100, 2
    )
    
    # Model-level aggregated summary
    model_summary = richness_df.groupby("model_name")[[
        "word_count", "total_claims", "unique_claims", "factual_claims", 
        "causal_claims", "legal_claims", "recommendation_claims",
        "information_density_per_100w", "information_richness_score"
    ]].mean().reset_index().round(2)
    
    return richness_df, model_summary
