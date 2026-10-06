import os
import re

data_dir = r"c:\Users\sumiy\OneDrive\Desktop\academic_codes\LCT\gear-exchange"
files = [f for f in os.listdir(data_dir) if not f.startswith('.')]
print("Files in directory:", files)

# Detect prompts file
prompt_candidates = [f for f in files if "prompt" in f.lower() or ("chat" not in f.lower() and "claude" not in f.lower() and "gemini" not in f.lower())]
print("Prompt candidate files:", prompt_candidates)

prompts = []
if prompt_candidates:
    p_file = prompt_candidates[0]
    p_path = os.path.join(data_dir, p_file)
    with open(p_path, "r", encoding="utf-8") as f:
        prompts = [line.strip() for line in f if line.strip()]
    print(f"\n--- Detected {len(prompts)} Prompts from '{p_file}' ---")
    for i, p in enumerate(prompts, 1):
        print(f"[{i}] {p}")

model_files = [f for f in files if f not in prompt_candidates]
print(f"\n--- Detected {len(model_files)} Model Files ---", model_files)

# Split pattern for model responses
# Matches headers like: "Chatgpt-1:", " Chatgpt-2:", "Chatgpt3:", "chatgpt4:", "chatgpt 5:-"
header_pattern = re.compile(r'^\s*(?:chatgpt|claude|gemini|grmini)\s*[-_]?\s*(\d+)[\s:-]*', re.IGNORECASE | re.MULTILINE)

dataset = []
for mf in model_files:
    m_path = os.path.join(data_dir, mf)
    with open(m_path, "r", encoding="utf-8") as f:
        text = f.read()
    
    # Infer base model name
    base_name = mf.split("-")[0].capitalize()
    if "chat" in mf.lower():
        base_name = "ChatGPT"
    elif "claude" in mf.lower():
        base_name = "Claude"
    elif "gemini" in mf.lower():
        base_name = "Gemini"

    # Find all matches
    matches = list(header_pattern.finditer(text))
    print(f"\nModel file: {mf} -> Identified as {base_name}. Header matches found: {len(matches)}")
    
    for idx, match in enumerate(matches):
        p_num = int(match.group(1))
        start_idx = match.end()
        end_idx = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        resp_text = text[start_idx:end_idx].strip()
        word_count = len(resp_text.split())
        char_count = len(resp_text)
        first_sentence = resp_text.split("\n")[0][:80]
        
        print(f"  Item {idx+1}: Prompt ID={p_num} | Header='{match.group(0).strip()}' | Words={word_count} | Chars={char_count}")
        print(f"    Preview: {first_sentence}...")
        
        prompt_str = prompts[p_num - 1] if p_num <= len(prompts) else "UNKNOWN_PROMPT"
        dataset.append({
            "prompt_id": p_num,
            "prompt_text": prompt_str,
            "model_name": base_name,
            "response_text": resp_text,
            "word_count": word_count,
            "char_count": char_count
        })

print(f"\nTotal parsed responses: {len(dataset)}")
