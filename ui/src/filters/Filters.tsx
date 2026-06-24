import { useState } from "react";
export function Filters({ onJudgmentsOnly, onRestsOn }:
  { onJudgmentsOnly: (on: boolean) => void; onRestsOn: (on: boolean) => void }) {
  const [j, setJ] = useState(false); const [r, setR] = useState(false);
  return (
    <div style={{ display: "flex", gap: 8, padding: 8 }}>
      <button onClick={() => { const v = !j; setJ(v); onJudgmentsOnly(v); }}
              style={btn(j)}>Show only the judgment calls</button>
      <button onClick={() => { const v = !r; setR(v); onRestsOn(v); }}
              style={btn(r)}>What this rests on (stretch)</button>
    </div>
  );
}
const btn = (on: boolean): React.CSSProperties => ({
  padding: "6px 10px", border: "1px solid #888", borderRadius: 6,
  background: on ? "#1f2937" : "#fff", color: on ? "#fff" : "#111", cursor: "pointer" });
