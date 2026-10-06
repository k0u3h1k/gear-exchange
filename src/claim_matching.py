import re
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Any, Set
from sklearn.metrics.pairwise import cosine_similarity
from src.semantic import SemanticAnalyzer

NEGATION_PATTERNS = [
    r'\b(?:not|cannot|can\'t|never|no|neither|nor|fails to|does not|doesn\'t|won\'t|without)\b'
]

def has_negation(text: str) -> bool:
    lower = text.lower()
    return any(re.search(p, lower) for p in NEGATION_PATTERNS)

def match_claims_for_prompt(
    claims_df: pd.DataFrame, 
    prompt_id: int, 
    analyzer: SemanticAnalyzer,
    threshold_shared: float = 0.80,
    threshold_similar: float = 0.68,
    threshold_contradiction: float = 0.65
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Matches claims across ChatGPT, Claude, and Gemini for a single prompt."""
    p_claims = claims_df[claims_df["prompt_id"] == prompt_id].copy()
    if p_claims.empty:
        return [], {}
        
    models = ["ChatGPT", "Claude", "Gemini"]
    model_claims = {m: p_claims[p_claims["model"] == m].to_dict('records') for m in models}
    
    # Pre-encode all claims for this prompt
    all_claim_list = p_claims.to_dict('records')
    claim_texts = [c["claim_text"] for c in all_claim_list]
    embeddings = analyzer.encode(claim_texts)
    
    emb_lookup = {c["claim_id"]: embeddings[i] for i, c in enumerate(all_claim_list)}
    
    matched_clusters = []
    claimed_ids = set()
    
    # Helper to calculate cosine
    def get_cos(c_id1, c_id2):
        v1 = emb_lookup[c_id1].reshape(1, -1)
        v2 = emb_lookup[c_id2].reshape(1, -1)
        return float(cosine_similarity(v1, v2)[0, 0])
        
    # First pass: find tripartite matches (shared by all 3)
    for c_chat in model_claims.get("ChatGPT", []):
        if c_chat["claim_id"] in claimed_ids:
            continue
            
        best_claude = None
        best_claude_sim = -1.0
        for c_cl in model_claims.get("Claude", []):
            if c_cl["claim_id"] not in claimed_ids:
                sim = get_cos(c_chat["claim_id"], c_cl["claim_id"])
                if sim > best_claude_sim:
                    best_claude_sim = sim
                    best_claude = c_cl
                    
        best_gemini = None
        best_gemini_sim = -1.0
        for c_gm in model_claims.get("Gemini", []):
            if c_gm["claim_id"] not in claimed_ids:
                sim = get_cos(c_chat["claim_id"], c_gm["claim_id"])
                if sim > best_gemini_sim:
                    best_gemini_sim = sim
                    best_gemini = c_gm
                    
        # Check if 3-way match
        if best_claude and best_gemini and best_claude_sim >= threshold_shared and best_gemini_sim >= threshold_shared:
            cg_sim = get_cos(best_claude["claim_id"], best_gemini["claim_id"])
            if cg_sim >= threshold_similar:
                # Contradiction check
                negs = [has_negation(c_chat["claim_text"]), has_negation(best_claude["claim_text"]), has_negation(best_gemini["claim_text"])]
                classification = "CONTRADICTORY" if (any(negs) and not all(negs)) else "SHARED_BY_ALL_3"
                
                matched_clusters.append({
                    "prompt_id": prompt_id,
                    "concept": c_chat["claim_text"][:90] + "...",
                    "chatgpt_claim": c_chat["claim_text"],
                    "claude_claim": best_claude["claim_text"],
                    "gemini_claim": best_gemini["claim_text"],
                    "chatgpt_id": c_chat["claim_id"],
                    "claude_id": best_claude["claim_id"],
                    "gemini_id": best_gemini["claim_id"],
                    "classification": classification,
                    "mean_similarity": round(float(np.mean([best_claude_sim, best_gemini_sim, cg_sim])), 4)
                })
                claimed_ids.add(c_chat["claim_id"])
                claimed_ids.add(best_claude["claim_id"])
                claimed_ids.add(best_gemini["claim_id"])
                
    # Second pass: find two-way matches
    pairs = [("ChatGPT", "Claude"), ("ChatGPT", "Gemini"), ("Claude", "Gemini")]
    for m1, m2 in pairs:
        for c1 in model_claims.get(m1, []):
            if c1["claim_id"] in claimed_ids:
                continue
            best_c2 = None
            best_sim = -1.0
            for c2 in model_claims.get(m2, []):
                if c2["claim_id"] not in claimed_ids:
                    sim = get_cos(c1["claim_id"], c2["claim_id"])
                    if sim > best_sim:
                        best_sim = sim
                        best_c2 = c2
                        
            if best_c2 and best_sim >= threshold_similar:
                neg1 = has_negation(c1["claim_text"])
                neg2 = has_negation(best_c2["claim_text"])
                if neg1 != neg2 and best_sim >= threshold_contradiction:
                    classification = "CONTRADICTORY"
                elif best_sim >= threshold_shared:
                    classification = "SHARED_BY_2"
                else:
                    classification = "SEMANTICALLY_SIMILAR"
                    
                cluster_item = {
                    "prompt_id": prompt_id,
                    "concept": c1["claim_text"][:90] + "...",
                    "chatgpt_claim": c1["claim_text"] if m1 == "ChatGPT" else (best_c2["claim_text"] if m2 == "ChatGPT" else None),
                    "claude_claim": c1["claim_text"] if m1 == "Claude" else (best_c2["claim_text"] if m2 == "Claude" else None),
                    "gemini_claim": c1["claim_text"] if m1 == "Gemini" else (best_c2["claim_text"] if m2 == "Gemini" else None),
                    "chatgpt_id": c1["claim_id"] if m1 == "ChatGPT" else (best_c2["claim_id"] if m2 == "ChatGPT" else None),
                    "claude_id": c1["claim_id"] if m1 == "Claude" else (best_c2["claim_id"] if m2 == "Claude" else None),
                    "gemini_id": c1["claim_id"] if m1 == "Gemini" else (best_c2["claim_id"] if m2 == "Gemini" else None),
                    "classification": classification,
                    "mean_similarity": round(best_sim, 4)
                }
                matched_clusters.append(cluster_item)
                claimed_ids.add(c1["claim_id"])
                claimed_ids.add(best_c2["claim_id"])
                
    # Third pass: Unmatched claims are Unique or Uncertain
    for c in all_claim_list:
        if c["claim_id"] not in claimed_ids:
            m = c["model"]
            matched_clusters.append({
                "prompt_id": prompt_id,
                "concept": c["claim_text"][:90] + "...",
                "chatgpt_claim": c["claim_text"] if m == "ChatGPT" else None,
                "claude_claim": c["claim_text"] if m == "Claude" else None,
                "gemini_claim": c["claim_text"] if m == "Gemini" else None,
                "chatgpt_id": c["claim_id"] if m == "ChatGPT" else None,
                "claude_id": c["claim_id"] if m == "Claude" else None,
                "gemini_id": c["claim_id"] if m == "Gemini" else None,
                "classification": f"UNIQUE_TO_{m.upper()}",
                "mean_similarity": 0.0
            })
            
    # Compute summary stats for this prompt
    total_distinct = len(matched_clusters)
    class_counts = pd.Series([mc["classification"] for mc in matched_clusters]).value_counts().to_dict()
    
    shared_3 = class_counts.get("SHARED_BY_ALL_3", 0)
    shared_2 = class_counts.get("SHARED_BY_2", 0) + class_counts.get("SEMANTICALLY_SIMILAR", 0)
    uniq_chat = class_counts.get("UNIQUE_TO_CHATGPT", 0)
    uniq_cl = class_counts.get("UNIQUE_TO_CLAUDE", 0)
    uniq_gm = class_counts.get("UNIQUE_TO_GEMINI", 0)
    contradictions = class_counts.get("CONTRADICTORY", 0)
    
    prompt_summary = {
        "prompt_id": prompt_id,
        "total_distinct_claims": total_distinct,
        "shared_all_3": shared_3,
        "shared_by_2": shared_2,
        "unique_chatgpt": uniq_chat,
        "unique_claude": uniq_cl,
        "unique_gemini": uniq_gm,
        "contradictions": contradictions,
        "shared_percentage": round((shared_3 + shared_2) / max(1, total_distinct) * 100, 2),
        "unique_percentage": round((uniq_chat + uniq_cl + uniq_gm) / max(1, total_distinct) * 100, 2)
    }
    
    return matched_clusters, prompt_summary

def perform_cross_model_claim_matching(
    claims_df: pd.DataFrame, 
    analyzer: SemanticAnalyzer,
    cfg: Any
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Runs cross-model claim matching across all prompts."""
    all_clusters = []
    summary_records = []
    
    for p_id in sorted(claims_df["prompt_id"].unique()):
        clusters, summary = match_claims_for_prompt(
            claims_df=claims_df,
            prompt_id=p_id,
            analyzer=analyzer,
            threshold_shared=cfg.claim_shared_similarity,
            threshold_similar=cfg.claim_similar_similarity,
            threshold_contradiction=cfg.claim_contradiction_similarity
        )
        all_clusters.extend(clusters)
        summary_records.append(summary)
        
    clusters_df = pd.DataFrame(all_clusters)
    summary_df = pd.DataFrame(summary_records)
    return clusters_df, summary_df
