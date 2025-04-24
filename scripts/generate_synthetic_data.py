#!/usr/bin/env python3
import pandas as pd
import numpy as np
import psycopg2
from sklearn.preprocessing import StandardScaler

# Connect to DB
conn = psycopg2.connect("dbname=bank_ml_mvp user=bank_user password=your_strong_password")
cur = conn.cursor()

# Generate synthetic data
n_samples = 100
np.random.seed(42)

# Generate base features
data = []
for i in range(n_samples):
    # Generate monthly deposits (higher is better)
    avg_monthly_deposits = np.random.lognormal(8, 1)  # Center around ~$3000
    deposits_stability = np.random.uniform(0, avg_monthly_deposits * 0.5)
    
    # Generate withdrawals (lower ratio to deposits is better)
    withdrawal_ratio = np.random.beta(2, 5)  # Mostly lower ratios
    avg_monthly_withdrawals = avg_monthly_deposits * withdrawal_ratio
    withdrawals_stability = np.random.uniform(0, avg_monthly_withdrawals * 0.5)
    
    # Generate other features
    total_deposits = avg_monthly_deposits * np.random.uniform(1, 12)
    total_withdrawals = avg_monthly_withdrawals * np.random.uniform(1, 12)
    total_fees = total_deposits * np.random.beta(1, 20)  # Mostly low fees
    total_transfer_in = total_deposits * np.random.beta(2, 2)
    total_transfer_out = total_withdrawals * np.random.beta(2, 2)
    total_loan_payments = total_deposits * np.random.beta(1, 4)  # Mostly low loan payments
    
    # Calculate derived features
    deposits_to_withdrawals = total_deposits / (total_withdrawals + 1)
    monthly_net = (total_deposits - total_withdrawals) / 12
    fees_ratio = total_fees / (total_deposits + 1)
    transfer_ratio = (total_transfer_in - total_transfer_out) / (total_deposits + 1)
    rent_to_income = np.random.beta(1, 3)  # Mostly low rent-to-income ratio
    loan_to_income = np.random.beta(1, 4)  # Mostly low loan-to-income ratio
    
    # Determine approval based on rules
    score = 0
    score += 1 if deposits_to_withdrawals > 1.2 else 0
    score += 1 if monthly_net > 1000 else 0
    score += 1 if fees_ratio < 0.05 else 0
    score += 1 if rent_to_income < 0.4 else 0
    score += 1 if loan_to_income < 0.3 else 0
    
    approve = score >= 3  # Approve if meeting at least 3 criteria
    
    # Add some noise to prevent perfect separation
    if np.random.random() < 0.1:  # 10% chance to flip the decision
        approve = not approve
    
    data.append({
        'statement_name': f'synthetic_{i}',
        'avg_monthly_deposits': avg_monthly_deposits,
        'deposits_stability': deposits_stability,
        'avg_monthly_withdrawals': avg_monthly_withdrawals,
        'withdrawals_stability': withdrawals_stability,
        'total_deposits': total_deposits,
        'total_withdrawals': total_withdrawals,
        'total_fees': total_fees,
        'total_transfer_in': total_transfer_in,
        'total_transfer_out': total_transfer_out,
        'total_loan_payments': total_loan_payments,
        'num_months': 12,
        'avg_rent': total_deposits * rent_to_income / 12,
        'avg_payroll': total_deposits * 0.8 / 12,  # Assume 80% of deposits are payroll
        'approve': approve
    })

# Convert to DataFrame
df = pd.DataFrame(data)

# Insert into database
for _, row in df.iterrows():
    # Insert monthly summary for each month
    for month in range(12):
        year_month = f'2024-{month+1:02d}'
        cur.execute("""
        INSERT INTO monthly_summary (
            statement_name, year_month, deposits, withdrawals, fees_total,
            transfer_in, transfer_out
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            row['statement_name'],
            year_month,
            row['avg_monthly_deposits'] * np.random.uniform(0.8, 1.2),  # Add some monthly variance
            row['avg_monthly_withdrawals'] * np.random.uniform(0.8, 1.2),
            row['total_fees'] / 12 * np.random.uniform(0.8, 1.2),
            row['total_transfer_in'] / 12 * np.random.uniform(0.8, 1.2),
            row['total_transfer_out'] / 12 * np.random.uniform(0.8, 1.2)
        ))
    
    # Insert risk label
    cur.execute("""
    INSERT INTO risk_labels (statement_name, approve)
    VALUES (%s, %s)
    """, (row['statement_name'], 1 if row['approve'] else 0))
    
    # Insert recurring bills
    if row['avg_rent'] > 0:
        cur.execute("""
        INSERT INTO recurring_bills (statement_name, category, avg_amount)
        VALUES (%s, 'Rent', %s)
        """, (row['statement_name'], row['avg_rent']))
    
    if row['avg_payroll'] > 0:
        cur.execute("""
        INSERT INTO recurring_bills (statement_name, category, avg_amount)
        VALUES (%s, 'Payroll', %s)
        """, (row['statement_name'], row['avg_payroll']))
    
    # Insert loan data
    cur.execute("""
    INSERT INTO outstanding_loans (statement_name, total_loan_payments)
    VALUES (%s, %s)
    """, (row['statement_name'], row['total_loan_payments']))

conn.commit()
print("✅ Generated and inserted synthetic data")
