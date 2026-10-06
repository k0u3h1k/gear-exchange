import pytest
import os
import pandas as pd
from src.parser import parse_dataset, clean_text_for_lexical

def test_dataset_parsing_dimensions():
    df = parse_dataset(input_dir="./gear-exchange", fallback_dir="./data")
    assert len(df) == 15, f"Expected 15 responses, got {len(df)}"
    assert set(df["model_name"].unique()) == {"ChatGPT", "Claude", "Gemini"}
    assert set(df["prompt_id"].unique()) == {1, 2, 3, 4, 5}

def test_clean_text_for_lexical():
    raw = "Here is a **bold** statement with a [citation][1] and # headers!"
    cleaned = clean_text_for_lexical(raw)
    assert "bold" in cleaned
    assert "statement" in cleaned
    assert "**" not in cleaned
    assert "#" not in cleaned

def test_missing_directory_error():
    with pytest.raises(FileNotFoundError):
        parse_dataset(input_dir="./non_existent_dir_12345", fallback_dir="./also_non_existent")
