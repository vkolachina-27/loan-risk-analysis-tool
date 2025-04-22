 bank-ml-mvp/scripts/weak_label.py
import psycopg2, re

KEYWORDS = {
     — Rent
    'rent':       'Rent',
    'lease':      'Rent',
    'apartments': 'Rent',
    'landlord':   'Rent',
    'property':   'Rent',
    'rentals':    'Rent',

     — Payroll / Employee Salary / Labor
    'salary':     'Payroll',
    'payroll':    'Payroll',
    'payslip':    'Payroll',
    'epay':       'Payroll',
    'labor':      'Payroll',      catches “Labor – Growing” etc.
    'growing':    'Payroll',
    'harvest':    'Payroll',

     — Utilities
    'electric':   'Utilities',
    'hydro':      'Utilities',
    'water':      'Utilities',
    'gas':        'Utilities',
    'utility':    'Utilities',
    'telstra':    'Utilities',
    'vodafone':   'Utilities',
    'airtel':     'Utilities',
    'idea':       'Utilities',
    'videocon':   'Utilities',
    'tata power': 'Utilities',
    'dth':        'Utilities',
    'internet':   'Utilities',

     — Fees
    'account fee':      'Fees',
    'annual debit card':'Fees',
    'service charge':   'Fees',
    'analysis service': 'Fees',

     — Internal / External Transfers
    'transfer':      'Transfer',

     — Outstanding Loans / EMI
    'loan':       'Loan',
    'emi':        'Loan',
    'installment':'Loan',
    'disbursal':  'Loan',
    'finnovation':'Loan',
    'principal':  'Loan',
    'interest':   'Loan',
}


conn = psycopg2.connect("dbname=bank_ml_mvp user=bank_user password=your_strong_password")
print(f"[weak_label] Connected to: {conn.dsn}")
cur = conn.cursor()
 --- Find recurring deposit descriptions (credit, positive amount, 3+ months) ---
recurring_deposit_sql = '''
WITH freq AS (
  SELECT description, COUNT(DISTINCT to_char(date,'YYYY-MM')) AS months
  FROM transactions_raw
  WHERE amount > 0
  GROUP BY description
)
SELECT description FROM freq WHERE months >= 3;
'''
cur.execute(recurring_deposit_sql)
recurring_deposit_descs = set(row[0].strip().lower() for row in cur.fetchall())
print(f"[weak_label] Found {len(recurring_deposit_descs)} recurring deposit descriptions for Payroll labeling")

cur.execute("SELECT id, description, amount FROM transactions_raw")
rows = cur.fetchall()
print(f"[weak_label] Fetched {len(rows)} rows from transactions_raw")
count = 0
for tx_id, desc, amount in rows:
    label = 'Other'
    desc_low = desc.lower()
     1. Try keyword matching first
    for kw, cat in KEYWORDS.items():
        if kw in desc_low:
            label = cat
            break
     2. If not matched and is a recurring deposit, label as Payroll
    if label == 'Other' and desc_low in recurring_deposit_descs and amount > 0:
        label = 'Payroll'
    cur.execute("""
      INSERT INTO transactions_labeled(id, category)
      VALUES (%s,%s)
      ON CONFLICT (id) DO UPDATE SET category=EXCLUDED.category
    """, (tx_id, label))
    count += 1

conn.commit()
cur.close()
conn.close()
print(f"✅ Weak labels applied to {count} transactions")
