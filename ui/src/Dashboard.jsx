import React, { useState } from "react";
import MonthlyChart from "./MonthlyChart";
import RecurringList from "./RecurringList";
import LoansInfo from "./LoansInfo";
import ScoreBadge from "./ScoreBadge";

export default function Dashboard() {
  const [statementName, setStatementName] = useState("Simulated Decline 1.pdf");

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>Bank Statement Analysis</h1>
        <div style={styles.inputContainer}>
          <input 
            style={styles.input}
            value={statementName} 
            onChange={e => setStatementName(e.target.value)}
            placeholder="Enter statement name..."
          />
        </div>
      </div>

      <div style={styles.content}>
        <div style={styles.scoreSection}>
          <ScoreBadge statementName={statementName} />
        </div>

        <div style={styles.mainSection}>
          <div style={styles.chartSection}>
            <h2 style={styles.sectionTitle}>Monthly Cash Flow</h2>
            <MonthlyChart statementName={statementName} />
          </div>

          <div style={styles.infoSection}>
            <div style={styles.panel}>
              <h2 style={styles.sectionTitle}>Recurring Bills</h2>
              <RecurringList statementName={statementName} />
            </div>

            <div style={styles.panel}>
              <h2 style={styles.sectionTitle}>Loan Activity</h2>
              <LoansInfo statementName={statementName} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    maxWidth: 1200,
    margin: '0 auto',
    padding: '20px',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif',
  },
  header: {
    marginBottom: '2rem',
    padding: '20px',
    borderRadius: '12px',
    background: '#f8f9fa',
  },
  title: {
    fontSize: '2rem',
    color: '#2c3e50',
    margin: '0 0 1rem 0',
  },
  inputContainer: {
    maxWidth: '600px',
  },
  input: {
    width: '100%',
    padding: '12px 16px',
    fontSize: '1rem',
    border: '2px solid #e9ecef',
    borderRadius: '8px',
    outline: 'none',
    transition: 'border-color 0.2s',
  },
  content: {
    display: 'flex',
    flexDirection: 'column',
    gap: '2rem',
  },
  scoreSection: {
    padding: '20px',
    borderRadius: '12px',
    background: '#fff',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  mainSection: {
    display: 'grid',
    gap: '2rem',
    gridTemplateColumns: '1fr',
  },
  chartSection: {
    padding: '20px',
    borderRadius: '12px',
    background: '#fff',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  infoSection: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
    gap: '2rem',
  },
  panel: {
    padding: '20px',
    borderRadius: '12px',
    background: '#fff',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  sectionTitle: {
    fontSize: '1.25rem',
    color: '#2c3e50',
    marginTop: 0,
    marginBottom: '1rem',
  },
}