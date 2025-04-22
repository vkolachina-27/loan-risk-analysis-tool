import React, { useEffect, useState } from "react";
import axios from "axios";
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend } from "recharts";

export default function MonthlyChart({ statementName }) {
  const [data, setData] = useState([]);
  useEffect(() => {
    axios.get(`/monthly/${encodeURIComponent(statementName)}`)
      .then(res => setData(res.data));
  }, [statementName]);
  return (
    <LineChart width={600} height={300} data={data}>
      <XAxis dataKey="month" />
      <YAxis />
      <Tooltip />
      <Legend />
      <Line type="monotone" dataKey="in" stroke="#8884d8" name="In" />
      <Line type="monotone" dataKey="out" stroke="#ff7300" name="Out" />
      <Line type="monotone" dataKey="fees" stroke="#888" strokeDasharray="5 5" name="Fees" />
      <Line type="monotone" dataKey="t_in" stroke="#0a0" strokeDasharray="5 5" name="Transfer In" />
      <Line type="monotone" dataKey="t_out" stroke="#a00" strokeDasharray="5 5" name="Transfer Out" />
    </LineChart>
  );
}