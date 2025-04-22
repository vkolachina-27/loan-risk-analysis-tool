 scripts/recurring_descs.py
import psycopg2
import pandas as pd

conn = psycopg2.connect("dbname=bank_ml_mvp user=bank_user password=your_strong_password")
query = """
WITH freq AS (
  SELECT description, COUNT(DISTINCT to_char(date,'YYYY-MM')) AS months
  FROM transactions_raw
  GROUP BY description
)
SELECT description, months
FROM freq
WHERE months >= 3
ORDER BY months DESC
LIMIT 20;
"""
df = pd.read_sql(query, conn)
conn.close()
print("Most recurring descriptions (likely bills/payroll/rent):")
print(df.to_string(index=False))
