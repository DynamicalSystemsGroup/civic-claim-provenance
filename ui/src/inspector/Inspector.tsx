import { useEffect, useState } from "react";
import { fetchView } from "../data/views";

export function Inspector({ selectedId }: { selectedId: string | null }) {
  const [detail, setDetail] = useState<Record<string, any>>({});
  useEffect(() => { fetchView<Record<string, any>>("V3").then(setDetail).catch(console.error); }, []);
  if (!selectedId) return <aside style={pane}><em>Select a node</em></aside>;
  const rec = detail[selectedId] ?? {};
  return (
    <aside style={pane}>
      <h3 style={{ marginTop: 0 }}>{selectedId}</h3>
      <table><tbody>
        {Object.entries(rec).map(([k, v]) => (
          <tr key={k}><td style={{ fontWeight: 600, paddingRight: 8, verticalAlign: "top" }}>{k}</td><td>{String(v)}</td></tr>
        ))}
      </tbody></table>
    </aside>
  );
}
const pane: React.CSSProperties = { width: 320, padding: 16, borderLeft: "1px solid #ddd", overflow: "auto", fontSize: 13 };
