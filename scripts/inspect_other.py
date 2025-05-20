import psycopg2
import pandas as pd

conn = psycopg2.connect("dbname=bank_ml_mvp user=bank_user password=your_strong_password")
query = """
  SELECT r.description, COUNT(*) AS freq
  FROM transactions_raw r
  JOIN transactions_labeled l ON r.id=l.id
  WHERE l.category='Other'
  GROUP BY r.description
  ORDER BY freq DESC
  LIMIT 20;
"""
df = pd.read_sql(query, conn)
conn.close()
print("Top 'Other' descriptions:")
print(df.to_string(index=False))
