import React, { useEffect, useState } from "react";
import axios from "axios";

export default function RecurringList({ statementName }) {
  const [data, setData] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!statementName?.trim()) {
      setData([]);
      return;
    }
    setError(null);
    axios.get(`/recurring/${encodeURIComponent(statementName)}`)
      .then(res => {
        setData(res.data);
        setError(null);
      })
      .catch(err => {
        setData([]);
        setError(err.response?.data?.error || 'Failed to load recurring bills');
      });
  }, [statementName]);

  if (!statementName?.trim()) return null;
  if (error) return <div style={styles.error}>{error}</div>;
  if (!data.length) return <div style={styles.loading}>Loading...</div>;

  // Calculate the maximum amount for relative sizing
  const maxAmount = Math.max(...data.map(item => item.avg));

  return (
    <div style={styles.container}>
      {data.map((item, idx) => (
        <div key={idx} style={styles.item}>
          <div style={styles.header}>
            <div style={styles.category}>{item.category}</div>
            <div style={styles.months}>{item.months} months</div>
          </div>
          
          <div style={styles.barContainer}>
            <div 
              style={{
                ...styles.bar,
                width: `${(item.avg / maxAmount) * 100}%`,
                background: getBarColor(item.category)
              }}
            />
          </div>
          
          <div style={styles.amount}>
            ${item.avg.toFixed(2)}
            <span style={styles.frequency}>/month</span>
          </div>
        </div>
      ))}
    </div>
  );
}

function getBarColor(category) {
  const colors = {
    'Rent': '#60a5fa',      // Blue
    'Payroll': '#34d399',   // Green
    'Utilities': '#fbbf24',  // Yellow
    'Insurance': '#f87171',  // Red
  };
  return colors[category] || '#9ca3af';
}

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
  },
  item: {
    padding: '0.75rem',
    borderRadius: '8px',
    background: '#f9fafb',
    transition: 'transform 0.2s',
    ':hover': {
      transform: 'translateX(4px)'
    }
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '0.5rem',
  },
  category: {
    fontWeight: 500,
    color: '#374151',
  },
  months: {
    fontSize: '0.75rem',
    color: '#6b7280',
    padding: '0.25rem 0.5rem',
    borderRadius: '9999px',
    background: '#e5e7eb',
  },
  barContainer: {
    height: '6px',
    background: '#e5e7eb',
    borderRadius: '3px',
    overflow: 'hidden',
    marginBottom: '0.5rem',
  },
  bar: {
    height: '100%',
    transition: 'width 0.3s ease',
  },
  amount: {
    fontSize: '1.125rem',
    fontWeight: 500,
    color: '#111827',
  },
  frequency: {
    fontSize: '0.75rem',
    color: '#6b7280',
    marginLeft: '0.25rem',
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