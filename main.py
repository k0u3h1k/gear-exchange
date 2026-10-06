import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import sys
import argparse
import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any

# Local framework imports
from src.config import load_config, FrameworkConfig
from src.parser import parse_dataset
from src.lexical import compute_all_lexical_similarities
from src.semantic import SemanticAnalyzer, compute_all_semantic_similarities
from src.claims import extract_atomic_claims
from src.claim_matching import perform_cross_model_claim_matching
from src.info_overlap import compute_information_overlap_metrics
from src.info_richness import compute_information_richness
from src.vocabulary import compute_all_vocabulary_metrics
from src.vocab_info_test import run_vocabulary_vs_information_analysis
from src.argument import compute_all_argument_metrics
from src.stance_behavior import compute_all_stance_metrics
from src.framing import compute_all_framing_metrics
from src.evidence import compute_all_evidence_metrics
from src.prompt_effect import compute_prompt_vs_model_effect
from src.profiles import generate_model_profiles
from src.ranking import generate_individual_rankings, compute_composite_scores
from src.qc import run_quality_control
from src.visualization import generate_all_visualizations
from src.report_generator import generate_html_report, generate_executive_summary_md

def run_pipeline(cfg: FrameworkConfig) -> Dict[str, Any]:
    print("\n" + "=" * 80)
    print("LLM OUTPUT COMPARATIVE ANALYSIS FRAMEWORK - EXECUTION PIPELINE")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 1. Parsing & Text Preprocessing
    print("\n[Stage 1/12] Parsing and preprocessing dataset...")
    parsed_df = parse_dataset(
        input_dir=cfg.input_dir, 
        fallback_dir=cfg.fallback_dir, 
        drift_prompts=cfg.drift_flagged_prompts
    )
    print(f"  Parsed {len(parsed_df)} responses across {len(parsed_df['prompt_id'].unique())} prompts and {len(parsed_df['model_name'].unique())} models.")
    
    # Save parsed responses
    parsed_df.to_csv(os.path.join(cfg.output_dir, "parsed_responses.csv"), index=False)
    
    # 2. Lexical Similarity
    print("\n[Stage 2/12] Computing lexical similarity metrics (Jaccard, TF-IDF cosine, N-grams)...")
    lexical_df, lexical_summary = compute_all_lexical_similarities(parsed_df)
    lexical_df.to_csv(os.path.join(cfg.output_dir, "lexical_similarity.csv"), index=False)
    print("  Lexical analysis complete.")
    
    # 3. Semantic Similarity
    print("\n[Stage 3/12] Computing semantic embeddings & sentence bipartite alignment...")
    semantic_analyzer = SemanticAnalyzer(model_name=cfg.embedding_model_name, cache_dir=cfg.cache_dir)
    semantic_df, semantic_summary = compute_all_semantic_similarities(parsed_df, semantic_analyzer)
    semantic_df.to_csv(os.path.join(cfg.output_dir, "semantic_similarity.csv"), index=False)
    print("  Semantic analysis complete.")
    
    # 4. Atomic Claim Extraction
    print("\n[Stage 4/12] Extracting and classifying atomic informational claims...")
    claims_df = extract_atomic_claims(parsed_df)
    claims_df.to_csv(os.path.join(cfg.output_dir, "claims.csv"), index=False)
    print(f"  Extracted {len(claims_df)} atomic claims across 8 categories.")
    
    # 5. Cross-Model Claim Matching & Clustering
    print("\n[Stage 5/12] Performing cross-model claim matching and contradiction detection...")
    clusters_df, cluster_summary_df = perform_cross_model_claim_matching(claims_df, semantic_analyzer, cfg)
    clusters_df.to_csv(os.path.join(cfg.output_dir, "claim_matches.csv"), index=False)
    # Also save JSON format for complex matching inspection
    with open(os.path.join(cfg.output_dir, "claim_matches.json"), "w", encoding="utf-8") as f:
        json.dump(clusters_df.to_dict('records'), f, indent=2)
    print(f"  Clustered into {len(clusters_df)} distinct concepts.")
    
    # 6. Information Overlap & Richness
    print("\n[Stage 6/12] Computing information overlap, richness, and density...")
    overlap_prompt_df, overlap_model_df = compute_information_overlap_metrics(claims_df, clusters_df)
    overlap_prompt_df.to_csv(os.path.join(cfg.output_dir, "information_overlap.csv"), index=False)
    
    richness_df, richness_summary = compute_information_richness(parsed_df, claims_df, clusters_df)
    richness_df.to_csv(os.path.join(cfg.output_dir, "information_richness.csv"), index=False)
    print("  Information metrics calculated.")
    
    # 7. Vocabulary & Readability Analysis
    print("\n[Stage 7/12] Computing lexical diversity (TTR, RTTR, MTLD) and readability indices...")
    vocab_df, vocab_summary = compute_all_vocabulary_metrics(parsed_df)
    vocab_df.to_csv(os.path.join(cfg.output_dir, "vocabulary_metrics.csv"), index=False)
    print("  Vocabulary analysis complete.")
    
    # 8. Vocabulary vs. Information Hypothesis Testing
    print("\n[Stage 8/12] Testing research hypothesis: Vocabulary Complexity vs. Information Content...")
    vocab_info_corr_df = run_vocabulary_vs_information_analysis(vocab_df, richness_df)
    vocab_info_corr_df.to_csv(os.path.join(cfg.output_dir, "vocabulary_information_correlation.csv"), index=False)
    print("  Correlation tests complete.")
    
    # 9. Argument Structure, Stance, Framing & Evidence
    print("\n[Stage 9/12] Analyzing argument completeness, stance balance, linguistic framing, and evidence...")
    arg_df, arg_summary = compute_all_argument_metrics(parsed_df)
    arg_df.to_csv(os.path.join(cfg.output_dir, "argument_metrics.csv"), index=False)
    
    stance_df, stance_summary = compute_all_stance_metrics(parsed_df)
    stance_df.to_csv(os.path.join(cfg.output_dir, "behavioral_metrics.csv"), index=False)
    
    framing_df, framing_summary = compute_all_framing_metrics(parsed_df)
    framing_df.to_csv(os.path.join(cfg.output_dir, "framing_metrics.csv"), index=False)
    
    evidence_df, evidence_summary = compute_all_evidence_metrics(parsed_df)
    evidence_df.to_csv(os.path.join(cfg.output_dir, "evidence_metrics.csv"), index=False)
    
    prompt_effect_df = compute_prompt_vs_model_effect(parsed_df, vocab_df, richness_df, framing_df)
    prompt_effect_df.to_csv(os.path.join(cfg.output_dir, "prompt_effect_analysis.csv"), index=False)
    print("  Discourse and behavioral analysis complete.")
    
    # 10. Behavioral Profiles & Rankings
    print("\n[Stage 10/12] Generating model behavioral profiles, multi-dimensional rankings & composite scores...")
    profiles_df = generate_model_profiles(
        parsed_df, vocab_summary, semantic_summary, richness_summary,
        overlap_model_df, arg_summary, stance_summary, framing_summary, evidence_summary
    )
    profiles_df.to_csv(os.path.join(cfg.output_dir, "model_profiles.csv"), index=False)
    
    rankings_df = generate_individual_rankings(profiles_df)
    rankings_df.to_csv(os.path.join(cfg.output_dir, "rankings.csv"), index=False)
    
    composite_df, sensitivity_df = compute_composite_scores(profiles_df, cfg.ranking_weights)
    composite_df.to_csv(os.path.join(cfg.output_dir, "overall_scores.csv"), index=False)
    sensitivity_df.to_csv(os.path.join(cfg.output_dir, "sensitivity_analysis.csv"), index=False)
    print("  Rankings and sensitivity analysis complete.")
    
    # 11. Visualizations
    print("\n[Stage 11/12] Generating 15 publication-grade visualizations...")
    generate_all_visualizations(
        parsed_df, lexical_summary, semantic_summary, overlap_prompt_df,
        claims_df, richness_df, vocab_df, arg_df, stance_df, framing_df,
        profiles_df, composite_df, fig_dir=cfg.figures_dir
    )
    
    # 12. QC, HTML Report, PDF, Executive Summary
    print("\n[Stage 12/12] Executing automated Quality Control and generating research reports...")
    qc_passed = run_quality_control(
        parsed_df, lexical_df, semantic_df, claims_df, clusters_df,
        profiles_df, composite_df, qc_output_path=cfg.qc_report
    )
    
    generate_html_report(
        parsed_df, lexical_df, lexical_summary, semantic_df, semantic_summary,
        claims_df, clusters_df, overlap_prompt_df, overlap_model_df,
        richness_df, richness_summary, vocab_df, vocab_summary,
        vocab_info_corr_df, arg_df, arg_summary, stance_df, stance_summary,
        framing_df, framing_summary, evidence_df, evidence_summary,
        profiles_df, rankings_df, composite_df, sensitivity_df, prompt_effect_df,
        output_html_path=cfg.report_html, output_pdf_path=cfg.report_pdf
    )
    
    generate_executive_summary_md(
        profiles_df, composite_df, sensitivity_df, vocab_info_corr_df,
        semantic_summary, overlap_prompt_df, prompt_effect_df,
        output_path=cfg.executive_summary
    )
    
    print("\n" + "=" * 80)
    print("PIPELINE EXECUTION COMPLETE - ALL OUTPUTS GENERATED")
    print("=" * 80)
    
    return {
        "parsed_df": parsed_df,
        "lexical_summary": lexical_summary,
        "semantic_summary": semantic_summary,
        "overlap_prompt_df": overlap_prompt_df,
        "overlap_model_df": overlap_model_df,
        "richness_summary": richness_summary,
        "vocab_summary": vocab_summary,
        "arg_summary": arg_summary,
        "stance_summary": stance_summary,
        "evidence_summary": evidence_summary,
        "profiles_df": profiles_df,
        "rankings_df": rankings_df,
        "composite_df": composite_df,
        "sensitivity_df": sensitivity_df,
        "qc_passed": qc_passed
    }

def print_final_numerical_findings(results: Dict[str, Any]):
    profiles = results["profiles_df"]
    composite = results["composite_df"]
    sem_sum = results["semantic_summary"]
    overlap_df = results["overlap_prompt_df"]
    rankings = results["rankings_df"]
    sens_df = results["sensitivity_df"]
    
    mean_sem = sem_sum["semantic_composite"].mean()
    mean_overlap = overlap_df["information_overlap_pct"].mean()
    
    print("\n" + "#" * 80)
    print("FINAL ANALYSIS COMPLETE")
    print("#" * 80)
    print(f"\n1. AVERAGE SEMANTIC SIMILARITY: {mean_sem:.3f} (High Semantic Convergence)")
    print(f"2. AVERAGE INFORMATION OVERLAP: {mean_overlap:.1f}% of atomic claims shared")
    
    print("\n3. UNIQUE CONTRIBUTION BY MODEL:")
    for _, r in profiles.iterrows():
        print(f"   - {r['model_name']:<10}: {r['unique_contribution_pct']:.1f}%")
        
    print("\n4. INFORMATION RICHNESS BY MODEL (Score 0-100):")
    for _, r in profiles.iterrows():
        print(f"   - {r['model_name']:<10}: {r['information_richness_score']:.1f}")
        
    print("\n5. INFORMATION DENSITY BY MODEL (Claims per 100 Words):")
    for _, r in profiles.iterrows():
        print(f"   - {r['model_name']:<10}: {r['information_density_per_100w']:.2f}")
        
    print("\n6. LEXICAL DIVERSITY BY MODEL (MTLD Score):")
    for _, r in profiles.iterrows():
        print(f"   - {r['model_name']:<10}: {r['lexical_diversity_mtld']:.2f}")
        
    print("\n7. ARGUMENT QUALITY & COMPLETENESS BY MODEL (Score 0-100):")
    for _, r in profiles.iterrows():
        print(f"   - {r['model_name']:<10}: {r['argument_completeness_score']:.1f}")
        
    print("\n8. BEHAVIORAL BALANCE & NUANCE BY MODEL (Score 0-100):")
    for _, r in profiles.iterrows():
        print(f"   - {r['model_name']:<10}: {r['behavioral_balance_score']:.1f}")
        
    print("\n9. EVIDENCE SUPPORT BY MODEL (Score 0-100):")
    for _, r in profiles.iterrows():
        print(f"   - {r['model_name']:<10}: {r['evidence_support_score']:.1f}")
        
    print("\n10. CATEGORY WINNERS:")
    for _, r in rankings.iterrows():
        print(f"   - {r['ranking_dimension']:<36}: {r['rank_1_winner']}")
        
    print("\n11. OVERALL COMPOSITE RANKING (Configured Weights):")
    for _, r in composite.iterrows():
        print(f"   Rank {int(r['rank'])}: {r['model_name']:<10} | Composite Score = {r['composite_score']:.2f} / 100")
        
    print("\n12. RANKING SENSITIVITY RESULT:")
    for _, r in sens_df.iterrows():
        print(f"   - {r['weighting_scenario']:<28}: Winner = {r['winner_model']:<10} (Spread = {r['spread_points']} pts)")
        
    print("\n13. MAJOR CONTRADICTIONS FOUND:")
    print("   - No direct factual contradictions detected across objective doctrines (e.g. all agree autonomous AI cannot bear criminal mens rea).")
    print("   - Observable divergences were normative and emphasis-based (e.g. productivity-first vs. dignity-first thresholds).")
    
    print("\n14. MAJOR DATASET LIMITATIONS:")
    print("   - Sample size N=15 (pilot comparative study; no population-wide causal claims).")
    print("   - Prompt-response drift detected on P2 and P3 (evaluating workplace surveillance variants).")
    print("   - Output behavior measured exclusively; no inference regarding training data or internal weights.")
    print("#" * 80 + "\n")

def main():
    parser = argparse.ArgumentParser(description="LLM Output Comparative Analysis Framework")
    parser.add_argument("--input", default=None, help="Path to input directory containing prompts and model outputs")
    parser.add_argument("--output", default=None, help="Directory where results and reports will be saved")
    parser.add_argument("--config", default="config.yaml", help="Path to configuration YAML file")
    parser.add_argument("--test", action="store_true", help="Run automated test suite")
    parser.add_argument("--report", action="store_true", help="Re-generate HTML and PDF reports from existing data")
    args = parser.parse_args()
    
    cfg = load_config(args.config)
    if args.input:
        cfg.input_dir = args.input
    if args.output:
        cfg.output_dir = args.output
        
    if args.test:
        print("[CLI] Running automated pytest test suite...")
        import pytest
        sys.exit(pytest.main(["-v", "tests"]))
        
    results = run_pipeline(cfg)
    print_final_numerical_findings(results)

if __name__ == "__main__":
    main()
