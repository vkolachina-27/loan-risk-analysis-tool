import pandas as pd
import numpy as np

n_samples = 200
np.random.seed(42)

approved_count = 0
declined_count = 0
max_imbalance = 10

data = []
for i in range(n_samples):
    avg_monthly_deposits = np.random.lognormal(8, 1)
    deposits_stability = np.random.uniform(0, avg_monthly_deposits * 0.5)
    
    withdrawal_ratio = np.random.beta(2, 5)
    avg_monthly_withdrawals = avg_monthly_deposits * withdrawal_ratio
    withdrawals_stability = np.random.uniform(0, avg_monthly_withdrawals * 0.5)
    
    num_months = max(1, int(np.random.normal(12, 2)))
    
    total_deposits = avg_monthly_deposits * num_months
    total_withdrawals = avg_monthly_withdrawals * num_months
    total_fees = total_deposits * np.random.beta(1, 20)
    total_transfer_in = total_deposits * np.random.beta(2, 2)
    total_transfer_out = total_withdrawals * np.random.beta(2, 2)
    total_loan_payments = total_deposits * np.random.beta(1, 4)
    
    deposits_to_withdrawals = total_deposits / (total_withdrawals + 1)
    monthly_net = (total_deposits - total_withdrawals) / num_months
    fees_ratio = total_fees / (total_deposits + 1)
    transfer_ratio = (total_transfer_in - total_transfer_out) / (total_deposits + 1)
    rent_to_income = np.random.beta(1, 3)
    loan_to_income = np.random.beta(1, 4)
    
    score = 0
    score += 1 if deposits_to_withdrawals > 1.2 else 0
    score += 1 if monthly_net > 1000 else 0
    score += 1 if fees_ratio < 0.05 else 0
    score += 1 if rent_to_income < 0.4 else 0
    score += 1 if loan_to_income < 0.3 else 0
    
    initial_approve = score >= 3
    
    if abs(approved_count - declined_count) > max_imbalance:
        approve = 1 if approved_count < declined_count else 0
    else:
        approve = 1 if initial_approve else 0
    
    if approve == 1:
        approved_count += 1
    else:
        declined_count += 1
    
    avg_rent = total_deposits * rent_to_income / num_months
    avg_payroll = total_deposits * 0.8 / num_months
    
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
        'deposits_to_withdrawals': deposits_to_withdrawals,
        'monthly_net': monthly_net,
        'fees_ratio': fees_ratio,
        'transfer_ratio': transfer_ratio,
        'rent_to_income': rent_to_income,
        'loan_to_income': loan_to_income,
        'avg_rent': avg_rent,
        'avg_payroll': avg_payroll,
        'num_months': num_months,
        'risk_score': score,
        'approve': approve
    })

df = pd.DataFrame(data)
df.to_csv('statement_data.csv', index=False)
print("✅ Generated synthetic data and saved to statement_data.csv")
