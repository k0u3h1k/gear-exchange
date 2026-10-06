import os
import yaml
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class FrameworkConfig:
    input_dir: str = "./gear-exchange"
    fallback_dir: str = "./data"
    expected_models: List[str] = field(default_factory=lambda: ["ChatGPT", "Claude", "Gemini"])
    expected_prompts: int = 5
    drift_flagged_prompts: List[int] = field(default_factory=lambda: [2, 3])
    
    embedding_model_name: str = "all-MiniLM-L6-v2"
    fallback_to_tfidf: bool = True
    cache_dir: str = "./.cache/embeddings"
    
    semantic_high_similarity: float = 0.82
    semantic_moderate_similarity: float = 0.65
    lexical_high_similarity: float = 0.45
    claim_shared_similarity: float = 0.82
    claim_similar_similarity: float = 0.70
    claim_contradiction_similarity: float = 0.65
    min_claim_words: int = 4
    
    ranking_weights: Dict[str, float] = field(default_factory=lambda: {
        "information_richness": 0.25,
        "unique_information_contribution": 0.15,
        "argument_completeness": 0.15,
        "evidence_support": 0.15,
        "behavioral_balance": 0.10,
        "vocabulary_clarity_efficiency": 0.10,
        "information_density": 0.10
    })
    
    output_dir: str = "./outputs"
    figures_dir: str = "./outputs/figures"
    report_html: str = "./outputs/report.html"
    report_pdf: str = "./outputs/report.pdf"
    executive_summary: str = "./outputs/executive_summary.md"
    qc_report: str = "./outputs/qc_report.txt"
    random_seed: int = 42

def load_config(config_path: str = "config.yaml") -> FrameworkConfig:
    cfg = FrameworkConfig()
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            
        ds = data.get("dataset", {})
        cfg.input_dir = ds.get("input_dir", cfg.input_dir)
        cfg.fallback_dir = ds.get("fallback_dir", cfg.fallback_dir)
        cfg.expected_models = ds.get("expected_models", cfg.expected_models)
        cfg.expected_prompts = ds.get("expected_prompts", cfg.expected_prompts)
        cfg.drift_flagged_prompts = ds.get("drift_flagged_prompts", cfg.drift_flagged_prompts)
        
        emb = data.get("embedding", {})
        cfg.embedding_model_name = emb.get("model_name", cfg.embedding_model_name)
        cfg.fallback_to_tfidf = emb.get("fallback_to_tfidf", cfg.fallback_to_tfidf)
        cfg.cache_dir = emb.get("cache_dir", cfg.cache_dir)
        
        th = data.get("thresholds", {})
        cfg.semantic_high_similarity = th.get("semantic_high_similarity", cfg.semantic_high_similarity)
        cfg.semantic_moderate_similarity = th.get("semantic_moderate_similarity", cfg.semantic_moderate_similarity)
        cfg.lexical_high_similarity = th.get("lexical_high_similarity", cfg.lexical_high_similarity)
        cfg.claim_shared_similarity = th.get("claim_shared_similarity", cfg.claim_shared_similarity)
        cfg.claim_similar_similarity = th.get("claim_similar_similarity", cfg.claim_similar_similarity)
        cfg.claim_contradiction_similarity = th.get("claim_contradiction_similarity", cfg.claim_contradiction_similarity)
        cfg.min_claim_words = th.get("min_claim_words", cfg.min_claim_words)
        
        cr = data.get("composite_ranking", {})
        if "weights" in cr:
            cfg.ranking_weights = cr["weights"]
            
        out = data.get("output", {})
        cfg.output_dir = out.get("output_dir", cfg.output_dir)
        cfg.figures_dir = out.get("figures_dir", cfg.figures_dir)
        cfg.report_html = out.get("report_html", cfg.report_html)
        cfg.report_pdf = out.get("report_pdf", cfg.report_pdf)
        cfg.executive_summary = out.get("executive_summary", cfg.executive_summary)
        cfg.qc_report = out.get("qc_report", cfg.qc_report)
        
        cfg.random_seed = data.get("random_seed", cfg.random_seed)
        
    os.makedirs(cfg.output_dir, exist_ok=True)
    os.makedirs(cfg.figures_dir, exist_ok=True)
    os.makedirs(cfg.cache_dir, exist_ok=True)
    return cfg
