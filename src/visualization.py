import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from typing import Dict, List, Any

# Aesthetics style
sns.set_theme(style="whitegrid", font="sans-serif")
PALETTE = {"ChatGPT": "#10a37f", "Claude": "#d97706", "Gemini": "#2563eb"}

def save_fig(fig, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    fig.tight_layout()
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close(fig)

def plot_word_count(parsed_df: pd.DataFrame, out_path: str):
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(data=parsed_df, x="prompt_id", y="word_count", hue="model_name", palette=PALETTE, ax=ax)
    ax.set_title("Word Count by Model and Prompt", fontsize=14, weight='bold', pad=12)
    ax.set_xlabel("Prompt ID", fontsize=11, weight='bold')
    ax.set_ylabel("Word Count", fontsize=11, weight='bold')
    ax.legend(title="Model", frameon=True)
    save_fig(fig, out_path)

def plot_lexical_diversity(vocab_df: pd.DataFrame, out_path: str):
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(data=vocab_df, x="model_name", y="mtld", palette=PALETTE, ax=ax, width=0.4)
    sns.stripplot(data=vocab_df, x="model_name", y="mtld", color="black", size=6, jitter=0.1, ax=ax)
    ax.set_title("Lexical Diversity (MTLD) Distribution Across Prompts", fontsize=14, weight='bold', pad=12)
    ax.set_xlabel("Model Name", fontsize=11, weight='bold')
    ax.set_ylabel("MTLD Score (Higher = More Lexically Diverse)", fontsize=11, weight='bold')
    save_fig(fig, out_path)

def plot_similarity_heatmap(sim_df: pd.DataFrame, metric_col: str, title: str, out_path: str):
    models = ["ChatGPT", "Claude", "Gemini"]
    matrix = pd.DataFrame(np.eye(3), index=models, columns=models)
    
    # Fill average pairwise similarities
    for _, row in sim_df.iterrows():
        m1, m2 = row["model_a"], row["model_b"]
        val = row[metric_col]
        matrix.loc[m1, m2] = val
        matrix.loc[m2, m1] = val
        
    fig, ax = plt.subplots(figsize=(7, 5.5))
    sns.heatmap(matrix, annot=True, fmt=".3f", cmap="YlGnBu", vmin=0.3, vmax=1.0, ax=ax, cbar_kws={'label': 'Similarity'})
    ax.set_title(title, fontsize=13, weight='bold', pad=12)
    save_fig(fig, out_path)

def plot_claim_overlap_heatmap(overlap_df: pd.DataFrame, out_path: str):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    p_data = overlap_df[["prompt_id", "information_overlap_pct", "shared_by_all_3", "contradictions"]].set_index("prompt_id")
    sns.heatmap(p_data[["information_overlap_pct"]].T, annot=True, fmt=".1f", cmap="Blues", ax=ax, cbar_kws={'label': 'Overlap %'})
    ax.set_title("Information Overlap Percentage by Prompt", fontsize=13, weight='bold', pad=12)
    ax.set_xlabel("Prompt ID", fontsize=11, weight='bold')
    ax.set_yticklabels(["Information Overlap %"], rotation=0)
    save_fig(fig, out_path)

def plot_shared_vs_unique(overlap_df: pd.DataFrame, out_path: str):
    fig, ax = plt.subplots(figsize=(9, 5))
    df = overlap_df.copy()
    prompts = df["prompt_id"]
    
    p1 = ax.bar(prompts, df["shared_by_all_3"], label="Shared by All 3", color="#10b981")
    p2 = ax.bar(prompts, df["shared_by_2"], bottom=df["shared_by_all_3"], label="Shared by 2", color="#3b82f6")
    bottom_u = df["shared_by_all_3"] + df["shared_by_2"]
    u_tot = df["unique_chatgpt"] + df["unique_claude"] + df["unique_gemini"]
    p3 = ax.bar(prompts, u_tot, bottom=bottom_u, label="Unique Claims", color="#f59e0b")
    
    ax.set_title("Distribution of Shared vs. Unique Claims per Prompt", fontsize=14, weight='bold', pad=12)
    ax.set_xlabel("Prompt ID", fontsize=11, weight='bold')
    ax.set_ylabel("Distinct Claim Count", fontsize=11, weight='bold')
    ax.legend(frameon=True)
    save_fig(fig, out_path)

def plot_claim_types(claims_df: pd.DataFrame, out_path: str):
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.countplot(data=claims_df, x="claim_type", hue="model", palette=PALETTE, ax=ax, order=claims_df["claim_type"].value_counts().index)
    ax.set_title("Claim Type Distribution Across Models", fontsize=14, weight='bold', pad=12)
    ax.set_xlabel("Claim Taxonomy", fontsize=11, weight='bold')
    ax.set_ylabel("Extracted Claims Count", fontsize=11, weight='bold')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=25, ha="right")
    ax.legend(title="Model", frameon=True)
    save_fig(fig, out_path)

def plot_information_richness(richness_df: pd.DataFrame, out_path: str):
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(data=richness_df, x="prompt_id", y="information_richness_score", hue="model_name", palette=PALETTE, ax=ax)
    ax.set_title("Information Richness Score by Prompt", fontsize=14, weight='bold', pad=12)
    ax.set_xlabel("Prompt ID", fontsize=11, weight='bold')
    ax.set_ylabel("Information Richness (0-100)", fontsize=11, weight='bold')
    ax.legend(title="Model", frameon=True)
    save_fig(fig, out_path)

def plot_information_density(richness_df: pd.DataFrame, out_path: str):
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(data=richness_df, x="prompt_id", y="information_density_per_100w", hue="model_name", palette=PALETTE, ax=ax)
    ax.set_title("Information Density (Claims per 100 Words) by Prompt", fontsize=14, weight='bold', pad=12)
    ax.set_xlabel("Prompt ID", fontsize=11, weight='bold')
    ax.set_ylabel("Claims / 100 Words", fontsize=11, weight='bold')
    ax.legend(title="Model", frameon=True)
    save_fig(fig, out_path)

def plot_vocab_vs_info_scatter(vocab_df: pd.DataFrame, richness_df: pd.DataFrame, out_path: str):
    merged = pd.merge(vocab_df, richness_df, on=["prompt_id", "model_name"])
    fig, ax = plt.subplots(figsize=(8, 5.5))
    sns.scatterplot(
        data=merged, x="mtld", y="unique_claims", hue="model_name", 
        style="model_name", palette=PALETTE, s=120, ax=ax
    )
    sns.regplot(data=merged, x="mtld", y="unique_claims", scatter=False, ax=ax, color="grey", line_kws={'linestyle': '--'})
    ax.set_title("Research Hypothesis Test: Vocabulary Complexity (MTLD) vs. Unique Information", fontsize=13, weight='bold', pad=12)
    ax.set_xlabel("Lexical Diversity (MTLD)", fontsize=11, weight='bold')
    ax.set_ylabel("Unique Informational Claims Count", fontsize=11, weight='bold')
    ax.legend(title="Model", frameon=True)
    save_fig(fig, out_path)

def plot_argument_structure(arg_df: pd.DataFrame, out_path: str):
    fig, ax = plt.subplots(figsize=(9, 5))
    summary = arg_df.groupby("model_name")[["reasoning_count", "counterargument_count", "qualification_count", "evidence_count"]].mean().reset_index()
    melted = summary.melt(id_vars="model_name", var_name="Component", value_name="Avg_Count")
    sns.barplot(data=melted, x="Component", y="Avg_Count", hue="model_name", palette=PALETTE, ax=ax)
    ax.set_title("Explicit Argument & Visible Reasoning Components", fontsize=14, weight='bold', pad=12)
    ax.set_xlabel("Argument Component", fontsize=11, weight='bold')
    ax.set_ylabel("Mean Frequency per Response", fontsize=11, weight='bold')
    ax.set_xticklabels(["Reasoning Links", "Counterarguments", "Qualifications", "Evidence References"], rotation=15)
    ax.legend(title="Model", frameon=True)
    save_fig(fig, out_path)

def plot_behavioral_stance(stance_df: pd.DataFrame, out_path: str):
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=stance_df, x="prompt_id", y="behavioral_balance_score", hue="model_name", palette=PALETTE, ax=ax)
    ax.set_title("Behavioral Balance & Nuance Score by Prompt", fontsize=14, weight='bold', pad=12)
    ax.set_xlabel("Prompt ID", fontsize=11, weight='bold')
    ax.set_ylabel("Balance Score (0-100)", fontsize=11, weight='bold')
    ax.legend(title="Model", frameon=True)
    save_fig(fig, out_path)

def plot_framing_comparison(framing_df: pd.DataFrame, out_path: str):
    fig, ax = plt.subplots(figsize=(9, 5))
    summary = framing_df.groupby("model_name")[["risk_framing_density", "benefit_framing_density", "moral_framing_density", "legal_framing_density"]].mean().reset_index()
    melted = summary.melt(id_vars="model_name", var_name="Frame", value_name="Density")
    sns.barplot(data=melted, x="Frame", y="Density", hue="model_name", palette=PALETTE, ax=ax)
    ax.set_title("Linguistic Framing Density (% of Response Words)", fontsize=14, weight='bold', pad=12)
    ax.set_xlabel("Framing Orientation", fontsize=11, weight='bold')
    ax.set_ylabel("Framing Density (%)", fontsize=11, weight='bold')
    ax.set_xticklabels(["Risk/Threat", "Benefit/Gain", "Moral/Dignity", "Legal/Doctrinal"], rotation=15)
    ax.legend(title="Model", frameon=True)
    save_fig(fig, out_path)

def plot_radar_chart(profiles_df: pd.DataFrame, out_path: str):
    labels = [
        "Lexical Diversity", "Semantic Conv.", "Info Richness", 
        "Unique Contrib.", "Info Density", "Argument Qual.", 
        "Evidence Support", "Behavior Balance"
    ]
    num_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
    
    for _, row in profiles_df.iterrows():
        m = row["model_name"]
        # Normalize dimensions on standard scales
        values = [
            min(100.0, row["lexical_diversity_mtld"] / 1.2),
            row["semantic_convergence"] * 100.0,
            row["information_richness_score"],
            min(100.0, row["unique_contribution_pct"] * 2.5),
            min(100.0, row["information_density_per_100w"] * 12.0),
            row["argument_completeness_score"],
            row["evidence_support_score"],
            row["behavioral_balance_score"]
        ]
        values += values[:1]
        ax.plot(angles, values, color=PALETTE.get(m, '#333'), linewidth=2, label=m)
        ax.fill(angles, values, color=PALETTE.get(m, '#333'), alpha=0.15)
        
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels, fontsize=10)
    ax.set_ylim(0, 100)
    ax.set_title("Multi-Dimensional Model Behavioral Profiles", fontsize=14, weight='bold', pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1))
    save_fig(fig, out_path)

def plot_ranking_chart(composite_df: pd.DataFrame, out_path: str):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.barplot(data=composite_df, x="composite_score", y="model_name", palette=PALETTE, ax=ax)
    ax.set_title("Overall Composite Evaluation Score (Configured Weights)", fontsize=14, weight='bold', pad=12)
    ax.set_xlabel("Composite Score (0-100)", fontsize=11, weight='bold')
    ax.set_ylabel("Model", fontsize=11, weight='bold')
    for p in ax.patches:
        width = p.get_width()
        ax.annotate(f'{width:.1f}', (width + 1.0, p.get_y() + p.get_height() / 2.),
                    va='center', fontsize=11, weight='bold')
    ax.set_xlim(0, 105)
    save_fig(fig, out_path)

def generate_all_visualizations(
    parsed_df: pd.DataFrame,
    lexical_summary: pd.DataFrame,
    semantic_summary: pd.DataFrame,
    overlap_df: pd.DataFrame,
    claims_df: pd.DataFrame,
    richness_df: pd.DataFrame,
    vocab_df: pd.DataFrame,
    arg_df: pd.DataFrame,
    stance_df: pd.DataFrame,
    framing_df: pd.DataFrame,
    profiles_df: pd.DataFrame,
    composite_df: pd.DataFrame,
    fig_dir: str = "./outputs/figures"
):
    """Generates all 15 required publication-grade visualizations."""
    os.makedirs(fig_dir, exist_ok=True)
    
    plot_word_count(parsed_df, os.path.join(fig_dir, "01_word_count_by_model_prompt.png"))
    plot_lexical_diversity(vocab_df, os.path.join(fig_dir, "02_lexical_diversity_comparison.png"))
    plot_similarity_heatmap(lexical_summary, "lexical_composite", "Lexical Similarity Heatmap (TF-IDF & Jaccard)", os.path.join(fig_dir, "03_lexical_similarity_heatmap.png"))
    plot_similarity_heatmap(semantic_summary, "semantic_composite", "Semantic Convergence Heatmap (Embeddings)", os.path.join(fig_dir, "04_semantic_similarity_heatmap.png"))
    plot_claim_overlap_heatmap(overlap_df, os.path.join(fig_dir, "05_information_overlap_heatmap.png"))
    plot_shared_vs_unique(overlap_df, os.path.join(fig_dir, "06_shared_vs_unique_claims.png"))
    plot_claim_types(claims_df, os.path.join(fig_dir, "07_claim_type_distribution.png"))
    plot_information_richness(richness_df, os.path.join(fig_dir, "08_information_richness_comparison.png"))
    plot_information_density(richness_df, os.path.join(fig_dir, "09_information_density_comparison.png"))
    plot_vocab_vs_info_scatter(vocab_df, richness_df, os.path.join(fig_dir, "10_vocab_vs_information_scatter.png"))
    plot_argument_structure(arg_df, os.path.join(fig_dir, "11_argument_structure_comparison.png"))
    plot_behavioral_stance(stance_df, os.path.join(fig_dir, "12_behavioral_stance_comparison.png"))
    plot_framing_comparison(framing_df, os.path.join(fig_dir, "13_framing_comparison.png"))
    plot_radar_chart(profiles_df, os.path.join(fig_dir, "14_model_profile_radar.png"))
    plot_ranking_chart(composite_df, os.path.join(fig_dir, "15_ranking_comparison.png"))
    print("[Visualization] Successfully generated all 15 publication-grade figures.")
