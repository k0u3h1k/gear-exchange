import re
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Set
from sklearn.feature_extraction.text import TfidfVectorizer

STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
    "during", "each", "few", "for", "from", "further", "had", "hadn't", "has",
    "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her",
    "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's",
    "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it",
    "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other",
    "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't",
    "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then",
    "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've",
    "this", "those", "through", "to", "too", "under", "until", "up", "very", "was",
    "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what",
    "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's",
    "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd",
    "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"
}

def get_tokens(text: str) -> List[str]:
    return re.findall(r'\b[a-zA-Z0-9_\'-]+\b', text.lower())

def get_ngrams(tokens: List[str], n: int) -> Set[Tuple[str, ...]]:
    if len(tokens) < n:
        return set()
    return {tuple(tokens[i:i+n]) for i in range(len(tokens) - n + 1)}

def jaccard_similarity(set_a: Set, set_b: Set) -> float:
    if not set_a and not set_b:
        return 1.0
    if not set_a or not set_b:
        return 0.0
    return len(set_a.intersection(set_b)) / len(set_a.union(set_b))

def calculate_pairwise_lexical(text_a: str, text_b: str) -> Dict[str, float]:
    tokens_a = get_tokens(text_a)
    tokens_b = get_tokens(text_b)
    
    set_a = set(tokens_a)
    set_b = set(tokens_b)
    
    set_a_nostop = {w for w in set_a if w not in STOPWORDS}
    set_b_nostop = {w for w in set_b if w not in STOPWORDS}
    
    bigrams_a = get_ngrams(tokens_a, 2)
    bigrams_b = get_ngrams(tokens_b, 2)
    
    trigrams_a = get_ngrams(tokens_a, 3)
    trigrams_b = get_ngrams(tokens_b, 3)
    
    # TF-IDF Cosine
    vectorizer = TfidfVectorizer(token_pattern=r'\b[a-zA-Z0-9_\'-]+\b', stop_words='english')
    try:
        tfidf_mat = vectorizer.fit_transform([text_a, text_b])
        tfidf_sim = float((tfidf_mat * tfidf_mat.T).toarray()[0, 1])
    except Exception:
        tfidf_sim = 0.0
        
    return {
        "jaccard_raw": round(jaccard_similarity(set_a, set_b), 4),
        "jaccard_no_stopwords": round(jaccard_similarity(set_a_nostop, set_b_nostop), 4),
        "tfidf_cosine": round(tfidf_sim, 4),
        "bigram_overlap": round(jaccard_similarity(bigrams_a, bigrams_b), 4),
        "trigram_overlap": round(jaccard_similarity(trigrams_a, trigrams_b), 4),
        "lexical_composite": round(
            0.3 * jaccard_similarity(set_a, set_b) +
            0.3 * jaccard_similarity(set_a_nostop, set_b_nostop) +
            0.4 * tfidf_sim, 4
        )
    }

def compute_all_lexical_similarities(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Computes pairwise lexical similarities for all prompts and model pairs."""
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
                    sims = calculate_pairwise_lexical(model_texts[m_a], model_texts[m_b])
                    records.append({
                        "prompt_id": p_id,
                        "model_a": m_a,
                        "model_b": m_b,
                        **sims
                    })
                    
    results_df = pd.DataFrame(records)
    
    # Model-pair averages
    summary_df = results_df.groupby(["model_a", "model_b"])[[
        "jaccard_raw", "jaccard_no_stopwords", "tfidf_cosine", 
        "bigram_overlap", "trigram_overlap", "lexical_composite"
    ]].mean().reset_index()
    summary_df = summary_df.round(4)
    
    return results_df, summary_df
