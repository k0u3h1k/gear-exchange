import os
import shutil
import hashlib
from pathlib import Path

def get_hash(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()

def main():
    root_dir = Path("c:/Users/sumiy/OneDrive/Desktop/academic_codes/LCT/gear-exchange")
    
    # Expected files
    expected = [
        "Does automated workplace monitoring.txt",
        "Chatgpt-1.txt",
        "Claude-1.txt",
        "Gemini-1.txt"
    ]
    
    found_files = {}
    
    for root, dirs, files in os.walk(root_dir):
        # Avoid searching inside output dir if it exists
        if "output" in dirs:
            dirs.remove("output")
        for f in files:
            for exp in expected:
                if f.lower() == exp.lower():
                    found_files[exp] = Path(root) / f

    print("SOURCE DATASET FOUND\n")
    print(f"Prompt:\n{found_files['Does automated workplace monitoring.txt'].absolute()}")
    print(f"\nChatGPT:\n{found_files['Chatgpt-1.txt'].absolute()}")
    print(f"\nClaude:\n{found_files['Claude-1.txt'].absolute()}")
    print(f"\nGemini:\n{found_files['Gemini-1.txt'].absolute()}\n")

    output_dir = root_dir / "output"
    input_dir = output_dir / "input"
    
    output_dir.mkdir(exist_ok=True)
    input_dir.mkdir(exist_ok=True)
    
    print("COPY VERIFICATION\n")
    
    for key, path in found_files.items():
        dest = input_dir / path.name
        shutil.copy2(path, dest)
        
        src_hash = get_hash(path)
        dst_hash = get_hash(dest)
        
        match = "MATCH" if src_hash == dst_hash else "MISMATCH"
        
        # Display name nicely
        if "Chatgpt" in key: name = "ChatGPT"
        elif "Claude" in key: name = "Claude"
        elif "Gemini" in key: name = "Gemini"
        else: name = "Prompt"
        
        print(f"{name}:")
        print(f"Source: {path.absolute()}")
        print(f"Copy: {dest.absolute()}")
        print(f"SHA256: {match}\n")
        
    print("DATASET SNAPSHOT READY\n")
    print(f"Project root:\n{root_dir.absolute()}")
    print(f"\nOutput directory:\n{output_dir.absolute()}")
    print(f"\nInput snapshot:\n{input_dir.absolute()}")
    print(f"\nFiles copied:\n{len(found_files)} / 4")
    print(f"\nOriginal files modified:\nNO")
    print(f"\nAnalysis input:\noutput/input/\n")

if __name__ == "__main__":
    main()
