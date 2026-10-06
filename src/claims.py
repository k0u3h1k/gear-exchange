import re
import pandas as pd
from typing import List, Dict, Any, Tuple

# Patterns identifying specific discourse markers and claim types
CAUSAL_PATTERNS = [
    r'\b(?:cause|causes|caused|lead to|leads to|led to|result in|results in|resulting in|produce|produces|produced|triggers?|induces?|creates?|creating|erodes?|eroding|boosts?|increases?|decreases?|reduces?)\b',
    r'\b(?:because|due to|as a result of|thereby|consequently)\b'
]
NORMATIVE_PATTERNS = [
    r'\b(?:should|ought to|must|have to|duty|ethical|unethical|imperative|moral|acceptable|unacceptable|right|wrong|degrading)\b'
]
RECOMMENDATION_PATTERNS = [
    r'\b(?:recommend|suggest|propose|employers should|companies should|organizations should|workers should|ought to|best practice|principle)\b'
]
PREDICTIVE_PATTERNS = [
    r'\b(?:will|is likely to|are likely to|could lead|future|trend|predict|projected)\b'
]
DEFINITIONAL_PATTERNS = [
    r'\b(?:is defined as|refers to|means that|is classified as|constitutes|is considered)\b'
]
LEGAL_PATTERNS = [
    r'\b(?:international humanitarian law|ihl|rome statute|command responsibility|state responsibility|article \d+|mens rea|liability|prosecut|tort|sovereign immunity|legal)\b'
]
FACTUAL_PATTERNS = [
    r'\b(?:\d+%(?:\s+of)?|studies|research|experiment|longitudinal study|survey|doi|pubmed|found that|demonstrated|documented)\b'
]

def classify_claim_type(text: str) -> str:
    lower = text.lower()
    if any(re.search(p, lower) for p in LEGAL_PATTERNS):
        return "LEGAL/DOCTRINAL"
    if any(re.search(p, lower) for p in FACTUAL_PATTERNS):
        return "FACTUAL"
    if any(re.search(p, lower) for p in RECOMMENDATION_PATTERNS):
        return "RECOMMENDATION"
    if any(re.search(p, lower) for p in NORMATIVE_PATTERNS):
        return "NORMATIVE"
    if any(re.search(p, lower) for p in CAUSAL_PATTERNS):
        return "CAUSAL"
    if any(re.search(p, lower) for p in PREDICTIVE_PATTERNS):
        return "PREDICTIVE"
    if any(re.search(p, lower) for p in DEFINITIONAL_PATTERNS):
        return "DEFINITIONAL"
    return "OPINION"

def is_valid_claim(sentence: str) -> bool:
    s = sentence.strip()
    # Exclude headers, markdown formatting artifacts, short fragments
    if len(s.split()) < 4:
        return False
    if s.startswith('#') or s.startswith('|') or s.startswith('---'):
        return False
    if s.lower().startswith('here is a breakdown') or s.lower().startswith('let me lay out'):
        return False
    if s.lower().startswith('if you\'re weighing this') or s.lower().startswith('if you\'re approaching this'):
        return False
    return True

def clean_claim_text(s: str) -> str:
    # Clean leading bullet markers, markdown bold/italic tags, cite tokens
    cleaned = re.sub(r'^[#*\s\d.-]+', '', s).strip()
    cleaned = re.sub(r'\[.*?\](\[.*?\])?', '', cleaned).strip()
    cleaned = re.sub(r'[*_`]', '', cleaned).strip()
    return cleaned

def extract_atomic_claims(df: pd.DataFrame) -> pd.DataFrame:
    """Extracts atomic informational claims from parsed model responses."""
    claims = []
    claim_counter = 1
    
    for _, row in df.iterrows():
        p_id = row["prompt_id"]
        model = row["model_name"]
        text = row["response_text"]
        
        # Split on paragraph and clause/sentence boundaries
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        for line in lines:
            # Check if line is bullet or numbered item
            if line.startswith('*') or line.startswith('-') or re.match(r'^\d+\.', line):
                # Candidate atomic claim
                cleaned = clean_claim_text(line)
                if is_valid_claim(cleaned):
                    c_type = classify_claim_type(cleaned)
                    claims.append({
                        "claim_id": f"CLM-{claim_counter:04d}",
                        "prompt_id": p_id,
                        "model": model,
                        "claim_text": cleaned,
                        "claim_type": c_type,
                        "word_count": len(cleaned.split())
                    })
                    claim_counter += 1
            else:
                # Regular paragraph: split into sentences
                sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9])', line)
                for sent in sentences:
                    cleaned = clean_claim_text(sent)
                    if is_valid_claim(cleaned):
                        c_type = classify_claim_type(cleaned)
                        claims.append({
                            "claim_id": f"CLM-{claim_counter:04d}",
                            "prompt_id": p_id,
                            "model": model,
                            "claim_text": cleaned,
                            "claim_type": c_type,
                            "word_count": len(cleaned.split())
                        })
                        claim_counter += 1
                        
    return pd.DataFrame(claims)
