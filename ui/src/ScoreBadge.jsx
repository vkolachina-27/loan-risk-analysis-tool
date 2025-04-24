import React, { useEffect, useState } from "react";
import axios from "axios";

export default function ScoreBadge({ statementName }) {
  const [score, setScore] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!statementName?.trim()) {
      setScore(null);
      return;
    }
    setError(null);
    axios.get(`/score/${encodeURIComponent(statementName)}`)
      .then(res => {
        setScore(res.data);
        setError(null);
      })
      .catch(err => {
        setScore({ error: err.response?.data?.error || 'Failed to load score' });
        setError(err.response?.data?.error || 'Failed to load score');
      });
  }, [statementName]);

  if (!score) return (
    <div style={styles.loading}>
      <div style={styles.loadingDot}></div>
      <div style={{...styles.loadingDot, animationDelay: '0.2s'}}></div>
      <div style={{...styles.loadingDot, animationDelay: '0.4s'}}></div>
    </div>
  );

  if (score.error) return (
    <div style={styles.error}>
      Error: {score.error}
    </div>
  );

  if (!score.decision || !score.status) return (
    <div style={styles.loading}>
      Processing...
    </div>
  );

  const getStatusColor = (status) => {
    switch (status) {
      case 'approve': return '#22c55e';
      case 'decline': return '#ef4444';
      case 'manual_check': return '#f59e0b';
      default: return '#6b7280';
    }
  };

  const badgeStyle = {
    ...styles.badge,
    background: getStatusColor(score.status)
  };

  const confidenceBarStyle = {
    ...styles.confidenceBar,
    width: `${score.confidence * 100}%`,
    background: getStatusColor(score.status)
  };

  return (
    <div style={styles.container}>
      <div style={badgeStyle}>
        {score.decision}
      </div>
      
      <div style={styles.confidenceContainer}>
        <div style={styles.confidenceLabel}>
          Confidence: {Math.round(score.confidence * 100)}%
        </div>
        <div style={styles.confidenceTrack}>
          <div style={styles.confidenceTrack_low} />
          <div style={styles.confidenceTrack_med} />
          <div style={styles.confidenceTrack_high} />
          <div style={confidenceBarStyle} />
        </div>
      </div>

      {score.feature_values && (
        <div style={styles.featureGrid}>
          {Object.entries(score.feature_values || {}).map(([key, value]) => (
            <div key={key} style={styles.featureItem}>
              <div style={styles.featureLabel}>{key.replace(/_/g, ' ')}</div>
              <div style={styles.featureValue}>{value}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

const styles = {
  error: {
    color: '#ef4444',
    padding: '1rem',
    background: '#fee2e2',
    borderRadius: '6px',
    fontSize: '0.875rem',
  },
  container: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
    padding: '1rem',
    background: '#fff',
    borderRadius: '8px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
  },
  badge: {
    padding: '0.5rem 1rem',
    borderRadius: '6px',
    color: '#fff',
    fontWeight: 500,
    textAlign: 'center',
    fontSize: '1.125rem',
  },
  confidenceContainer: {
    marginTop: '0.5rem',
  },
  confidenceLabel: {
    fontSize: '0.875rem',
    color: '#6b7280',
    marginBottom: '0.25rem',
  },
  confidenceTrack: {
    height: '6px',
    background: '#e5e7eb',
    borderRadius: '3px',
    overflow: 'hidden',
    position: 'relative',
  },
  confidenceTrack_low: {
    position: 'absolute',
    left: '0',
    width: '20%',
    height: '100%',
    background: '#fee2e2',
    borderRight: '2px solid #fff',
  },
  confidenceTrack_med: {
    position: 'absolute',
    left: '20%',
    width: '60%',
    height: '100%',
    background: '#fef3c7',
    borderRight: '2px solid #fff',
  },
  confidenceTrack_high: {
    position: 'absolute',
    left: '80%',
    width: '20%',
    height: '100%',
    background: '#dcfce7',
  },
  confidenceBar: {
    position: 'absolute',
    left: '0',
    height: '100%',
    transition: 'width 0.3s ease',
  },
  featureGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
    gap: '1rem',
    marginTop: '1rem',
  },
  featureItem: {
    padding: '0.75rem',
    background: '#f9fafb',
    borderRadius: '6px',
  },
  featureLabel: {
    fontSize: '0.75rem',
    color: '#6b7280',
    marginBottom: '0.25rem',
  },
  featureValue: {
    fontSize: '1rem',
    color: '#111827',
    fontWeight: 500,
  },
  loading: {
    display: 'flex',
    gap: '0.5rem',
    justifyContent: 'center',
  },
  loadingDot: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    background: '#6b7280',
    animation: 'bounce 0.5s infinite alternate'
  }
};