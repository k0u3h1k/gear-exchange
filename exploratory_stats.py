import os
import re
import math
from collections import Counter

data_dir = r"c:\Users\sumiy\OneDrive\Desktop\academic_codes\LCT\gear-exchange"
files = [f for f in os.listdir(data_dir) if not f.startswith('.')]

# Prompt detection
prompt_candidates = [f for f in files if "prompt" in f.lower() or ("chat" not in f.lower() and "claude" not in f.lower() and "gemini" not in f.lower())]
p_file = prompt_candidates[0]
with open(os.path.join(data_dir, p_file), "r", encoding="utf-8") as f:
    prompts = [line.strip() for line in f if line.strip()]

# Model files
model_files = [f for f in files if f not in prompt_candidates]
header_pattern = re.compile(r'^\s*(?:chatgpt|claude|gemini|grmini)\s*[-_]?\s*(\d+)[\s:-]*', re.IGNORECASE | re.MULTILINE)

records = []
for mf in sorted(model_files):
    base_name = "ChatGPT" if "chat" in mf.lower() else "Claude" if "claude" in mf.lower() else "Gemini"
    with open(os.path.join(data_dir, mf), "r", encoding="utf-8") as f:
        text = f.read()
    matches = list(header_pattern.finditer(text))
    for idx, match in enumerate(matches):
        p_num = int(match.group(1))
        start_idx = match.end()
        end_idx = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        resp_text = text[start_idx:end_idx].strip()
        words = re.findall(r'\b[a-zA-Z0-9_\'-]+\b', resp_text.lower())
        sentences = [s.strip() for s in re.split(r'[.!?]+(?:\s+|\n+)', resp_text) if s.strip()]
        paragraphs = [p.strip() for p in resp_text.split('\n\n') if p.strip()]
        
        records.append({
            "prompt_id": p_num,
            "prompt_text": prompts[p_num - 1] if p_num <= len(prompts) else "UNKNOWN",
            "model_name": base_name,
            "raw_header": match.group(0).strip(),
            "char_count": len(resp_text),
            "word_count": len(words),
            "vocab_size": len(set(words)),
            "sentence_count": len(sentences),
            "paragraph_count": len(paragraphs),
            "ttr": len(set(words)) / max(1, len(words)),
            "first_60": resp_text.replace('\n', ' ')[:60]
        })

print("=== PARSED RECORD SUMMARY ===")
print(f"{'Prompt':<8}{'Model':<10}{'Words':<8}{'Chars':<8}{'Vocab':<8}{'TTR':<8}{'Sentences':<10}{'Header Match'}")
print("-" * 80)
for r in sorted(records, key=lambda x: (x['prompt_id'], x['model_name'])):
    print(f"P{r['prompt_id']:<7}{r['model_name']:<10}{r['word_count']:<8}{r['char_count']:<8}{r['vocab_size']:<8}{r['ttr']:.3f}   {r['sentence_count']:<10}{r['raw_header']}")

print("\n=== AGGREGATE PER MODEL ===")
for model in ["ChatGPT", "Claude", "Gemini"]:
    m_records = [r for r in records if r['model_name'] == model]
    tot_words = sum(r['word_count'] for r in m_records)
    avg_words = tot_words / len(m_records)
    all_words = []
    for r in m_records:
        # re-extract
        pass
    print(f"{model}: Total Words = {tot_words}, Mean Words/Response = {avg_words:.1f}, Responses = {len(m_records)}/5")

print("\n=== AGGREGATE PER PROMPT ===")
for p_idx in range(1, 6):
    p_records = [r for r in records if r['prompt_id'] == p_idx]
    tot_words = sum(r['word_count'] for r in p_records)
    models_present = [r['model_name'] for r in p_records]
    print(f"Prompt {p_idx}: Total Words = {tot_words}, Models = {models_present}")
