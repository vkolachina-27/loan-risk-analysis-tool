import React, { useEffect, useState } from "react";
import axios from "axios";

export default function LoansInfo({ statementName }) {
  const [info, setInfo] = useState({ payments: 0, count: 0 });
  useEffect(() => {
    axios.get(`/loans/${encodeURIComponent(statementName)}`)
      .then(res => setInfo(res.data));
  }, [statementName]);
  return (
    <div>
      <div>Total Loan Payments: ${info.payments.toFixed(2)}</div>
      <div>Loan Transaction Count: {info.count}</div>
    </div>
  );
}