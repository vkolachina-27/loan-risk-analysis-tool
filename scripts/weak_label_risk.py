import psycopg2

conn = psycopg2.connect(
    "dbname=bank_ml_mvp user=bank_user password=your_strong_password"
)
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS risk_labels;")

cur.execute("""
CREATE TABLE risk_labels AS
WITH monthly AS (
  SELECT
    statement_name,
    to_char(date,'YYYY-MM') AS ym,
    SUM(CASE WHEN debit_credit THEN amount ELSE -amount END) AS net_month
  FROM transactions_raw t
  JOIN transactions_labeled l USING (id)
  GROUP BY statement_name, ym
),
agg AS (
  SELECT
    statement_name,
    SUM(net_month)     AS total_net,
    MIN(net_month)     AS min_month_net
  FROM monthly
  GROUP BY statement_name
),
fees AS (
  SELECT
    statement_name,
    SUM(CASE WHEN category='Fees' AND NOT debit_credit THEN amount ELSE 0 END)
      AS total_fees
  FROM transactions_raw t
  JOIN transactions_labeled l USING (id)
  GROUP BY statement_name
),
loans AS (
  SELECT
    statement_name,
    SUM(CASE WHEN category='Loan' AND debit_credit THEN amount ELSE 0 END)
      AS loan_payments
  FROM transactions_raw t
  JOIN transactions_labeled l USING (id)
  GROUP BY statement_name
),
deps AS (
  SELECT
    statement_name,
    SUM(CASE WHEN debit_credit AND category<>'Transfer' THEN amount ELSE 0 END)
      AS total_deposits
  FROM transactions_raw t
  JOIN transactions_labeled l USING (id)
  GROUP BY statement_name
)

SELECT
  a.statement_name,
  CASE
    WHEN a.total_net > 0
     AND a.min_month_net >= 0
     AND f.total_fees < 0.05 * d.total_deposits
     AND COALESCE(lo.loan_payments,0) < 0.5 * a.total_net
    THEN 1 ELSE 0
  END AS approve
FROM agg a
LEFT JOIN fees f ON f.statement_name = a.statement_name
LEFT JOIN loans lo ON lo.statement_name = a.statement_name
LEFT JOIN deps d ON d.statement_name = a.statement_name
;
""")

conn.commit()
cur.close()
conn.close()
print("✅ Risk labels rebuilt with mixed heuristics (approve=1/decline=0).")

if __name__ == "__main__":
    print("[INFO] Inserting simulated declines into risk_labels from monthly_summary...")
    import psycopg2
    DB_CONN = "dbname=bank_ml_mvp user=bank_user password=your_strong_password"
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    try:
        cur.execute("ALTER TABLE risk_labels ADD CONSTRAINT risk_labels_pk PRIMARY KEY (statement_name);")
    except Exception as e:
        print("[INFO] PK already exists or error adding PK:", e)

    cur.execute('''
        INSERT INTO risk_labels (statement_name, approve)
        SELECT statement_name, 0
        FROM monthly_summary
        WHERE statement_name LIKE 'Simulated Decline%'
        ON CONFLICT (statement_name) DO NOTHING;
    ''')
    conn.commit()
    cur.close()
    conn.close()
    print("[INFO] Simulated declines inserted into risk_labels.")
