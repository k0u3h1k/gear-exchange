import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any

def compute_information_overlap_metrics(
    claims_df: pd.DataFrame, 
    clusters_df: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Computes rigorous information overlap and unique contribution scores."""
    prompt_records = []
    prompts = sorted(claims_df["prompt_id"].unique())
    models = ["ChatGPT", "Claude", "Gemini"]
    
    for p_id in prompts:
        sub_c = clusters_df[clusters_df["prompt_id"] == p_id]
        total_distinct = len(sub_c)
        if total_distinct == 0:
            continue
            
        shared_3 = len(sub_c[sub_c["classification"] == "SHARED_BY_ALL_3"])
        shared_2 = len(sub_c[sub_c["classification"].isin(["SHARED_BY_2", "SEMANTICALLY_SIMILAR"])])
        matched_total = shared_3 + shared_2
        
        uniq_chat = len(sub_c[sub_c["classification"] == "UNIQUE_TO_CHATGPT"])
        uniq_cl = len(sub_c[sub_c["classification"] == "UNIQUE_TO_CLAUDE"])
        uniq_gm = len(sub_c[sub_c["classification"] == "UNIQUE_TO_GEMINI"])
        contradictions = len(sub_c[sub_c["classification"] == "CONTRADICTORY"])
        
        info_overlap_pct = (matched_total / total_distinct) * 100
        
        prompt_records.append({
            "prompt_id": p_id,
            "total_distinct_claims": total_distinct,
            "matched_claims": matched_total,
            "shared_by_all_3": shared_3,
            "shared_by_2": shared_2,
            "unique_chatgpt": uniq_chat,
            "unique_claude": uniq_cl,
            "unique_gemini": uniq_gm,
            "contradictions": contradictions,
            "information_overlap_pct": round(info_overlap_pct, 2),
            "unique_chatgpt_pct": round((uniq_chat / total_distinct) * 100, 2),
            "unique_claude_pct": round((uniq_cl / total_distinct) * 100, 2),
            "unique_gemini_pct": round((uniq_gm / total_distinct) * 100, 2),
            "contradiction_pct": round((contradictions / total_distinct) * 100, 2)
        })
        
    prompt_df = pd.DataFrame(prompt_records)
    
    # Model-level aggregated summary
    tot_claims_distinct = prompt_df["total_distinct_claims"].sum()
    summary_data = []
    for m in models:
        col_uniq = f"unique_{m.lower()}"
        m_uniq = prompt_df[col_uniq].sum()
        m_claims_tot = len(claims_df[claims_df["model"] == m])
        summary_data.append({
            "model": m,
            "total_extracted_claims": m_claims_tot,
            "total_unique_claims": m_uniq,
            "mean_unique_contribution_pct": round(prompt_df[f"unique_{m.lower()}_pct"].mean(), 2),
            "cumulative_unique_contribution_pct": round((m_uniq / max(1, tot_claims_distinct)) * 100, 2)
        })
        
    model_summary_df = pd.DataFrame(summary_data)
    return prompt_df, model_summary_df
