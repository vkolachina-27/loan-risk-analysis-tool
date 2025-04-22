 scripts/category_distribution.py
import psycopg2
import pandas as pd

conn = psycopg2.connect("dbname=bank_ml_mvp user=bank_user password=your_strong_password")
query = """
SELECT category, COUNT(*) AS freq
FROM transactions_labeled
GROUP BY category
ORDER BY freq DESC;
"""
df = pd.read_sql(query, conn)
conn.close()
print("Current category distribution:")
print(df.to_string(index=False))
