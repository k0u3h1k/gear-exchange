import re
import math
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Any

from src.lexical import STOPWORDS

# Domain specific technical lexicons
DOMAIN_TERMS = {
    # Labor & Workplace surveillance
    "surveillance", "bossware", "keystroke", "monitoring", "telemetry", "asymmetry",
    "panopticon", "performative", "neurodivergent", "discretionary", "optimization",
    "autonomy", "attrition", "proportionality", "solipsism", "reciprocity",
    # Law & Autonomous Systems
    "humanitarian", "proportionality", "precautions", "collateral", "mens", "rea",
    "subordinate", "accountability", "jurisdictions", "sovereign", "immunity",
    "negligence", "reparations", "treaty", "sparrow", "culpable", "tribunal"
}

def count_syllables(word: str) -> int:
    w = word.lower().strip()
    if len(w) <= 3:
        return 1
    w = re.sub(r'(?:[^laeiouy]|ed|es|e)$', '', w)
    w = re.sub(r'^y', '', w)
    syllables = len(re.findall(r'[aeiouy]{1,2}', w))
    return max(1, syllables)

def calculate_mtld(tokens: List[str], threshold: float = 0.72) -> float:
    """Calculates the Measure of Textual Lexical Diversity (MTLD)."""
    if len(tokens) < 10:
        return float(len(set(tokens)))
        
    def _mtld_calc(toks):
        factors = 0.0
        current_types = set()
        current_tokens = 0
        for t in toks:
            current_tokens += 1
            current_types.add(t)
            ttr = len(current_types) / current_tokens
            if ttr <= threshold:
                factors += 1.0
                current_types = set()
                current_tokens = 0
        if current_tokens > 0:
            excess_ttr = len(current_types) / current_tokens
            if excess_ttr < 1.0:
                factors += (1.0 - excess_ttr) / (1.0 - threshold)
        return len(toks) / max(1e-5, factors)

    forward = _mtld_calc(tokens)
    backward = _mtld_calc(tokens[::-1])
    return round((forward + backward) / 2.0, 2)

def compute_vocabulary_metrics_for_text(text: str) -> Dict[str, float]:
    tokens = re.findall(r'\b[a-zA-Z0-9_\'-]+\b', text.lower())
    total_words = len(tokens)
    if total_words == 0:
        return {}
        
    types = set(tokens)
    unique_words = len(types)
    
    ttr = unique_words / total_words
    rttr = unique_words / math.sqrt(total_words)
    mtld = calculate_mtld(tokens)
    
    content_words = [t for t in tokens if t not in STOPWORDS]
    lexical_density = len(content_words) / total_words
    
    avg_word_len = sum(len(t) for t in tokens) / total_words
    
    # Sentences
    sentences = [s.strip() for s in re.split(r'[.!?]+(?:\s+|\n+)', text) if s.strip()]
    sentence_count = max(1, len(sentences))
    avg_sentence_len = total_words / sentence_count
    
    # Technical ratio
    tech_count = sum(1 for t in tokens if t in DOMAIN_TERMS)
    technical_ratio = tech_count / total_words
    
    # Readability: Flesch Reading Ease & Kincaid Grade & Gunning Fog
    total_syllables = sum(count_syllables(t) for t in tokens)
    syllables_per_word = total_syllables / total_words
    complex_words = sum(1 for t in tokens if count_syllables(t) >= 3 and t not in STOPWORDS)
    pct_complex = (complex_words / total_words) * 100.0
    
    # Flesch Reading Ease: 206.835 - 1.015*(words/sents) - 84.6*(syllables/words)
    flesch_reading_ease = 206.835 - (1.015 * avg_sentence_len) - (84.6 * syllables_per_word)
    # Flesch-Kincaid Grade: 0.39*(words/sents) + 11.8*(syllables/words) - 15.59
    flesch_kincaid_grade = (0.39 * avg_sentence_len) + (11.8 * syllables_per_word) - 15.59
    # Gunning Fog: 0.4 * ( (words/sents) + Pct_Complex )
    gunning_fog = 0.4 * (avg_sentence_len + pct_complex)
    
    return {
        "word_count": total_words,
        "unique_vocab": unique_words,
        "ttr": round(ttr, 4),
        "rttr": round(rttr, 3),
        "mtld": round(mtld, 2),
        "lexical_density": round(lexical_density, 4),
        "avg_word_length": round(avg_word_len, 2),
        "avg_sentence_length": round(avg_sentence_len, 2),
        "technical_vocab_ratio": round(technical_ratio, 4),
        "flesch_reading_ease": round(flesch_reading_ease, 2),
        "flesch_kincaid_grade": round(flesch_kincaid_grade, 2),
        "gunning_fog_index": round(gunning_fog, 2)
    }

def compute_all_vocabulary_metrics(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    records = []
    for _, row in df.iterrows():
        p_id = row["prompt_id"]
        model = row["model_name"]
        text = row["response_text"]
        v_metrics = compute_vocabulary_metrics_for_text(text)
        records.append({
            "prompt_id": p_id,
            "model_name": model,
            **v_metrics
        })
    results_df = pd.DataFrame(records)
    
    summary_df = results_df.groupby("model_name")[[
        "word_count", "unique_vocab", "ttr", "rttr", "mtld",
        "lexical_density", "avg_word_length", "avg_sentence_length",
        "technical_vocab_ratio", "flesch_reading_ease",
        "flesch_kincaid_grade", "gunning_fog_index"
    ]].mean().reset_index().round(3)
    
    return results_df, summary_df
