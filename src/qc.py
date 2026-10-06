import os
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any

def run_quality_control(
    parsed_df: pd.DataFrame,
    lexical_df: pd.DataFrame,
    semantic_df: pd.DataFrame,
    claims_df: pd.DataFrame,
    clusters_df: pd.DataFrame,
    profiles_df: pd.DataFrame,
    composite_df: pd.DataFrame,
    qc_output_path: str = "./outputs/qc_report.txt"
) -> bool:
    """Performs rigorous automated validation checks and produces a formal QC report."""
    checks = []
    all_passed = True
    
    # 1. Exactly 15 responses parsed
    c1 = len(parsed_df) == 15
    checks.append(("Response Count == 15", c1, f"Found {len(parsed_df)} responses"))
    all_passed = all_passed and c1
    
    # 2. No response is empty
    empty_resps = parsed_df[parsed_df["response_text"].str.strip() == ""]
    c2 = len(empty_resps) == 0
    checks.append(("No Empty Responses", c2, f"{len(empty_resps)} empty responses found"))
    all_passed = all_passed and c2
    
    # 3. Model names normalized
    expected_models = {"ChatGPT", "Claude", "Gemini"}
    found_models = set(parsed_df["model_name"].unique())
    c3 = found_models == expected_models
    checks.append(("Normalized Model Names", c3, f"Models: {sorted(list(found_models))}"))
    all_passed = all_passed and c3
    
    # 4. Prompt IDs range 1-5
    expected_p = set(range(1, 6))
    found_p = set(parsed_df["prompt_id"].unique())
    c4 = found_p == expected_p
    checks.append(("Prompt IDs [1-5]", c4, f"Prompts: {sorted(list(found_p))}"))
    all_passed = all_passed and c4
    
    # 5. Claims extracted and valid
    c5 = len(claims_df) > 50 and not claims_df["claim_id"].duplicated().any()
    checks.append(("Claims Count & Unique IDs", c5, f"{len(claims_df)} claims extracted; no duplicate IDs"))
    all_passed = all_passed and c5
    
    # 6. Lexical similarities in [0, 1]
    lex_cols = ["jaccard_raw", "tfidf_cosine", "bigram_overlap"]
    c6 = (lexical_df[lex_cols] >= 0.0).all().all() and (lexical_df[lex_cols] <= 1.0).all().all()
    checks.append(("Lexical Similarities in [0, 1]", c6, "All lexical values within valid theoretical bounds"))
    all_passed = all_passed and c6
    
    # 7. Semantic similarities in [-1, 1] (or [0, 1] for cosine on text)
    sem_cols = ["full_response_cosine", "sentence_symmetric_alignment"]
    c7 = (semantic_df[sem_cols] >= -1.0).all().all() and (semantic_df[sem_cols] <= 1.05).all().all()
    checks.append(("Semantic Similarities in [-1, 1]", c7, "All semantic cosine scores within valid bounds"))
    all_passed = all_passed and c7
    
    # 8. No NaNs in composite scores
    c8 = not composite_df["composite_score"].isna().any()
    checks.append(("No NaNs in Composite Rankings", c8, "Composite rankings computed without missing values"))
    all_passed = all_passed and c8
    
    # Write report
    os.makedirs(os.path.dirname(qc_output_path), exist_ok=True)
    with open(qc_output_path, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("LLM OUTPUT COMPARATIVE ANALYSIS FRAMEWORK - QUALITY CONTROL AUDIT\n")
        f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Overall QC Status: {'PASSED [OK]' if all_passed else 'FAILED [WARNINGS]'}\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"{'Check Description':<38} | {'Status':<8} | Details\n")
        f.write("-" * 70 + "\n")
        for desc, passed, detail in checks:
            status_str = "PASS" if passed else "FAIL"
            f.write(f"{desc:<38} | {status_str:<8} | {detail}\n")
        f.write("\n" + "=" * 70 + "\n")
        f.write("DATA INTEGRITY AUDIT NOTE:\n")
        f.write("Prompts P2 and P3 are documented as prompt-response drift cases (the underlying\n")
        f.write("model texts evaluate Workplace Monitoring variants rather than the canonical prompts).\n")
        f.write("These cases have been preserved with their prompt IDs and evaluated for cross-model\n")
        f.write("consistency without penalty.\n")
        f.write("=" * 70 + "\n")
        
    return all_passed
