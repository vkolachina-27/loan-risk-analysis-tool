import psycopg2

conn = psycopg2.connect("dbname=bank_ml_mvp user=bank_user password=your_strong_password")
cur  = conn.cursor()
cur.execute("DELETE FROM monthly_summary;")

cur.execute("""
INSERT INTO monthly_summary
SELECT
  statement_name,
  to_char(date,'YYYY-MM') AS year_month,
  -- deposits: credits excluding Transfers
  SUM(CASE WHEN debit_credit AND category<>'Transfer' THEN amount ELSE 0 END),
  -- withdrawals: debits excluding Transfers and Fees
  SUM(CASE WHEN NOT debit_credit AND category NOT IN ('Transfer','Fees') THEN amount ELSE 0 END),
  -- fees total: all Fees debits
  SUM(CASE WHEN NOT debit_credit AND category='Fees' THEN amount ELSE 0 END),
  -- transfer_in: credits that are Transfers
  SUM(CASE WHEN debit_credit AND category='Transfer' THEN amount ELSE 0 END),
  -- transfer_out: debits that are Transfers
  SUM(CASE WHEN NOT debit_credit AND category='Transfer' THEN amount ELSE 0 END)
FROM transactions_raw t
JOIN transactions_labeled l ON t.id=l.id
GROUP BY statement_name, year_month;
""")
conn.commit()
cur.execute("SELECT COUNT(*) FROM monthly_summary;")
print("Rows in monthly_summary:", cur.fetchone()[0])
cur.close()
conn.close()
print("✅ monthly_summary rebuilt with transfers & fees")
