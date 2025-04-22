
import sys, os
from llm_extract import extract_transactions
from utils import normalize_and_save

def main(pdf_path):
    print(f"[parse] LLM‑extracting {pdf_path}…")
    df = extract_transactions(pdf_path)
    print("[parse] Extracted DataFrame shape:", df.shape)
    print("[parse] Extracted DataFrame columns:", df.columns.tolist())
    print("[parse] First few rows:\n", df.head())

     Ensure df is a DataFrame and has all required columns
    import pandas as pd
    required_columns = ['date', 'description', 'amount', 'type']
    if not isinstance(df, pd.DataFrame):
        print("[parse] ERROR: extract_transactions did not return a DataFrame!")
        sys.exit(1)
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        print(f"[parse] ERROR: Extracted DataFrame missing columns: {missing_cols}")
        sys.exit(1)

     Drop rows missing any required field
    before_drop = len(df)
    df_clean = df.dropna(subset=required_columns)
    dropped = before_drop - len(df_clean)
    if dropped > 0:
        print(f"[parse] WARNING: Dropping {dropped} rows missing required fields.")
    df = df_clean
    print("[parse] DataFrame after dropping missing fields:", df.shape)

    if df.empty:
        print("[parse] ERROR: no transactions after dropping missing fields")
        sys.exit(1)

     Convert date column to string for regex validation
    df['date'] = df['date'].astype(str)

     Filter out rows with invalid dates
    import re
    def is_valid_date(date_str):
        return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", str(date_str)))
    invalid_dates = df[~df['date'].apply(is_valid_date)]
    if not invalid_dates.empty:
        print(f"[parse] WARNING: Dropping {len(invalid_dates)} rows with invalid dates:")
        print(invalid_dates[['date', 'description']])
    df = df[df['date'].apply(is_valid_date)]
    print("[parse] DataFrame after date validation:", df.shape)

     If df is now empty, exit gracefully
    if df.empty:
        print("[parse] ERROR: all rows dropped after date validation")
        sys.exit(1)

     Dedupe by (date, description, abs(amount)), robust to non-string/missing description and non-numeric amount
    import pandas as pd
    df['key'] = df.apply(
        lambda r: (
            r.date,
            str(r.description).strip() if not pd.isna(r.description) else "",
            abs(float(r.amount)) if not pd.isna(r.amount) else 0.0
        ),
        axis=1
    )
    df = df.drop_duplicates('key').drop(columns='key')
    print(f"[parse] {len(df)} unique transactions")
    normalize_and_save(df, os.path.basename(pdf_path))
    print("[parse] Done.")

if __name__=="__main__":
    if len(sys.argv)!=2:
        print("Usage: python parse.py <pdf>")
        sys.exit(1)
    main(sys.argv[1])
