import os
import pandas as pd
import psycopg2

 Database connection string: override via environment variable if needed
db_conn = os.getenv(
    'DB_CONN',
    "dbname=bank_ml_mvp user=bank_user password=your_strong_password"
)


def normalize_and_save(df: pd.DataFrame, statement_name: str) -> None:
    """
    Normalize the LLM-extracted transactions DataFrame and write into transactions_raw.

    Expected columns in df:
      - date: datetime.date
      - description: str
      - amount: float
      - type: str ("debit" or "credit")

    Rows with null date or amount are skipped. Duplicates are ignored via DB constraint.
    """
     Ensure required columns exist
    expected_cols = {'date', 'description', 'amount', 'type'}
    missing = expected_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns for normalization: {missing}")

     Connect to Postgres\    
    conn = psycopg2.connect(db_conn)
    cur = conn.cursor()

    for _, row in df.iterrows():
        date = row['date']
        desc = row['description']
        amount = row['amount']
        tx_type = str(row['type']).strip().lower()

         Skip invalid rows
        if pd.isna(date) or pd.isna(amount):
            continue

         Convert type to boolean: credit=True, debit=False
        debit_credit = True if tx_type == 'credit' else False

         Insert into DB; assume a unique constraint avoids duplicates
        cur.execute(
            """
            INSERT INTO transactions_raw(
              statement_name, date, description, debit_credit, amount
            ) VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
            """,
            (statement_name, date, desc, debit_credit, amount)
        )

    conn.commit()
    cur.close()
    conn.close()
