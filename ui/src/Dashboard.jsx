import React, { useState } from "react";
import MonthlyChart from "./MonthlyChart";
import RecurringList from "./RecurringList";
import LoansInfo from "./LoansInfo";
import ScoreBadge from "./ScoreBadge";

export default function Dashboard() {
  const [statementName, setStatementName] = useState("Simulated Decline 1.pdf");
  // Add file upload logic here if needed

  return (
    <div>
      <h1>Bank Statement Dashboard</h1>
      <input value={statementName} onChange={e => setStatementName(e.target.value)} />
      <ScoreBadge statementName={statementName} />
      <MonthlyChart statementName={statementName} />
      <RecurringList statementName={statementName} />
      <LoansInfo statementName={statementName} />
    </div>
  );
}