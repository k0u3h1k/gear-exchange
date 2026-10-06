import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import re
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

class SemanticAnalyzer:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", cache_dir: str = "./.cache/embeddings"):
        self.model_name = model_name
        self.cache_dir = cache_dir
        self.encoder = None
        self.is_fallback = False
        self._init_encoder()
        
    def _init_encoder(self):
        try:
            from sentence_transformers import SentenceTransformer
            print(f"[SemanticAnalyzer] Loading SentenceTransformer: {self.model_name}...")
            try:
                self.encoder = SentenceTransformer(self.model_name, local_files_only=True)
            except Exception:
                self.encoder = SentenceTransformer(self.model_name)
            print("[SemanticAnalyzer] SentenceTransformer loaded successfully.")
        except Exception as e:
            print(f"[SemanticAnalyzer] Warning: Could not load {self.model_name} ({e}). Using robust TF-IDF fallback.")
            self.is_fallback = True

    def split_sentences(self, text: str) -> List[str]:
        # Split on sentence boundaries, keeping meaningful sentences
        raw = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9*#])', text)
        sents = []
        for s in raw:
            cleaned = re.sub(r'^[#*\s-]+', '', s).strip()
            # remove markdown citation marks
            cleaned = re.sub(r'\[.*?\](\[.*?\])?', '', cleaned).strip()
            if len(cleaned.split()) >= 3:
                sents.append(cleaned)
        return sents if sents else [text.strip()]

    def encode(self, texts: List[str]) -> np.ndarray:
        if not self.is_fallback and self.encoder is not None:
            return self.encoder.encode(texts, show_progress_bar=False, normalize_embeddings=True)
        else:
            vec = TfidfVectorizer(token_pattern=r'\b[a-zA-Z0-9_\'-]+\b', stop_words='english')
            tfidf = vec.fit_transform(texts)
            norms = np.linalg.norm(tfidf.toarray(), axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            return tfidf.toarray() / norms

    def compute_full_response_similarity(self, text_a: str, text_b: str) -> float:
        emb = self.encode([text_a, text_b])
        return float(cosine_similarity([emb[0]], [emb[1]])[0, 0])

    def compute_sentence_alignment(self, sents_a: List[str], sents_b: List[str]) -> Tuple[float, float, float]:
        """Computes symmetric sentence alignment and mean sentence similarity."""
        if not sents_a or not sents_b:
            return 0.0, 0.0, 0.0
            
        emb_a = self.encode(sents_a)
        emb_b = self.encode(sents_b)
        
        sim_matrix = cosine_similarity(emb_a, emb_b)
        
        # Best matches A -> B
        max_a_to_b = np.max(sim_matrix, axis=1)
        mean_a_to_b = float(np.mean(max_a_to_b))
        
        # Best matches B -> A
        max_b_to_a = np.max(sim_matrix, axis=0)
        mean_b_to_a = float(np.mean(max_b_to_a))
        
        # Symmetric Bipartite Alignment
        symmetric_alignment = 0.5 * (mean_a_to_b + mean_b_to_a)
        overall_mean_sim = float(np.mean(sim_matrix))
        
        return round(symmetric_alignment, 4), round(overall_mean_sim, 4), round(mean_a_to_b, 4)

    def analyze_pair(self, text_a: str, text_b: str) -> Dict[str, float]:
        full_sim = round(self.compute_full_response_similarity(text_a, text_b), 4)
        sents_a = self.split_sentences(text_a)
        sents_b = self.split_sentences(text_b)
        sym_align, mean_sent_sim, _ = self.compute_sentence_alignment(sents_a, sents_b)
        
        # Combined Semantic Convergence
        composite_semantic = round(0.5 * full_sim + 0.5 * sym_align, 4)
        
        return {
            "full_response_cosine": full_sim,
            "sentence_symmetric_alignment": sym_align,
            "mean_sentence_similarity": mean_sent_sim,
            "semantic_composite": composite_semantic,
            "sent_count_a": len(sents_a),
            "sent_count_b": len(sents_b),
            "is_fallback": self.is_fallback
        }

def compute_all_semantic_similarities(df: pd.DataFrame, analyzer: SemanticAnalyzer) -> Tuple[pd.DataFrame, pd.DataFrame]:
    records = []
    prompts = sorted(df["prompt_id"].unique())
    models = sorted(df["model_name"].unique())
    
    for p_id in prompts:
        sub = df[df["prompt_id"] == p_id]
        model_texts = {row["model_name"]: row["response_text"] for _, row in sub.iterrows()}
        
        for i in range(len(models)):
            for j in range(i + 1, len(models)):
                m_a, m_b = models[i], models[j]
                if m_a in model_texts and m_b in model_texts:
                    res = analyzer.analyze_pair(model_texts[m_a], model_texts[m_b])
                    records.append({
                        "prompt_id": p_id,
                        "model_a": m_a,
                        "model_b": m_b,
                        **res
                    })
                    
    results_df = pd.DataFrame(records)
    
    # Model-pair averages across all prompts
    summary_df = results_df.groupby(["model_a", "model_b"])[[
        "full_response_cosine", "sentence_symmetric_alignment", 
        "mean_sentence_similarity", "semantic_composite"
    ]].mean().reset_index()
    summary_df = summary_df.round(4)
    
    return results_df, summary_df
