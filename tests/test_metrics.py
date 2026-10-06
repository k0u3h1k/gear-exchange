import pytest
import numpy as np
from src.lexical import calculate_pairwise_lexical, jaccard_similarity
from src.semantic import SemanticAnalyzer

def test_identical_responses_maximal_similarity():
    text = "Workplace surveillance can reduce employee autonomy and damage mutual trust."
    lex = calculate_pairwise_lexical(text, text)
    assert lex["jaccard_raw"] == 1.0
    assert lex["tfidf_cosine"] >= 0.99
    
    analyzer = SemanticAnalyzer()
    sem = analyzer.analyze_pair(text, text)
    assert sem["full_response_cosine"] >= 0.99
    assert sem["sentence_symmetric_alignment"] >= 0.99

def test_unrelated_responses_low_similarity():
    text_a = "Quantum computing relies on quantum bits or qubits in superposition states."
    text_b = "Baking artisan sourdough bread requires wild yeast fermentation and high hydration."
    lex = calculate_pairwise_lexical(text_a, text_b)
    assert lex["jaccard_raw"] < 0.15
    assert lex["tfidf_cosine"] < 0.15
    
    analyzer = SemanticAnalyzer()
    sem = analyzer.analyze_pair(text_a, text_b)
    # Semantic similarity should be substantially lower than on identical/related texts
    assert sem["full_response_cosine"] < 0.40

def test_synonymous_different_vocabulary():
    # As requested in the scientific test specifications:
    # A: "Workers may lose autonomy through continuous surveillance."
    # B: "Persistent monitoring can reduce employee control over how they work."
    text_a = "Workers may lose autonomy through continuous surveillance."
    text_b = "Persistent monitoring can reduce employee control over how they work."
    
    lex = calculate_pairwise_lexical(text_a, text_b)
    analyzer = SemanticAnalyzer()
    sem = analyzer.analyze_pair(text_a, text_b)
    
    # Lexical similarity should be low/moderate because words differ
    assert lex["jaccard_no_stopwords"] <= 0.40
    # Semantic similarity should be high because underlying meaning is synonymous
    assert sem["full_response_cosine"] >= 0.65
    assert sem["full_response_cosine"] > lex["jaccard_no_stopwords"]

def test_similarity_metric_bounds():
    text_a = "Autonomous algorithms select targets in warfare."
    text_b = "Legal responsibility remains with commanders and sovereign states."
    lex = calculate_pairwise_lexical(text_a, text_b)
    for k, v in lex.items():
        assert 0.0 <= v <= 1.0, f"Metric {k} out of bounds: {v}"
