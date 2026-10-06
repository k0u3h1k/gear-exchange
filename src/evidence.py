import re
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any

# Patterns identifying concrete references and empirical citations
CITATION_PATTERNS = [
    r'\[(?:doi|pubmed|sciencedirect|frontiers|icrc|human rights watch|uq law school)\]',
    r'\b(?:article 36|rome statute|gdpr|robert sparrow|ccw)\b',
    r'\b\d{4}\s+(?:longitudinal\s+)?study\b',
    r'\b\d+%\s+of\b',
    r'\b\d+-\d+%\b',
    r'\b(?:longitudinal study involving|experiment found that|survey)\b'
]

def analyze_evidence_support(text: str) -> Dict[str, Any]:
    lower = text.lower()
    sentences = [s.strip() for s in re.split(r'[.!?]+(?:\s+|\n+)', text) if s.strip()]
    
    # Specific citation / empirical marker matches
    matches = []
    for p in CITATION_PATTERNS:
        found = re.findall(p, lower)
        matches.extend(found)
        
    citation_count = len(matches)
    
    # Quantitative claims (percentages, numbers like 2,000 adults)
    quant_claims = len(re.findall(r'\b(?:\d+%(?:-\d+%)?|\d+,\d+\s+adults)\b', lower))
    
    # Legal / Institutional sources
    named_entities = len(re.findall(r'\b(?:icrc|human rights watch|rome statute|eu\'s gdpr|robert sparrow|un general assembly)\b', lower))
    
    # Evidence Support Score (0-100)
    raw_support = (citation_count * 15.0) + (quant_claims * 10.0) + (named_entities * 12.0)
    evidence_support_score = min(100.0, raw_support)
    
    return {
        "citation_count": citation_count,
        "quantitative_claim_count": quant_claims,
        "named_source_count": named_entities,
        "evidence_support_score": round(evidence_support_score, 2)
    }

def compute_all_evidence_metrics(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    records = []
    for _, row in df.iterrows():
        p_id = row["prompt_id"]
        model = row["model_name"]
        text = row["response_text"]
        ev = analyze_evidence_support(text)
        records.append({
            "prompt_id": p_id,
            "model_name": model,
            **ev
        })
    results_df = pd.DataFrame(records)
    
    summary_df = results_df.groupby("model_name")[[
        "citation_count", "quantitative_claim_count", "named_source_count", "evidence_support_score"
    ]].mean().reset_index().round(2)
    
    return results_df, summary_df
