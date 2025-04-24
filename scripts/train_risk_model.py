#!/usr/bin/env python3
import pandas as pd
import numpy as np
import psycopg2
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler

# 1) Load features + label from DB
conn = psycopg2.connect("dbname=bank_ml_mvp user=bank_user password=your_strong_password")
df = pd.read_sql("""
  WITH monthly_stats AS (
    SELECT 
      statement_name,
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
    GROUP BY statement_name
  )
  SELECT
    ms.*,
    o.total_loan_payments,
    rb1.avg_amount as avg_rent,
    rb2.avg_amount as avg_payroll,
    rl.approve as label
  FROM monthly_stats ms
  JOIN risk_labels rl USING(statement_name)
  LEFT JOIN outstanding_loans o USING(statement_name)
  LEFT JOIN recurring_bills rb1 
    ON ms.statement_name=rb1.statement_name AND rb1.category='Rent'
  LEFT JOIN recurring_bills rb2 
    ON ms.statement_name=rb2.statement_name AND rb2.category='Payroll'
""", conn)
conn.close()

# 2) Feature Engineering
# Basic ratios
df['deposits_to_withdrawals'] = df['total_deposits'] / df['total_withdrawals'].replace(0, 1)
df['monthly_net'] = (df['total_deposits'] - df['total_withdrawals']) / df['num_months']
df['fees_ratio'] = df['total_fees'] / df['total_deposits'].replace(0, 1)

# Fix transfer ratio calculation to handle negative values
df['transfer_in_amount'] = df.apply(lambda row: abs(row['total_transfer_in']) if row['total_transfer_in'] < 0 else row['total_transfer_in'], axis=1)
df['transfer_out_amount'] = df.apply(lambda row: abs(row['total_transfer_out']) if row['total_transfer_out'] < 0 else row['total_transfer_out'], axis=1)
df['transfer_ratio'] = (df['transfer_in_amount'] - df['transfer_out_amount']) / (df['total_deposits'] + 1)

# Monthly expense ratios (relative to monthly deposits)
df['monthly_loan_payment'] = df.apply(lambda row: abs(row['total_loan_payments']) / row['num_months'] if row['total_loan_payments'] != 0 else 0, axis=1)
df['monthly_income'] = df.apply(lambda row: row['avg_monthly_deposits'] if row['avg_monthly_deposits'] > 0 else 0, axis=1)
df['rent_to_income'] = df['avg_rent'] / (df['monthly_income'] + 1)
df['loan_to_income'] = df['monthly_loan_payment'] / (df['monthly_income'] + 1)

# Risk indicators
df['high_loan_burden'] = (df['loan_to_income'] > 0.5).astype(float)
df['negative_net_income'] = (df['monthly_net'] < 0).astype(float)
df['debt_service_ratio'] = (df['monthly_loan_payment'] + df['avg_rent']) / (df['monthly_income'] + 1)

# Fill NaN values with 0
df = df.fillna(0)

# 3) Prepare features
feature_columns = [
    'avg_monthly_deposits', 'deposits_stability',
    'avg_monthly_withdrawals', 'withdrawals_stability',
    'total_fees', 'total_transfer_in', 'total_transfer_out',
    'monthly_loan_payment', 'avg_rent', 'avg_payroll',
    'deposits_to_withdrawals', 'monthly_net', 'fees_ratio',
    'transfer_ratio', 'rent_to_income', 'loan_to_income',
    'high_loan_burden', 'negative_net_income', 'debt_service_ratio'
]

X = df[feature_columns]
y = df['label']

# 4) Split data and scale features
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Print data quality info
print("\nData Quality Check:")
print(f"Total samples: {len(df)}")
print(f"Approval distribution:\n{df['label'].value_counts()}")
print("\nFeature statistics:")
print(df[feature_columns].describe())

# 5) Train model with adjusted parameters
rf = RandomForestClassifier(
    n_estimators=200,    # More trees for better probability estimates
    max_depth=4,         # More restricted depth to avoid overfitting
    min_samples_split=5, # Require more samples to split
    min_samples_leaf=3,  # Require more samples in leaves
    max_features='sqrt',
    class_weight={0: 2, 1: 1},  # Stronger bias against approval
    random_state=42
)

# 6) Evaluate with cross-validation
cv_scores = cross_val_score(rf, X_train_scaled, y_train, cv=3)
print(f"Cross-validation scores: {cv_scores}")
print(f"Average CV score: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")

# 7) Train final model and evaluate on test set
rf.fit(X_train_scaled, y_train)
y_pred = rf.predict(X_test_scaled)
print("\nModel Performance Report:")
print(classification_report(y_test, y_pred))

# 8) Print feature importance
importance = pd.DataFrame({
    'feature': feature_columns,
    'importance': rf.feature_importances_
})
print("\nTop 10 Most Important Features:")
print(importance.sort_values('importance', ascending=False).head(10))

# 9) Save model and scaler
joblib.dump(rf, "models/rf_risk.pkl")
joblib.dump(scaler, "models/scaler.pkl")
print(f"\n✅ Risk model trained on {len(df)} statements")
