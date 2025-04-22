import React, { useEffect, useState } from "react";
import axios from "axios";

export default function RecurringList({ statementName }) {
  const [data, setData] = useState([]);
  useEffect(() => {
    axios.get(`/recurring/${encodeURIComponent(statementName)}`)
      .then(res => setData(res.data));
  }, [statementName]);
  return (
    <ul>
      {data.map((item, idx) => (
        <li key={idx}>
          <b>{item.category}</b>: ${item.avg.toFixed(2)} ({item.months} months)
        </li>
      ))}
    </ul>
  );
}