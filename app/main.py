from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional

import os
import json
import shutil
import traceback

import joblib
import numpy as np
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()
STATEMENTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "statements"))

# Define feature columns
feature_columns = [
    'avg_monthly_deposits', 'deposits_stability',
    'avg_monthly_withdrawals', 'withdrawals_stability',
    'total_fees', 'total_transfer_in', 'total_transfer_out',
    'monthly_loan_payment', 'avg_rent', 'avg_payroll',
    'deposits_to_withdrawals', 'monthly_net', 'fees_ratio',
    'transfer_ratio', 'rent_to_income', 'loan_to_income',
    'high_loan_burden', 'negative_net_income', 'debt_service_ratio'
]

# Load model and scaler on startup
rf_risk = None
scaler = None

@app.on_event("startup")
def load_model():
    global rf_risk, scaler
    rf_risk = joblib.load(os.path.abspath(os.path.join(os.path.dirname(__file__),"../models/rf_risk.pkl")))
    scaler = joblib.load(os.path.abspath(os.path.join(os.path.dirname(__file__),"../models/scaler.pkl")))

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
    try:
        print(f"Processing score request for statement: {statement_name}")
        conn = psycopg2.connect("dbname=bank_ml_mvp user=bank_user password=your_strong_password")
        cur = conn.cursor()
        
        # First check if statement exists
        cur.execute("SELECT COUNT(*) FROM monthly_summary WHERE statement_name = %s", (statement_name,))
        count = cur.fetchone()[0]
        if count == 0:
            print(f"Statement not found: {statement_name}")
            return {"error": "Statement not found"}
        
        # Get monthly stats
        print("Fetching monthly stats...")
        cur.execute("""
            WITH monthly_stats AS (
                SELECT 
                    AVG(deposits) as avg_monthly_deposits,
                    STDDEV(deposits) as deposits_stability,
                    AVG(withdrawals) as avg_monthly_withdrawals,
                    STDDEV(withdrawals) as withdrawals_stability,
                    SUM(deposits) as total_deposits,
                    SUM(withdrawals) as total_withdrawals,
                    SUM(fees_total) as total_fees,
                    SUM(transfer_in) as total_transfer_in,
                    SUM(transfer_out) as total_transfer_out,
                    COUNT(*) as num_months
                FROM monthly_summary
                WHERE statement_name = %s
                GROUP BY statement_name
            )
            SELECT
                ms.*,
                COALESCE(o.total_loan_payments, 0) as total_loan_payments,
                COALESCE(r1.avg_amount, 0) as avg_rent,
                COALESCE(r2.avg_amount, 0) as avg_payroll
            FROM monthly_stats ms
            LEFT JOIN outstanding_loans o ON o.statement_name = %s
            LEFT JOIN recurring_bills r1 ON r1.statement_name = %s AND r1.category = 'Rent'
            LEFT JOIN recurring_bills r2 ON r2.statement_name = %s AND r2.category = 'Payroll'
        """, (statement_name, statement_name, statement_name, statement_name))
        
        row = cur.fetchone()
        if not row:
            print(f"No data found for statement: {statement_name}")
            return {"error": "No data found for statement"}
            
        print("Processing features...")
        # Convert row to feature vector and handle potential NULL values
        features = [0 if x is None else float(x) for x in row]
        
        # Calculate derived features with safe division
        total_deposits = features[4]  # Index from monthly_stats query
        total_withdrawals = features[5]
        num_months = features[9]
        avg_monthly_deposits = features[0]
        avg_monthly_withdrawals = features[2]
        total_fees = features[6]
        total_transfer_in = features[7]
        total_transfer_out = features[8]
        total_loan_payments = features[10]
        avg_rent = features[11]
        avg_payroll = features[12]
        
        # Calculate derived features with safe division
        deposits_to_withdrawals = total_deposits / total_withdrawals if total_withdrawals != 0 else 1
        monthly_net = (total_deposits - total_withdrawals) / num_months
        fees_ratio = total_fees / total_deposits if total_deposits != 0 else 0
        
        # Fix transfer ratio calculation to handle negative values
        transfer_in_amount = abs(total_transfer_in) if total_transfer_in < 0 else total_transfer_in
        transfer_out_amount = abs(total_transfer_out) if total_transfer_out < 0 else total_transfer_out
        transfer_ratio = (transfer_in_amount - transfer_out_amount) / (total_deposits + 1)
        
        # Calculate monthly metrics
        monthly_loan_payment = abs(total_loan_payments) / num_months if total_loan_payments != 0 else 0
        monthly_income = avg_monthly_deposits if avg_monthly_deposits > 0 else 0
        rent_to_income = avg_rent / (monthly_income + 1)
        loan_to_income = monthly_loan_payment / (monthly_income + 1)
        
        # Calculate risk indicators
        high_loan_burden = float(loan_to_income > 0.5)
        negative_net_income = float(monthly_net < 0)
        debt_service_ratio = (monthly_loan_payment + avg_rent) / (monthly_income + 1)

        # Prepare feature vector
        X = [avg_monthly_deposits, features[1],
             avg_monthly_withdrawals, features[3],
             total_fees, total_transfer_in, total_transfer_out,
             monthly_loan_payment, avg_rent, avg_payroll,
             deposits_to_withdrawals, monthly_net, fees_ratio,
             transfer_ratio, rent_to_income, loan_to_income,
             high_loan_burden, negative_net_income, debt_service_ratio]
        
        print("\nInput features:")
        for i, val in enumerate(X):
            print(f"{feature_columns[i]}: {val}")
        
        # Scale features
        X_scaled = scaler.transform([X])
        
        # Print scaled features
        print("\nScaled features:")
        for i, val in enumerate(X_scaled[0]):
            print(f"{feature_columns[i]}: {val}")
        
        # Get prediction probability and feature importances
        probs = rf_risk.predict_proba(X_scaled)
        print("\nRaw prediction probabilities:", probs)
        
        # Extract probabilities
        try:
            approve_prob = float(probs[0][1])
            decline_prob = float(probs[0][0])
            print(f"Approve probability: {approve_prob}")
            print(f"Decline probability: {decline_prob}")
        except Exception as e:
            print(f"Error extracting probabilities: {e}")
            approve_prob = 0.0
        
        # Overall confidence based on weighted deviations
        importance_score = 1.0
        print(f"Importance score: {importance_score}")
        
        # Final confidence score
        confidence = approve_prob * importance_score
        print(f"Final confidence: {confidence}")
        
        # Ensure confidence is valid
        confidence = max(0.0, min(1.0, confidence))
        
        # Determine decision and status based on confidence thresholds
        if approve_prob >= 0.75:
            decision = "Approve"
            status = "approve"
        elif approve_prob <= 0.25:
            decision = "Decline"
            status = "decline"
        else:
            suggested = "approve" if approve_prob >= 0.5 else "decline"
            decision = f"Check Manually ({suggested})"
            status = "manual_check"
        
        print(f"\nFinal result:")
        print(f"Decision: {decision}")
        print(f"Raw probability: {approve_prob:.2f}")
        
        return {
            "decision": decision,
            "status": status,
            "confidence": round(approve_prob, 2),
            "feature_values": {
                "deposits_to_withdrawals": round(deposits_to_withdrawals, 2),
                "monthly_net": round(monthly_net, 2),
                "fees_ratio": round(fees_ratio, 2),
                "rent_to_income": round(rent_to_income, 2),
                "loan_to_income": round(loan_to_income, 2),
                "debt_service_ratio": round(debt_service_ratio, 2),
                "high_loan_burden": high_loan_burden
            }
        }
    except Exception as e:
        print(f"Error in score endpoint: {str(e)}")
        traceback.print_exc()
        return {
            "decision": "Error",
            "status": "error",
            "confidence": None,
            "error": str(e)
        }
    finally:
        if 'conn' in locals():
            conn.close()

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
