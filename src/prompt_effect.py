import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any

def compute_prompt_vs_model_effect(
    parsed_df: pd.DataFrame,
    vocab_df: pd.DataFrame,
    richness_df: pd.DataFrame,
    framing_df: pd.DataFrame
) -> pd.DataFrame:
    """Analyzes whether variation is driven more by the prompt or by the model."""
    m1 = pd.merge(parsed_df[["prompt_id", "model_name", "word_count"]], vocab_df[["prompt_id", "model_name", "mtld", "gunning_fog_index"]], on=["prompt_id", "model_name"])
    m2 = pd.merge(m1, richness_df[["prompt_id", "model_name", "total_claims", "information_richness_score"]], on=["prompt_id", "model_name"])
    data = pd.merge(m2, framing_df[["prompt_id", "model_name", "risk_framing_density", "benefit_framing_density"]], on=["prompt_id", "model_name"])
    
    metrics = [
        ("Word Count", "word_count"),
        ("Lexical Diversity (MTLD)", "mtld"),
        ("Readability (Gunning Fog)", "gunning_fog_index"),
        ("Total Claims Extracted", "total_claims"),
        ("Information Richness Score", "information_richness_score"),
        ("Risk Framing Density", "risk_framing_density"),
        ("Benefit Framing Density", "benefit_framing_density")
    ]
    
    records = []
    
    for name, col in metrics:
        vals = data[col].values
        overall_mean = np.mean(vals)
        overall_var = np.var(vals, ddof=1) if len(vals) > 1 else 1e-5
        
        # Between-Prompt Variation (Prompt Effect)
        prompt_means = data.groupby("prompt_id")[col].mean()
        var_between_prompts = np.var(prompt_means, ddof=1)
        
        # Between-Model Variation (Model Effect)
        model_means = data.groupby("model_name")[col].mean()
        var_between_models = np.var(model_means, ddof=1)
        
        # Ratio of prompt variance to model variance
        ratio = var_between_prompts / max(1e-5, var_between_models)
        
        driver = "PROMPT DOMINANT" if ratio > 1.5 else ("MODEL DOMINANT" if ratio < 0.67 else "BALANCED INFLUENCE")
        
        records.append({
            "metric": name,
            "overall_mean": round(overall_mean, 2),
            "between_prompt_variance": round(var_between_prompts, 2),
            "between_model_variance": round(var_between_models, 2),
            "prompt_to_model_var_ratio": round(ratio, 2),
            "dominant_variation_driver": driver
        })
        
    return pd.DataFrame(records)
