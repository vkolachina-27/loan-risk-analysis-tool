import psycopg2

conn = psycopg2.connect("dbname=bank_ml_mvp user=bank_user password=your_strong_password")
cur = conn.cursor()
cur.execute("DELETE FROM recurring_bills;")

cur.execute("""
WITH monthly_cat AS (
  SELECT
    t.statement_name,
    to_char(t.date,'YYYY-MM') AS ym,
    l.category,
    SUM(t.amount) AS sum_amt
  FROM transactions_raw t
  JOIN transactions_labeled l USING(id)
  WHERE l.category IN ('Rent','Payroll','Utilities','Loan','Fees')
  GROUP BY t.statement_name, ym, l.category
)
INSERT INTO recurring_bills(statement_name, category, avg_amount, count_months)
SELECT
  statement_name,
  category,
  ROUND(AVG(sum_amt)::numeric,2),
  COUNT(*)::int
FROM monthly_cat
GROUP BY statement_name, category;
""")
conn.commit()
cur.close()
conn.close()
print("✅ recurring_bills rebuilt with Fees included")
