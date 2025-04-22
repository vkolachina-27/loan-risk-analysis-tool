!/usr/bin/env python3
import pandas as pd, psycopg2, joblib
from sklearn.ensemble import RandomForestClassifier

 1) Load features + label from your DB
conn = psycopg2.connect("dbname=bank_ml_mvp user=bank_user password=your_strong_password")
df = pd.read_sql("""
  SELECT
    m.statement_name,
    SUM(m.deposits)       AS net_deposits,
    SUM(m.withdrawals)    AS real_withdrawals,
    SUM(m.fees_total)     AS fees,
    SUM(m.transfer_in)    AS transfer_in,
    SUM(m.transfer_out)   AS transfer_out,
    MAX(o.total_loan_payments) AS total_loan_payments,
    MAX(rb1.avg_amount)   AS avg_rent,
    MAX(rb2.avg_amount)   AS avg_payroll,
    MAX(rl.approve)       AS label
  FROM monthly_summary m
  JOIN risk_labels rl           USING(statement_name)
  LEFT JOIN outstanding_loans o USING(statement_name)
  LEFT JOIN recurring_bills rb1 
    ON m.statement_name=rb1.statement_name AND rb1.category='Rent'
  LEFT JOIN recurring_bills rb2 
    ON m.statement_name=rb2.statement_name AND rb2.category='Payroll'
  GROUP BY m.statement_name
""", conn)
conn.close()

 2) Prepare X, y
X = df[[
  'net_deposits','real_withdrawals','fees',
  'transfer_in','transfer_out',
  'total_loan_payments','avg_rent','avg_payroll'
]]
y = df['label']

 3) Train & save
rf = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
rf.fit(X, y)
joblib.dump(rf, "models/rf_risk.pkl")
print("✅ Risk model trained on", len(df), "statements")
