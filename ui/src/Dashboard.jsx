import React, { useState } from "react";
import MonthlyChart from "./MonthlyChart";
import RecurringList from "./RecurringList";
import LoansInfo from "./LoansInfo";
import ScoreBadge from "./ScoreBadge";

const PDF_OPTIONS = [
  "Free Editable Bank Statement .pdf",
  "Free PDF Bank Statement .pdf",
  "Bank Statement Example Free .pdf",
  "Word Format Bank Statement Sample .pdf",
  "Dummy Statement 1.pdf",
  "Dummy Statement 2.pdf"
];

export default function Dashboard() {
  const [statementName, setStatementName] = useState("");

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>Bank Statement Analysis</h1>
        <div style={styles.inputContainer}>
          <div style={styles.inputGroup}>
            <select 
              style={styles.input}
              value={statementName} 
              onChange={e => setStatementName(e.target.value)}
            >
              <option value="">Select a PDF...</option>
              {PDF_OPTIONS.map(pdf => (
                <option key={pdf} value={pdf}>{pdf}</option>
              ))}
            </select>
            <button style={styles.uploadButton}>Upload File</button>
          </div>
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
    maxWidth: '800px',
  },
  inputGroup: {
    display: 'flex',
    gap: '12px',
    alignItems: 'center',
  },
  input: {
    flex: 1,
    padding: '12px 16px',
    fontSize: '1rem',
    border: '2px solid #e9ecef',
    borderRadius: '8px',
    outline: 'none',
    transition: 'border-color 0.2s',
    backgroundColor: '#fff',
    cursor: 'pointer',
    appearance: 'none',
    WebkitAppearance: 'none',
    MozAppearance: 'none',
    backgroundImage: 'url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23007CB2%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E")',
    backgroundRepeat: 'no-repeat',
    backgroundPosition: 'right 12px top 50%',
    backgroundSize: '12px auto',
    paddingRight: '40px',
  },
  uploadButton: {
    padding: '12px 24px',
    fontSize: '1rem',
    backgroundColor: '#3b82f6',
    color: '#fff',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
    fontWeight: '500',
    ':hover': {
      backgroundColor: '#2563eb',
    },
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