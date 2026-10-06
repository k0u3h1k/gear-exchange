import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any

def generate_model_profiles(
    parsed_df: pd.DataFrame,
    vocab_summary: pd.DataFrame,
    semantic_summary: pd.DataFrame,
    richness_summary: pd.DataFrame,
    overlap_summary: pd.DataFrame,
    argument_summary: pd.DataFrame,
    stance_summary: pd.DataFrame,
    framing_summary: pd.DataFrame,
    evidence_summary: pd.DataFrame
) -> pd.DataFrame:
    """Consolidates all metrics into multi-dimensional behavioral profiles for each model."""
    models = ["ChatGPT", "Claude", "Gemini"]
    profile_records = []
    
    for m in models:
        v_row = vocab_summary[vocab_summary["model_name"] == m].iloc[0]
        r_row = richness_summary[richness_summary["model_name"] == m].iloc[0]
        o_row = overlap_summary[overlap_summary["model"] == m].iloc[0]
        a_row = argument_summary[argument_summary["model_name"] == m].iloc[0]
        s_row = stance_summary[stance_summary["model_name"] == m].iloc[0]
        f_row = framing_summary[framing_summary["model_name"] == m].iloc[0]
        e_row = evidence_summary[evidence_summary["model_name"] == m].iloc[0]
        
        # Semantic convergence: average similarity with other 2 models
        sem_pairs = semantic_summary[(semantic_summary["model_a"] == m) | (semantic_summary["model_b"] == m)]
        mean_sem_conv = float(sem_pairs["semantic_composite"].mean()) if not sem_pairs.empty else 0.0
        
        # Formulate qualitative interpretation based on empirical data
        if m == "ChatGPT":
            qual_summary = (
                "Highly didactic and structured. Relies on enumerated principles, simulation of academic citations "
                "([DOI], [PubMed]), and high premise-testing questions. High conciseness control."
            )
        elif m == "Claude":
            qual_summary = (
                "Nuanced, meta-evaluative, and dialectical. Explicitly acknowledges its own positionality as an AI, "
                "incorporates academic authors (Robert Sparrow) and statutory frameworks (IHL, GDPR), with balanced hedging."
            )
        else: # Gemini
            qual_summary = (
                "Empirically aggressive with high domain terminology ('bossware', 'panopticon effect', 'solipsism'). "
                "Frequently utilizes comparative tables and quantitative workforce survey statistics."
            )
            
        profile_records.append({
            "model_name": m,
            "mean_word_count": round(v_row["word_count"], 1),
            "lexical_diversity_mtld": round(v_row["mtld"], 2),
            "root_ttr": round(v_row["rttr"], 2),
            "semantic_convergence": round(mean_sem_conv, 3),
            "information_richness_score": round(r_row["information_richness_score"], 2),
            "unique_contribution_pct": round(o_row["mean_unique_contribution_pct"], 2),
            "information_density_per_100w": round(r_row["information_density_per_100w"], 2),
            "argument_completeness_score": round(a_row["argument_completeness_score"], 2),
            "qualification_rate": round(a_row["qualification_rate"], 3),
            "counterargument_count_avg": round(a_row["counterargument_count"], 2),
            "evidence_support_score": round(e_row["evidence_support_score"], 2),
            "technical_vocab_ratio": round(v_row["technical_vocab_ratio"], 4),
            "gunning_fog_readability": round(v_row["gunning_fog_index"], 2),
            "behavioral_balance_score": round(s_row["behavioral_balance_score"], 2),
            "dialectical_balance_index": round(f_row["dialectical_balance_index"], 3),
            "strong_modal_ratio": round(f_row["strong_modal_ratio"], 3),
            "qualitative_profile": qual_summary
        })
        
    return pd.DataFrame(profile_records)
