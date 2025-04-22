import React, { useEffect, useState } from "react";
import axios from "axios";

export default function ScoreBadge({ statementName }) {
  const [score, setScore] = useState(null);
  useEffect(() => {
    axios.get(`/score/${encodeURIComponent(statementName)}`)
      .then(res => setScore(res.data));
  }, [statementName]);
  if (!score) return <div>Loading...</div>;
  return (
    <div>
      <h2>
        {score.approve ? "✅ Approve" : "❌ Decline"}
      </h2>
      <div>
        Confidence: <progress value={score.confidence} max="1" style={{ width: 200 }} />
        {` ${(score.confidence * 100).toFixed(1)}%`}
      </div>
    </div>
  );
}