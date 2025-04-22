 bank-ml-mvp/app/main.py
from fastapi import FastAPI, File, UploadFile, HTTPException
import os, shutil
import joblib, psycopg2

app = FastAPI()
STATEMENTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "statements"))
rf_risk = joblib.load(os.path.abspath(os.path.join(os.path.dirname(__file__),"../models/rf_risk.pkl")))

@app.post("/upload")
async def upload_statement(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    dest_path = os.path.join(STATEMENTS_DIR, file.filename)
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"status": "uploaded", "filename": file.filename}

@app.get("/score/{statement_name}")
def score(statement_name: str):
    conn = psycopg2.connect("dbname=bank_ml_mvp user=bank_user password=your_strong_password")
    cur  = conn.cursor()
    cur.execute("""
      SELECT deposits, withdrawals, fees_total, transfer_in, transfer_out,
             COALESCE(o.total_loan_payments,0),
             COALESCE(r1.avg_amount,0), COALESCE(r2.avg_amount,0)
      FROM monthly_summary m
      LEFT JOIN outstanding_loans o 
        ON m.statement_name=o.statement_name
      LEFT JOIN recurring_bills r1 
        ON m.statement_name=r1.statement_name AND r1.category='Rent'
      LEFT JOIN recurring_bills r2 
        ON m.statement_name=r2.statement_name AND r2.category='Payroll'
      WHERE m.statement_name=%s
      ORDER BY m.year_month DESC
      LIMIT 1
    """, (statement_name,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return {"error": "Statement not found"}, 404
    prob     = float(rf_risk.predict_proba([row])[0][1])
    decision = bool(prob >= 0.5)
    return {"approve": decision, "confidence": round(prob,2)}

@app.get("/monthly/{statement_name}")
def get_monthly(statement_name: str):
    conn=psycopg2.connect("dbname=bank_ml_mvp user=bank_user password=your_strong_password")
    cur=conn.cursor()
    cur.execute("""
      SELECT year_month, deposits, withdrawals, fees_total, transfer_in, transfer_out
      FROM monthly_summary
      WHERE statement_name=%s
      ORDER BY year_month
    """, (statement_name,))
    data = [
      {"month":r[0],"in":float(r[1]),"out":float(r[2]),
       "fees":float(r[3]),"t_in":float(r[4]),"t_out":float(r[5])}
      for r in cur.fetchall()
    ]
    conn.close()
    return data

@app.get("/recurring/{statement_name}")
def get_recurring(statement_name: str):
    conn=psycopg2.connect("dbname=bank_ml_mvp user=bank_user password=your_strong_password")
    cur=conn.cursor()
    cur.execute("""
      SELECT category, avg_amount, count_months
      FROM recurring_bills
      WHERE statement_name=%s
    """, (statement_name,))
    data = [{"category":r[0],"avg":float(r[1]),"months":r[2]} for r in cur.fetchall()]
    conn.close()
    return data

@app.get("/loans/{statement_name}")
def get_loans(statement_name: str):
    conn=psycopg2.connect("dbname=bank_ml_mvp user=bank_user password=your_strong_password")
    cur=conn.cursor()
    cur.execute("""
      SELECT total_loan_payments, loan_tx_count
      FROM outstanding_loans
      WHERE statement_name=%s
    """, (statement_name,))
    row = cur.fetchone() or (0,0)
    conn.close()
    return {"payments": float(row[0]), "count": row[1]}
