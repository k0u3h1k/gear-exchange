import pytest
import pandas as pd
from src.claims import classify_claim_type, clean_claim_text, is_valid_claim

def test_claim_type_classification():
    factual = "A 2026 study found that 72% of monitored employees reported negative outcomes."
    causal = "Continuous monitoring causes elevated stress and leads to employee burnout."
    normative = "Employers should prioritize human dignity and fundamental rights."
    legal = "Under the Rome Statute, command responsibility requires proof of intent or knowledge."
    
    assert classify_claim_type(factual) == "FACTUAL"
    assert classify_claim_type(causal) == "CAUSAL"
    assert classify_claim_type(normative) in ["NORMATIVE", "RECOMMENDATION"]
    assert classify_claim_type(legal) == "LEGAL/DOCTRINAL"

def test_valid_claim_filters():
    assert not is_valid_claim("### The case against it")
    assert not is_valid_claim("short")
    assert not is_valid_claim("---")
    assert is_valid_claim("Surveillance software records keystrokes and active application windows.")

def test_clean_claim_text():
    raw = "* **Loss of autonomy:** workers have less control over their daily schedules."
    cleaned = clean_claim_text(raw)
    assert "**" not in cleaned
    assert not cleaned.startswith("*")
