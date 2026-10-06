import re
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

# Patterns identifying visible discourse reasoning markers
EVIDENCE_MARKERS = [
    r'\b(?:studies|research|survey|data|experiment|findings|consistently find|documented|demonstrated|statistics|reports|percent|%|doi|pubmed|according to)\b'
]
REASONING_MARKERS = [
    r'\b(?:therefore|because|since|consequently|as a result|this means that|leads to|results in|implies|thus|hence|in order to|so that)\b'
]
COUNTERARGUMENT_MARKERS = [
    r'\b(?:however|on the other hand|conversely|critics argue|counter-argument|in contrast|others counter|alternative view|nevertheless|yet|despite)\b'
]
QUALIFICATION_MARKERS = [
    r'\b(?:depends heavily on|to some degree|in certain contexts|under specific conditions|partly|in narrowly defined|not inherently|nuance|trade-off|not necessarily)\b'
]
CONCLUSION_MARKERS = [
    r'\b(?:in short|in conclusion|ultimately|the reality is|my conclusion|the bottom line|so the answer is|to summarize)\b'
]
RECOMMENDATION_MARKERS = [
    r'\b(?:employers should|organizations should|companies should|workers should|we should|best practice|recommend|must retain|ought to|framework)\b'
]

def analyze_argument_structure(text: str) -> Dict[str, Any]:
    """Analyzes explicitly articulated argument components in the response text."""
    lower = text.lower()
    sentences = [s.strip() for s in re.split(r'[.!?]+(?:\s+|\n+)', text) if s.strip()]
    n_sents = max(1, len(sentences))
    
    # Counts of explicit markers across sentences
    evidence_count = sum(1 for s in sentences if any(re.search(p, s.lower()) for p in EVIDENCE_MARKERS))
    reasoning_count = sum(1 for s in sentences if any(re.search(p, s.lower()) for p in REASONING_MARKERS))
    counter_count = sum(1 for s in sentences if any(re.search(p, s.lower()) for p in COUNTERARGUMENT_MARKERS))
    qualification_count = sum(1 for s in sentences if any(re.search(p, s.lower()) for p in QUALIFICATION_MARKERS))
    conclusion_count = sum(1 for s in sentences if any(re.search(p, s.lower()) for p in CONCLUSION_MARKERS))
    recomm_count = sum(1 for s in sentences if any(re.search(p, s.lower()) for p in RECOMMENDATION_MARKERS))
    
    # Structural flags
    has_counterargument = counter_count > 0
    has_evidence = evidence_count > 0
    has_qualification = qualification_count > 0
    has_conclusion = conclusion_count > 0
    has_recommendation = recomm_count > 0
    
    # Reasoning density: proportion of sentences containing inferential links
    reasoning_density = round(reasoning_count / n_sents, 3)
    qualification_rate = round(qualification_count / n_sents, 3)
    evidence_rate = round(evidence_count / n_sents, 3)
    
    # Argument Completeness Score (0-100):
    # Evaluates presence of core dialectical elements: Premise/Reasoning + Evidence + Counterargument + Qualification + Conclusion
    component_coverage = (
        (1.0 if reasoning_count >= 2 else 0.5 if reasoning_count == 1 else 0.0) * 20.0 +
        (1.0 if has_evidence else 0.0) * 20.0 +
        (1.0 if has_counterargument else 0.0) * 20.0 +
        (1.0 if has_qualification else 0.0) * 20.0 +
        (1.0 if has_conclusion or has_recommendation else 0.0) * 20.0
    )
    
    return {
        "sentence_count": n_sents,
        "evidence_count": evidence_count,
        "reasoning_count": reasoning_count,
        "counterargument_count": counter_count,
        "qualification_count": qualification_count,
        "conclusion_count": conclusion_count,
        "recommendation_count": recomm_count,
        "reasoning_density": reasoning_density,
        "qualification_rate": qualification_rate,
        "evidence_rate": evidence_rate,
        "has_counterargument": has_counterargument,
        "has_evidence": has_evidence,
        "argument_completeness_score": round(component_coverage, 2)
    }

def compute_all_argument_metrics(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    records = []
    for _, row in df.iterrows():
        p_id = row["prompt_id"]
        model = row["model_name"]
        text = row["response_text"]
        arg_data = analyze_argument_structure(text)
        records.append({
            "prompt_id": p_id,
            "model_name": model,
            **arg_data
        })
    results_df = pd.DataFrame(records)
    
    summary_df = results_df.groupby("model_name")[[
        "evidence_count", "reasoning_count", "counterargument_count",
        "qualification_count", "conclusion_count", "recommendation_count",
        "reasoning_density", "qualification_rate", "evidence_rate",
        "argument_completeness_score"
    ]].mean().reset_index().round(3)
    
    return results_df, summary_df
