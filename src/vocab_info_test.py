import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Any

def run_vocabulary_vs_information_analysis(
    vocab_df: pd.DataFrame, 
    richness_df: pd.DataFrame
) -> pd.DataFrame:
    """Calculates Pearson and Spearman correlations between vocabulary complexity and information metrics."""
    merged = pd.merge(vocab_df, richness_df, on=["prompt_id", "model_name"])
    
    comparisons = [
        ("MTLD (Lexical Diversity)", "mtld", "Total Atomic Claims", "total_claims"),
        ("MTLD (Lexical Diversity)", "mtld", "Unique Claims", "unique_claims"),
        ("MTLD (Lexical Diversity)", "mtld", "Information Density (per 100w)", "information_density_per_100w"),
        ("Root TTR (RTTR)", "rttr", "Total Atomic Claims", "total_claims"),
        ("Root TTR (RTTR)", "rttr", "Unique Claims", "unique_claims"),
        ("Technical Vocab Ratio", "technical_vocab_ratio", "Unique Claims", "unique_claims"),
        ("Gunning Fog (Readability Complexity)", "gunning_fog_index", "Information Richness Score", "information_richness_score"),
        ("Word Count", "word_count_x", "Information Richness Score", "information_richness_score"),
        ("Word Count", "word_count_x", "Total Atomic Claims", "total_claims")
    ]
    
    records = []
    n = len(merged)
    
    for label_x, col_x, label_y, col_y in comparisons:
        x = merged[col_x].values
        y = merged[col_y].values
        
        # Pearson
        r_val, p_pearson = stats.pearsonr(x, y)
        # Spearman
        rho_val, p_spearman = stats.spearmanr(x, y)
        
        # Interpretation
        if abs(r_val) >= 0.7:
            strength = "Strong"
        elif abs(r_val) >= 0.4:
            strength = "Moderate"
        elif abs(r_val) >= 0.2:
            strength = "Weak"
        else:
            strength = "Negligible"
            
        direction = "Positive" if r_val > 0 else "Negative"
        
        records.append({
            "complexity_metric": label_x,
            "information_metric": label_y,
            "sample_size_n": n,
            "pearson_r": round(r_val, 4),
            "pearson_p_value": round(p_pearson, 4),
            "spearman_rho": round(rho_val, 4),
            "spearman_p_value": round(p_spearman, 4),
            "correlation_strength": f"{strength} {direction}",
            "statistically_significant_05": p_pearson < 0.05
        })
        
    return pd.DataFrame(records)
