# bank-ml-mvp/worker/llm_extract.py
import pdfplumber, pandas as pd
import openai
import os

openai_api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=openai_api_key)

def read_lines(pdf_path):
    lines = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            lines += page.extract_text().splitlines()
    return lines

def make_chunks(lines, window=40, overlap=10):
    for i in range(0, len(lines), window-overlap):
        yield lines[i:i+window]

def parse_chunk_with_llm(chunk):
    prompt = f"""
    You are given this snippet of a bank statement (up to ~50 lines).
    Extract every transaction as a JSON array of objects with keys:
      - date (must be strictly in the format YYYY-MM-DD, e.g., 2019-12-31; skip if not present or not in this format)
      - description (string)
      - amount (must be a number, signed float, negative for debits)
      - type (must be either "debit" or "credit" as a string, nothing else)
    If the original shows two columns Debit/Credit (one blank), treat blank as zero.
    IMPORTANT: Only include transactions where the date is a valid YYYY-MM-DD. If the date is not in this format, skip that transaction.
    Output ONLY valid JSON (no markdown, no explanation, no code fences), just the array.
    Snippet:
    {'\n'.join(chunk)}
    """
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return resp.choices[0].message.content

from io import StringIO
import json
import re

def strip_code_fences(s):
    """Remove markdown code fences (``` or ```json) from a string."""
    s = s.strip()
    if s.startswith('```'):
        s = re.sub(r'^```[a-zA-Z0-9]*\s*\n?', '', s)
        s = re.sub(r'\n?```$', '', s)
    return s.strip()

def extract_transactions(pdf_path):
    lines = read_lines(pdf_path)
    all_txs = []
    for chunk in make_chunks(lines):
        raw_json = parse_chunk_with_llm(chunk)
        cleaned = strip_code_fences(raw_json)
        if not cleaned or not cleaned.strip():
            print("[parse] WARNING: LLM returned empty output for a chunk")
            continue
        try:
            json.loads(cleaned)
            txs = pd.read_json(StringIO(cleaned))
            all_txs.append(txs)
        except Exception as e:
            print(f"[parse] ERROR: Failed to parse chunk as JSON: {e}")
            print(f"[parse] Raw output: {raw_json}")
            continue
    if not all_txs:
        return pd.DataFrame()
    return pd.concat(all_txs, ignore_index=True)
