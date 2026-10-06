import re
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any

FRAMING_LEXICONS = {
    "risk": [r'\b(?:risk|risks|danger|dangers|harm|harms|threat|threats|burnout|anxiety|stress|peril|vulnerability|backfire)\b'],
    "benefit": [r'\b(?:benefit|benefits|advantage|advantages|improve|improves|improved|optimize|optimizes|efficiency|gain|gains|protection)\b'],
    "moral": [r'\b(?:dignity|moral|morals|ethics|ethical|unethical|justice|rights|degrading|humanity|dehumaniz|respect)\b'],
    "legal": [r'\b(?:law|legal|statute|ihl|treaty|liability|prosecute|jurisdiction|sovereign|immunity|court|negligence)\b'],
    "economic": [r'\b(?:cost|costs|turnover|market|markets|profit|wages|financial|economic|competitive|attrition)\b'],
    "emotional": [r'\b(?:loneliness|pain|isolated|isolation|connection|alienation|comfort|rejection|intimacy|solipsism)\b']
}

STRONG_MODALS = [r'\b(?:must|will|shall|definitely|cannot)\b']
WEAK_MODALS = [r'\b(?:may|might|could|possibly|perhaps)\b']

def analyze_framing_characteristics(text: str) -> Dict[str, Any]:
    lower = text.lower()
    tokens = re.findall(r'\b[a-zA-Z0-9_\'-]+\b', lower)
    total_tokens = max(1, len(tokens))
    
    # Calculate density for each framing category
    framing_scores = {}
    for frame, patterns in FRAMING_LEXICONS.items():
        count = sum(len(re.findall(p, lower)) for p in patterns)
        framing_scores[f"{frame}_framing_density"] = round((count / total_tokens) * 100, 2)
        
    strong_modal_count = sum(len(re.findall(p, lower)) for p in STRONG_MODALS)
    weak_modal_count = sum(len(re.findall(p, lower)) for p in WEAK_MODALS)
    
    modal_ratio = round(strong_modal_count / max(1, (strong_modal_count + weak_modal_count)), 3)
    
    # Dialectical balance between Risk and Benefit
    risk_d = framing_scores["risk_framing_density"]
    benefit_d = framing_scores["benefit_framing_density"]
    balance_index = round(1.0 - abs(risk_d - benefit_d) / max(0.1, (risk_d + benefit_d)), 3)
    
    return {
        **framing_scores,
        "strong_modal_count": strong_modal_count,
        "weak_modal_count": weak_modal_count,
        "strong_modal_ratio": modal_ratio,
        "dialectical_balance_index": max(0.0, balance_index)
    }

def compute_all_framing_metrics(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    records = []
    for _, row in df.iterrows():
        p_id = row["prompt_id"]
        model = row["model_name"]
        text = row["response_text"]
        f_res = analyze_framing_characteristics(text)
        records.append({
            "prompt_id": p_id,
            "model_name": model,
            **f_res
        })
    results_df = pd.DataFrame(records)
    
    summary_df = results_df.groupby("model_name")[[
        "risk_framing_density", "benefit_framing_density", "moral_framing_density",
        "legal_framing_density", "economic_framing_density", "emotional_framing_density",
        "strong_modal_ratio", "dialectical_balance_index"
    ]].mean().reset_index().round(3)
    
    return results_df, summary_df
