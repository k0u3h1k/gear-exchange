import os
import re
import pandas as pd
from typing import List, Dict, Tuple, Any

def discover_dataset_files(input_dir: str, fallback_dir: str = "./data") -> Tuple[str, List[str]]:
    """Discovers the prompt file and model response files."""
    target_dir = input_dir if os.path.exists(input_dir) else fallback_dir
    if not os.path.exists(target_dir):
        raise FileNotFoundError(f"Neither input directory '{input_dir}' nor fallback '{fallback_dir}' exists.")
        
    all_files = [f for f in os.listdir(target_dir) if not f.startswith('.')]
    
    # Identify prompt file
    prompt_file = None
    for f in all_files:
        lower = f.lower()
        if "prompt" in lower:
            prompt_file = os.path.join(target_dir, f)
            break
            
    if not prompt_file:
        # Check non-model txt files
        candidates = [
            f for f in all_files 
            if f.endswith('.txt') and not any(m in f.lower() for m in ['chatgpt', 'claude', 'gemini'])
        ]
        if candidates:
            prompt_file = os.path.join(target_dir, candidates[0])
            
    if not prompt_file:
        raise FileNotFoundError(f"Could not automatically identify prompts file in {target_dir}.")
        
    model_files = [
        os.path.join(target_dir, f) for f in all_files
        if f.endswith('.txt') and os.path.join(target_dir, f) != prompt_file
    ]
    
    if not model_files:
        raise FileNotFoundError(f"No model output text files found in {target_dir}.")
        
    return prompt_file, sorted(model_files)

def parse_prompts(prompt_file_path: str) -> Dict[int, str]:
    """Reads prompt file into a dictionary of {prompt_id: prompt_text}."""
    with open(prompt_file_path, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]
    return {idx + 1: text for idx, text in enumerate(lines)}

def clean_text_for_lexical(text: str) -> str:
    """Preprocesses text for lexical analysis while retaining clean tokens."""
    # Remove markdown links, symbols, lowercase
    t = re.sub(r'\[.*?\]\(.*?\)', ' ', text)
    t = re.sub(r'\[[A-Z0-9_-]+\]\[\d+\]', ' ', t) # Citation placeholders like [DOI][1]
    t = re.sub(r'[#*`_~>|]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip().lower()
    return t

def parse_dataset(input_dir: str, fallback_dir: str = "./data", drift_prompts: List[int] = None) -> pd.DataFrame:
    """Parses prompts and model files into a structured pandas DataFrame."""
    if drift_prompts is None:
        drift_prompts = [2, 3]
        
    prompt_file, model_files = discover_dataset_files(input_dir, fallback_dir)
    prompts_map = parse_prompts(prompt_file)
    
    # Regex that flexibly matches headers like:
    # "Chatgpt-1:", " Chatgpt-2:", "Chatgpt3:", "chatgpt4:", "chatgpt 5:-", "Grmini-3:", "Gemini-1 "
    header_pattern = re.compile(
        r'^\s*(?:chatgpt|claude|gemini|grmini)\s*[-_]?\s*(\d+)[\s:-]*', 
        re.IGNORECASE | re.MULTILINE
    )
    
    records = []
    
    for mf in model_files:
        fname = os.path.basename(mf)
        base_name = "ChatGPT" if "chat" in fname.lower() else "Claude" if "claude" in fname.lower() else "Gemini"
        
        with open(mf, "r", encoding="utf-8") as f:
            content = f.read()
            
        matches = list(header_pattern.finditer(content))
        if matches:
            # Multi-section file
            for idx, match in enumerate(matches):
                p_num = int(match.group(1))
                start_pos = match.end()
                end_pos = matches[idx + 1].start() if idx + 1 < len(matches) else len(content)
                resp_text = content[start_pos:end_pos].strip()
                
                clean_text = clean_text_for_lexical(resp_text)
                words = re.findall(r'\b[a-zA-Z0-9_\'-]+\b', resp_text.lower())
                
                records.append({
                    "prompt_id": p_num,
                    "prompt_text": prompts_map.get(p_num, f"Prompt {p_num}"),
                    "model_name": base_name,
                    "raw_header": match.group(0).strip(),
                    "response_text": resp_text,
                    "clean_text": clean_text,
                    "word_count": len(words),
                    "char_count": len(resp_text),
                    "is_drift_flagged": p_num in drift_prompts
                })
        else:
            # Single prompt file e.g. ChatGPT-1.txt
            m_num = re.search(r'[-_](\d+)', fname)
            p_num = int(m_num.group(1)) if m_num else 1
            clean_text = clean_text_for_lexical(content)
            words = re.findall(r'\b[a-zA-Z0-9_\'-]+\b', content.lower())
            records.append({
                "prompt_id": p_num,
                "prompt_text": prompts_map.get(p_num, f"Prompt {p_num}"),
                "model_name": base_name,
                "raw_header": "FILE_LEVEL",
                "response_text": content.strip(),
                "clean_text": clean_text,
                "word_count": len(words),
                "char_count": len(content),
                "is_drift_flagged": p_num in drift_prompts
            })
            
    df = pd.DataFrame(records)
    # Sort logically
    df = df.sort_values(by=["prompt_id", "model_name"]).reset_index(drop=True)
    return df
