import React, { useEffect, useState } from "react";
import axios from "axios";

export default function LoansInfo({ statementName }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!statementName?.trim()) {
      setData(null);
      return;
    }
    setError(null);
    axios.get(`/loans/${encodeURIComponent(statementName)}`)
      .then(res => {
        setData(res.data);
        setError(null);
      })
      .catch(err => {
        setData(null);
        setError(err.response?.data?.error || 'Failed to load loan data');
      });
  }, [statementName]);

  if (!statementName?.trim()) return null;
  if (error) return <div style={styles.error}>{error}</div>;
  if (!data) return <div style={styles.loading}>Loading...</div>;

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.label}>Total Loan Payments</div>
        <div style={styles.amount}>
          ${data.payments.toFixed(2)}
        </div>
      </div>

      <div style={styles.card}>
        <div style={styles.label}>Loan Transactions</div>
        <div style={styles.count}>
          {data.count}
          <span style={styles.subtitle}>transactions</span>
        </div>
      </div>

      {data.count > 0 && (
        <div style={styles.average}>
          Average Payment: ${(data.payments / data.count).toFixed(2)}
        </div>
      )}
    </div>
  );
}

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
  },
  card: {
    padding: '1rem',
    borderRadius: '8px',
    background: '#f9fafb',
    border: '1px solid #e5e7eb',
  },
  label: {
    fontSize: '0.875rem',
    color: '#6b7280',
    marginBottom: '0.5rem',
  },
  amount: {
    fontSize: '1.5rem',
    fontWeight: 600,
    color: '#047857',  // Green shade
  },
  count: {
    fontSize: '1.5rem',
    fontWeight: 600,
    color: '#1d4ed8',  // Blue shade
    display: 'flex',
    alignItems: 'baseline',
    gap: '0.5rem',
  },
  subtitle: {
    fontSize: '0.875rem',
    fontWeight: 400,
    color: '#6b7280',
  },
  average: {
    fontSize: '0.875rem',
    color: '#4b5563',
    padding: '0.5rem',
    borderRadius: '6px',
    background: '#f3f4f6',
    textAlign: 'center',
  },
  error: {
    color: '#ef4444',
    fontSize: '0.875rem',
  },
  loading: {
    color: '#6b7280',
    fontSize: '0.875rem',
  },
}