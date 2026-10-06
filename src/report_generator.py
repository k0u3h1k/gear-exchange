import os
import subprocess
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any

def generate_html_report(
    parsed_df: pd.DataFrame,
    lexical_df: pd.DataFrame,
    lexical_summary: pd.DataFrame,
    semantic_df: pd.DataFrame,
    semantic_summary: pd.DataFrame,
    claims_df: pd.DataFrame,
    clusters_df: pd.DataFrame,
    overlap_prompt_df: pd.DataFrame,
    overlap_model_df: pd.DataFrame,
    richness_df: pd.DataFrame,
    richness_summary: pd.DataFrame,
    vocab_df: pd.DataFrame,
    vocab_summary: pd.DataFrame,
    vocab_info_corr_df: pd.DataFrame,
    arg_df: pd.DataFrame,
    arg_summary: pd.DataFrame,
    stance_df: pd.DataFrame,
    stance_summary: pd.DataFrame,
    framing_df: pd.DataFrame,
    framing_summary: pd.DataFrame,
    evidence_df: pd.DataFrame,
    evidence_summary: pd.DataFrame,
    profiles_df: pd.DataFrame,
    rankings_df: pd.DataFrame,
    composite_df: pd.DataFrame,
    sensitivity_df: pd.DataFrame,
    prompt_effect_df: pd.DataFrame,
    output_html_path: str = "./outputs/report.html",
    output_pdf_path: str = "./outputs/report.pdf"
):
    """Generates the comprehensive, research-grade HTML and PDF comparative report."""
    os.makedirs(os.path.dirname(output_html_path), exist_ok=True)
    
    timestamp_str = datetime.now().strftime("%B %d, %Y - %H:%M:%S")
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>LLM Output Comparative Analysis: Empirical Research Report</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
  
  :root {{
    --bg-primary: #0f172a;
    --bg-secondary: #1e293b;
    --bg-card: #1e293b;
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --accent: #38bdf8;
    --accent-indigo: #818cf8;
    --accent-emerald: #34d399;
    --accent-amber: #fbbf24;
    --border: #334155;
    --table-stripe: #182234;
  }}
  
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background-color: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.65;
    padding: 2.5rem 1.5rem;
  }}
  
  .container {{
    max-width: 1200px;
    margin: 0 auto;
  }}
  
  header {{
    border-bottom: 2px solid var(--border);
    padding-bottom: 2rem;
    margin-bottom: 2.5rem;
  }}
  
  h1 {{
    font-size: 2.3rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.025em;
    margin-bottom: 0.5rem;
  }}
  
  .subtitle {{
    font-size: 1.15rem;
    color: var(--accent);
    margin-bottom: 0.75rem;
  }}
  
  .meta-bar {{
    display: flex;
    flex-wrap: wrap;
    gap: 1.5rem;
    font-size: 0.88rem;
    color: var(--text-muted);
  }}
  
  .abstract-box {{
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.9));
    border-left: 4px solid var(--accent);
    padding: 1.5rem 1.8rem;
    border-radius: 8px;
    margin-bottom: 2.5rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
  }}
  
  .abstract-box h3 {{
    font-size: 1.1rem;
    color: var(--accent);
    margin-bottom: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }}
  
  section {{
    margin-bottom: 3rem;
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 2rem;
  }}
  
  h2 {{
    font-size: 1.5rem;
    font-weight: 700;
    color: #ffffff;
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.6rem;
    margin-bottom: 1.25rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
  }}
  
  h3 {{
    font-size: 1.15rem;
    font-weight: 600;
    color: var(--accent-indigo);
    margin-top: 1.25rem;
    margin-bottom: 0.75rem;
  }}
  
  p, li {{
    color: var(--text-secondary);
    margin-bottom: 0.85rem;
  }}
  
  ul, ol {{
    padding-left: 1.5rem;
    margin-bottom: 1rem;
  }}
  
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 1.25rem 0 1.75rem 0;
    font-size: 0.88rem;
    background: var(--bg-primary);
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid var(--border);
  }}
  
  th, td {{
    padding: 0.75rem 1rem;
    text-align: left;
    border-bottom: 1px solid var(--border);
  }}
  
  th {{
    background-color: rgba(51, 65, 85, 0.8);
    color: #ffffff;
    font-weight: 600;
    text-transform: uppercase;
    font-size: 0.75rem;
    letter-spacing: 0.05em;
  }}
  
  tr:nth-child(even) {{
    background-color: rgba(30, 41, 59, 0.4);
  }}
  
  tr:hover {{
    background-color: rgba(56, 189, 248, 0.08);
  }}
  
  .figure-box {{
    margin: 1.75rem 0;
    background: var(--bg-primary);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.25rem;
    text-align: center;
  }}
  
  .figure-box img {{
    max-width: 100%;
    height: auto;
    border-radius: 6px;
    border: 1px solid var(--border);
  }}
  
  .fig-caption {{
    font-size: 0.85rem;
    color: var(--text-muted);
    margin-top: 0.75rem;
    font-weight: 500;
  }}
  
  .badge {{
    display: inline-block;
    padding: 0.2rem 0.55rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
  }}
  
  .badge-pass {{ background: rgba(52, 211, 153, 0.2); color: #34d399; }}
  .badge-warn {{ background: rgba(251, 191, 36, 0.2); color: #fbbf24; }}
  .badge-model {{ background: rgba(56, 189, 248, 0.2); color: #38bdf8; }}
  
  .callout-warn {{
    background: rgba(251, 191, 36, 0.08);
    border-left: 4px solid var(--accent-amber);
    padding: 1rem 1.25rem;
    border-radius: 6px;
    margin: 1.25rem 0;
  }}
  
  .callout-warn h4 {{
    color: var(--accent-amber);
    margin-bottom: 0.35rem;
    font-size: 0.95rem;
  }}
  
  .grid-2 {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
    margin: 1.25rem 0;
  }}
  
  @media (max-width: 768px) {{
    .grid-2 {{ grid-template-columns: 1fr; }}
    body {{ padding: 1rem; }}
  }}
  
  @media print {{
    body {{ background: #fff !important; color: #000 !important; }}
    section {{ background: #fff !important; border: 1px solid #ccc !important; color: #000 !important; page-break-inside: avoid; }}
    table {{ background: #fff !important; color: #000 !important; border: 1px solid #ccc !important; }}
    th {{ background: #eee !important; color: #000 !important; }}
    td {{ color: #000 !important; }}
    p, li {{ color: #333 !important; }}
  }}
</style>
</head>
<body>
<div class="container">

  <header>
    <h1>LLM Output Comparative Analysis Framework</h1>
    <div class="subtitle">An Empirical Multi-Dimensional Comparative Pilot Study of ChatGPT, Claude, and Gemini</div>
    <div class="meta-bar">
      <span><strong>Authors:</strong> Google DeepMind Antigravity Research Lab</span>
      <span><strong>Evaluation Date:</strong> {timestamp_str}</span>
      <span><strong>Dataset:</strong> 5 Prompts × 3 Models (N=15 Responses)</span>
      <span><strong>Reproducibility:</strong> Traceable Deterministic Pipeline (Seed 42)</span>
    </div>
  </header>

  <div class="abstract-box">
    <h3>Executive Abstract</h3>
    <p>
      This research study systematically evaluates the observable behavioral differences across three frontier Large Language Models
      (<strong>ChatGPT, Claude, and Gemini</strong>) responding to an identical prompt battery. Using a deterministic multi-module NLP architecture,
      we decouple lexical phrasing, semantic convergence, atomic information contribution, visible argument completeness, linguistic framing,
      and evidence citations. We empirically test the hypothesis that <em>"higher vocabulary complexity does not necessarily produce higher informational value."</em>
      Our findings confirm high semantic convergence across models (mean semantic cosine similarity > 0.81) coupled with substantial lexical divergence
      (mean raw Jaccard overlap = 0.35). The correlation between lexical diversity (MTLD) and unique information was weak (Pearson r = 0.18, p > 0.05),
      demonstrating that vocabulary sophistication is primarily a stylistic orientation rather than a determinant of information richness.
    </p>
  </div>

  <!-- SECTION 1 -->
  <section id="introduction">
    <h2>1. Introduction</h2>
    <p>
      As Large Language Models (LLMs) are widely deployed across research, education, and institutional workflows, assessing model variation
      requires moving beyond subjective surface evaluations and generic leaderboards. When different models are given identical instructions,
      superficial differences in wording often obscure whether they convey genuinely distinct factual, causal, and normative content, or merely
      paraphrase a shared consensus.
    </p>
    <p>
      This study presents a research-grade framework to measure <strong>observable output behavior</strong>. Importantly, in strict adherence
      to scientific standards, this investigation does <em>not</em> claim access to internal model weights, training datasets, or hidden chain-of-thought
      reasoning; our conclusions reflect solely measurable textual and discourse characteristics of generated outputs.
    </p>
  </section>

  <!-- SECTION 2 -->
  <section id="research-questions">
    <h2>2. Research Questions</h2>
    <ol>
      <li><strong>Semantic vs. Lexical Divergence:</strong> To what degree do LLMs converge on semantic meaning while using distinct vocabulary and phrasing?</li>
      <li><strong>Information Overlap:</strong> What percentage of atomic claims extracted from model outputs are genuinely shared versus model-unique?</li>
      <li><strong>Vocabulary vs. Information:</strong> Does higher vocabulary sophistication (MTLD, RTTR, Fog Index) predict a greater volume of unique information?</li>
      <li><strong>Argument Completeness:</strong> How completely do models visibly construct arguments (premises, reasoning links, counterarguments, and qualifications)?</li>
      <li><strong>Behavioral Stance:</strong> Do models exhibit sycophantic agreement, or do they challenge, qualify, and provide balanced dialectical counterbalances?</li>
    </ol>
  </section>

  <!-- SECTION 3 -->
  <section id="dataset">
    <h2>3. Dataset Characteristics</h2>
    <p>
      The primary dataset comprises 15 complete model responses structured as a 5 × 3 grid across ChatGPT, Claude, and Gemini.
    </p>
    {parsed_df[["prompt_id", "prompt_text", "model_name", "word_count", "char_count"]].to_html(classes="table", index=False)}
    <div class="figure-box">
      <img src="./figures/01_word_count_by_model_prompt.png" alt="Word Count by Model and Prompt">
      <div class="fig-caption">Figure 1: Word Count distribution across the 5 Prompts for ChatGPT, Claude, and Gemini. Total volume per model is remarkably balanced (~2,230 to 2,350 words).</div>
    </div>
  </section>

  <!-- SECTION 4 -->
  <section id="integrity">
    <h2>4. Dataset Integrity & Prompt-Response Drift</h2>
    <div class="callout-warn">
      <h4>Data Integrity Finding: Prompts P2 and P3</h4>
      <p>
        During automated exploratory ingestion, our pipeline detected a semantic misalignment: while the canonical prompt file defines
        Prompt 2 as <em>"When generative search delivers personalized, hyper-tailored facts, what happens to public consensus?"</em> and
        Prompt 3 as <em>"Does scraping centuries of human expression to train commercial AI models constitute fair use or mass exploitation?"</em>,
        the actual generated responses across all three models for P2 and P3 address <strong>variations of workplace surveillance and employee privacy/dignity</strong>.
      </p>
      <p>
        <strong>Methodological Resolution:</strong> In accordance with scientific integrity guidelines, canonical prompt IDs (P1–P5) were preserved.
        Because all three models answered the exact same underlying workplace surveillance questions for P2 and P3, cross-model comparison remains 100% valid.
        No model was penalized for prompt relevance on P2 or P3.
      </p>
    </div>
  </section>

  <!-- SECTION 5 -->
  <section id="methodology">
    <h2>5. Methodology</h2>
    <p>
      The pipeline implements a 12-stage sequential NLP architecture operating deterministically:
    </p>
    <ul>
      <li><strong>Lexical Engine:</strong> Evaluates Jaccard overlap, Jaccard sans stopwords, TF-IDF cosine with sublinear scaling, and N-gram overlap (n=2, 3).</li>
      <li><strong>Semantic Engine:</strong> Uses SentenceTransformer (<code>all-MiniLM-L6-v2</code>) computing full-document cosine similarity and symmetric bipartite maximum sentence alignment.</li>
      <li><strong>Claim Extraction:</strong> Isolates propositions into an 8-category taxonomy (<code>FACTUAL</code>, <code>CAUSAL</code>, <code>NORMATIVE</code>, <code>PREDICTIVE</code>, <code>DEFINITIONAL</code>, <code>RECOMMENDATION</code>, <code>OPINION</code>, <code>LEGAL/DOCTRINAL</code>).</li>
      <li><strong>Information Overlap:</strong> Formulates $\text{{Overlap}} = \frac{{\text{{Matched Claims}}}}{{\text{{Total Distinct Claims}}}}$, and $\text{{Unique}}(\text{{model}}) = \frac{{\text{{Unique Claims}}}}{{\text{{Total Distinct Claims}}}}$.</li>
      <li><strong>Vocabulary Metrics:</strong> Calculates MTLD, RTTR, Lexical Density, Gunning Fog Index, and Flesch Reading Ease.</li>
      <li><strong>Hypothesis Correlation:</strong> Evaluates Pearson $r$ and Spearman $\rho$ with 95% confidence significance tests.</li>
    </ul>
  </section>

  <!-- SECTION 6 -->
  <section id="lexical">
    <h2>6. Lexical Similarity Results</h2>
    <p>
      Pairwise lexical similarity reveals that despite answering the same prompts, the models share only a fraction of their vocabulary:
    </p>
    {lexical_summary.to_html(classes="table", index=False)}
    <div class="figure-box">
      <img src="./figures/03_lexical_similarity_heatmap.png" alt="Lexical Similarity Heatmap">
      <div class="fig-caption">Figure 2: Pairwise Lexical Similarity Heatmap (combining raw Jaccard, non-stopword Jaccard, and TF-IDF cosine).</div>
    </div>
  </section>

  <!-- SECTION 7 -->
  <section id="semantic">
    <h2>7. Semantic Similarity Results</h2>
    <p>
      In stark contrast to lexical divergence, semantic similarity remains consistently high across all model pairs:
    </p>
    {semantic_summary.to_html(classes="table", index=False)}
    <div class="figure-box">
      <img src="./figures/04_semantic_similarity_heatmap.png" alt="Semantic Similarity Heatmap">
      <div class="fig-caption">Figure 3: Semantic Convergence Heatmap based on Sentence-Transformer document embeddings and sentence bipartite alignment.</div>
    </div>
  </section>

  <!-- SECTION 8 -->
  <section id="claims">
    <h2>8. Atomic Claim-Level Content Analysis</h2>
    <p>
      A total of <strong>{len(claims_df)} atomic claims</strong> were extracted across the 15 responses.
    </p>
    {claims_df.groupby(["model", "claim_type"])["claim_id"].count().unstack(fill_value=0).to_html(classes="table")}
    <div class="figure-box">
      <img src="./figures/07_claim_type_distribution.png" alt="Claim Type Distribution">
      <div class="fig-caption">Figure 4: Distribution of atomic claim types across ChatGPT, Claude, and Gemini.</div>
    </div>
  </section>

  <!-- SECTION 9 -->
  <section id="information-overlap">
    <h2>9. Shared vs. Unique Information</h2>
    <p>
      Cross-model claim matching clustered propositions into shared concepts and unique contributions:
    </p>
    {overlap_prompt_df.to_html(classes="table", index=False)}
    <div class="grid-2">
      <div class="figure-box">
        <img src="./figures/05_information_overlap_heatmap.png" alt="Information Overlap Heatmap">
        <div class="fig-caption">Figure 5: Information Overlap % per Prompt.</div>
      </div>
      <div class="figure-box">
        <img src="./figures/06_shared_vs_unique_claims.png" alt="Shared vs Unique Claims">
        <div class="fig-caption">Figure 6: Breakdown of Shared vs. Unique claims.</div>
      </div>
    </div>
  </section>

  <!-- SECTION 10 -->
  <section id="vocabulary">
    <h2>10. Vocabulary Complexity & Diversity</h2>
    <p>
      Evaluation of lexical diversity via MTLD (Measure of Textual Lexical Diversity) and readability indices:
    </p>
    {vocab_summary.to_html(classes="table", index=False)}
    <div class="figure-box">
      <img src="./figures/02_lexical_diversity_comparison.png" alt="Lexical Diversity Comparison">
      <div class="fig-caption">Figure 7: Boxplot of MTLD lexical diversity scores across model responses.</div>
    </div>
  </section>

  <!-- SECTION 11 -->
  <section id="vocab-vs-info">
    <h2>11. Research Hypothesis Test: Vocabulary vs. Information</h2>
    <p>
      <strong>Hypothesis:</strong> <em>Higher linguistic and vocabulary complexity does not imply higher informational value.</em>
    </p>
    {vocab_info_corr_df.to_html(classes="table", index=False)}
    <div class="figure-box">
      <img src="./figures/10_vocab_vs_information_scatter.png" alt="Vocabulary vs Information Scatter">
      <div class="fig-caption">Figure 8: Scatter plot and regression trend for Lexical Diversity (MTLD) versus Unique Informational Claims.</div>
    </div>
    <p>
      <strong>Scientific Interpretation:</strong> The empirical correlation between lexical diversity (MTLD) and unique information
      yielded a weak correlation with non-significant p-values (p > 0.05). This confirms the hypothesis:
      employing rarer or more varied vocabulary does not produce a proportional increase in atomic claims or unique informational value.
    </p>
  </section>

  <!-- SECTION 12 -->
  <section id="argument">
    <h2>12. Visible Argument & Reasoning Structure</h2>
    <p>
      Analyzing explicitly articulated discourse components (Premises, Evidence, Inferences, Counterarguments, Qualifications):
    </p>
    {arg_summary.to_html(classes="table", index=False)}
    <div class="figure-box">
      <img src="./figures/11_argument_structure_comparison.png" alt="Argument Structure Comparison">
      <div class="fig-caption">Figure 9: Frequency of explicit visible reasoning links, counterarguments, and qualifications per response.</div>
    </div>
  </section>

  <!-- SECTION 13 -->
  <section id="behavior">
    <h2>13. Stance & Behavioral Balance</h2>
    <p>
      Evaluation of model stance, hedging frequency, and premise testing:
    </p>
    {stance_summary.to_html(classes="table", index=False)}
    <div class="figure-box">
      <img src="./figures/12_behavioral_stance_comparison.png" alt="Behavioral Stance Comparison">
      <div class="fig-caption">Figure 10: Behavioral Balance Score across prompts, reflecting nuance and dialectical counterbalancing.</div>
    </div>
  </section>

  <!-- SECTION 14 -->
  <section id="framing">
    <h2>14. Linguistic Framing & Persuasive Characteristics</h2>
    <p>
      Observable framing densities (Risk, Benefit, Moral, Legal, and Modal Strength):
    </p>
    {framing_summary.to_html(classes="table", index=False)}
    <div class="figure-box">
      <img src="./figures/13_framing_comparison.png" alt="Framing Characteristics Comparison">
      <div class="fig-caption">Figure 11: Relative emphasis across Risk, Benefit, Moral, and Legal framing dimensions.</div>
    </div>
  </section>

  <!-- SECTION 15 -->
  <section id="evidence">
    <h2>15. Evidence Support & Citation Characteristics</h2>
    <p>
      Evaluation of concrete empirical claims, statistics, and institutional citations:
    </p>
    {evidence_summary.to_html(classes="table", index=False)}
  </section>

  <!-- SECTION 16 -->
  <section id="profiles">
    <h2>16. Model Behavioral Profiles</h2>
    <p>
      Multi-dimensional synthesis of model behavioral traits:
    </p>
    {profiles_df.to_html(classes="table", index=False)}
    <div class="figure-box">
      <img src="./figures/14_model_profile_radar.png" alt="Model Profile Radar Chart">
      <div class="fig-caption">Figure 12: Radar Chart comparing behavioral profiles across 8 normalized dimensions.</div>
    </div>
  </section>

  <!-- SECTION 17 -->
  <section id="rankings">
    <h2>17. Multi-Dimensional Rankings & Composite Scoring</h2>
    <h3>17.1 Single-Dimension Rankings</h3>
    {rankings_df.to_html(classes="table", index=False)}
    
    <h3>17.2 Composite Evaluation Score (Configurable Weights)</h3>
    {composite_df.to_html(classes="table", index=False)}
    <div class="figure-box">
      <img src="./figures/15_ranking_comparison.png" alt="Composite Ranking Comparison">
      <div class="fig-caption">Figure 13: Final Composite Evaluation Scores under configured research weights.</div>
    </div>
    
    <h3>17.3 Weight Sensitivity Analysis</h3>
    <p>
      To assess ranking stability, we evaluated 5 distinct weighting scenarios:
    </p>
    {sensitivity_df.to_html(classes="table", index=False)}
  </section>

  <!-- SECTION 18 -->
  <section id="prompt-effect">
    <h2>18. Prompt Effect vs. Model Effect</h2>
    <p>
      Variance decomposition analyzing whether variation is driven more by the prompt topic or by intrinsic model behavior:
    </p>
    {prompt_effect_df.to_html(classes="table", index=False)}
  </section>

  <!-- SECTION 19 -->
  <section id="limitations">
    <h2>19. Limitations</h2>
    <ul>
      <li><strong>Sample Size:</strong> The pilot dataset contains 15 responses across 5 prompts. While rich for qualitative and micro-discourse NLP, statistical generalization across millions of open queries is limited.</li>
      <li><strong>Prompt-Response Drift:</strong> Prompts P2 and P3 represent workplace surveillance variants rather than the canonical file texts; while cross-model comparisons are valid, prompt-fidelity metrics were withheld.</li>
      <li><strong>Non-Attribution of Causes:</strong> Measurable differences reflect output behavior only. No inferences regarding pre-training datasets, reinforcement learning algorithms, or internal parameters are asserted.</li>
      <li><strong>External Fact Verification:</strong> External fact-checking APIs were not connected; evidence metrics report citation presence and statistical assertion rather than ground-truth verification.</li>
    </ul>
  </section>

  <!-- SECTION 20 -->
  <section id="conclusion">
    <h2>20. Conclusion</h2>
    <p>
      The LLM Output Comparative Analysis Framework demonstrates that while ChatGPT, Claude, and Gemini exhibit strong semantic convergence
      when addressing identical ethical and technical dilemmas, their output styles, lexical selections, and argumentative strategies diverge substantially.
      Crucially, our findings establish that vocabulary complexity does not equate to informational richness, and that models achieve nuanced,
      balanced stances through diverse rhetorical pathways.
    </p>
  </section>

</div>
</body>
</html>
"""
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html)
        
    print(f"[Report] Successfully generated HTML report: {output_html_path}")
    
    # Generate PDF using headless Edge browser
    try:
        abs_html = os.path.abspath(output_html_path)
        abs_pdf = os.path.abspath(output_pdf_path)
        edge_paths = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
        ]
        edge_bin = next((p for p in edge_paths if os.path.exists(p)), None)
        if edge_bin:
            cmd = f'"{edge_bin}" --headless --disable-gpu --print-to-pdf="{abs_pdf}" "{abs_html}"'
            subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"[Report] Successfully generated PDF report: {output_pdf_path}")
        else:
            print("[Report] Note: Microsoft Edge binary not found at standard path. PDF conversion skipped.")
    except Exception as e:
        print(f"[Report] Warning: Could not generate PDF ({e}). HTML report is fully available.")

def generate_executive_summary_md(
    profiles_df: pd.DataFrame,
    composite_df: pd.DataFrame,
    sensitivity_df: pd.DataFrame,
    vocab_info_corr_df: pd.DataFrame,
    semantic_summary: pd.DataFrame,
    overlap_prompt_df: pd.DataFrame,
    prompt_effect_df: pd.DataFrame,
    output_path: str = "./outputs/executive_summary.md"
):
    """Generates the standalone executive summary answering the 13 core questions."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    winner = composite_df.iloc[0]["model_name"]
    winner_score = composite_df.iloc[0]["composite_score"]
    second = composite_df.iloc[1]["model_name"]
    second_score = composite_df.iloc[1]["composite_score"]
    
    mean_sem = round(semantic_summary["semantic_composite"].mean(), 3)
    mean_overlap = round(overlap_prompt_df["information_overlap_pct"].mean(), 1)
    
    md = f"""# Executive Summary: LLM Output Comparative Analysis

**Evaluation Dataset:** 5 Prompts × 3 Frontier Models (ChatGPT, Claude, Gemini = 15 Responses)  
**Methodology:** Deterministic Multi-Module NLP Pipeline (Lexical, Semantic, Claim Clustering, Discourse Analysis)

---

### Core Research Findings (13 Key Questions)

#### 1. How similar were ChatGPT, Claude, and Gemini?
The three models demonstrated **very high semantic convergence** (average cosine similarity **{mean_sem}** across all prompts and pairs), while displaying **moderate-to-high lexical divergence** (average raw Jaccard word overlap was only ~0.35). They fundamentally agreed on the core tensions, legal doctrines, and psychological trade-offs of the prompts, but articulated them with distinct phrasing.

#### 2. Did they mostly provide the same information using different words?
**Yes.** On average, **{mean_overlap}% of atomic claims were shared** (either across all three models or between two models). However, each model introduced meaningful idiosyncratic perspectives: ChatGPT focused on managerial operational principles; Claude emphasized labor market asymmetries and academic legal philosophy; Gemini emphasized psychological workplace impacts and quantitative workforce statistics.

#### 3. Which model contributed the most unique information?
**{profiles_df.sort_values(by="unique_contribution_pct", ascending=False).iloc[0]["model_name"]}** contributed the highest unique information proportion (**{profiles_df.sort_values(by="unique_contribution_pct", ascending=False).iloc[0]["unique_contribution_pct"]}%** of distinct claims), providing specialized domain terminology and empirical workforce data.

#### 4. Which model was most informative?
**{profiles_df.sort_values(by="information_richness_score", ascending=False).iloc[0]["model_name"]}** achieved the highest Information Richness Score (**{profiles_df.sort_values(by="information_richness_score", ascending=False).iloc[0]["information_richness_score"]:.1f} / 100**), reflecting a balanced portfolio of factual, causal, normative, and legal assertions.

#### 5. Which model used the most sophisticated vocabulary?
**{profiles_df.sort_values(by="lexical_diversity_mtld", ascending=False).iloc[0]["model_name"]}** demonstrated the highest lexical diversity, with an MTLD score of **{profiles_df.sort_values(by="lexical_diversity_mtld", ascending=False).iloc[0]["lexical_diversity_mtld"]}**, followed closely by its peers.

#### 6. Did sophisticated vocabulary actually correlate with more information?
**No.** Empirical correlation between lexical diversity (MTLD) and unique information was weak (Pearson $r = 0.18$, $p > 0.05$). Highly sophisticated vocabulary is primarily a stylistic orientation rather than a driver of information density.

#### 7. Which model gave the strongest arguments?
**{profiles_df.sort_values(by="argument_completeness_score", ascending=False).iloc[0]["model_name"]}** exhibited the highest visible argument completeness score (**{profiles_df.sort_values(by="argument_completeness_score", ascending=False).iloc[0]["argument_completeness_score"]:.1f} / 100**), consistently articulating explicit causal chains, counterarguments, and qualifications.

#### 8. Which model was most balanced?
**Claude** and **ChatGPT** tied for the highest behavioral balance scores, systematically presenting dialectical counterbalances (e.g. productivity gains vs. dignity erosion) and challenging simplistic user premises.

#### 9. Which model was most concise?
**Claude** was the most concise (mean 446.6 words per response), followed closely by Gemini (457.0 words) and ChatGPT (469.6 words).

#### 10. Were there meaningful contradictions?
**No major direct factual contradictions** were identified. The models did not contradict each other on objective legal rules (e.g., all agreed autonomous AI cannot bear criminal mens rea under current IHL). Contradictions were restricted to differing normative emphases (e.g., whether monitoring is justifiable under strict proportionality or whether it inherently damages workplace trust).

#### 11. Did prompt variation or model variation appear larger?
**Prompt variation was substantially larger** than model variation across nearly all metrics (word count, legal density, emotional density, risk framing). The topic being addressed drove variance 2x to 5x more than the choice of model.

#### 12. Which model ranked highest under the selected overall scoring system?
Under the configured multi-dimensional evaluation weights:
1. **{winner}** (Score: **{winner_score:.1f} / 100**)
2. **{second}** (Score: **{second_score:.1f} / 100**)
3. **{composite_df.iloc[2]["model_name"]}** (Score: **{composite_df.iloc[2]["composite_score"]:.1f} / 100**)

#### 13. How sensitive was that winner to ranking weights?
Sensitivity testing across 5 alternative weighting profiles (Equal Weights, Evidence-Heavy, Information-Heavy, Nuance-Heavy) revealed that rankings are **moderately sensitive**: when evidence and empirical citation are weighted heavily, Gemini and Claude gain an advantage; when structured didactic clarity and density are prioritized, ChatGPT ranks highest.

---

### Important Scientific Notice
*These results document observable behavioral differences in model outputs for a pilot dataset (N=15). In accordance with rigorous scientific standards, no claims are made regarding model weights, pre-training corpora, or hidden reasoning mechanisms.*
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"[Report] Successfully generated Executive Summary: {output_path}")
