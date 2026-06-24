import { useEffect, useState } from "react";
import { Graph } from "./graph/Graph";
import { Inspector } from "./inspector/Inspector";
import { Filters } from "./filters/Filters";
import { fetchView, type NodeRow } from "./data/views";

export default function App() {
  const [selected, setSelected] = useState<string | null>(null);
  const [hidden, setHidden] = useState<Set<string> | undefined>(undefined);

  useEffect(() => { fetchView<NodeRow[]>("V1").catch(console.error); }, []);

  const judgmentsOnly = async (on: boolean) => {
    if (!on) return setHidden(undefined);
    const keep = new Set(await fetchView<string[]>("V5"));
    setHidden(keep);
  };
  const restsOn = async (on: boolean) => {
    if (!on || !selected) return setHidden(undefined);
    const v4 = await fetchView<Record<string, string[]>>("V4");
    const keep = new Set([selected, ...(v4[selected] ?? [])]);
    setHidden(keep);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      <header style={{ padding: "8px 16px", borderBottom: "1px solid #ddd" }}>
        <strong>Civic Claim Provenance</strong> — NYC composting claim
        <Filters onJudgmentsOnly={judgmentsOnly} onRestsOn={restsOn} />
      </header>
      <div style={{ display: "flex", flex: 1, minHeight: 0 }}>
        <div style={{ flex: 1, minWidth: 0 }}><Graph onSelect={setSelected} hidden={hidden} /></div>
        <Inspector selectedId={selected} />
      </div>
    </div>
  );
}
