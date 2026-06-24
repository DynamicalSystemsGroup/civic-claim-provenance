import { useEffect, useRef } from "react";
import cytoscape from "cytoscape";
import { fetchView, NodeRow, EdgeRow } from "../data/views";
import { TYPE_COLOR, VERDICT_OPACITY } from "./style";

export function Graph({ onSelect, hidden }: { onSelect: (id: string) => void; hidden?: Set<string> }) {
  const box = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);
  useEffect(() => {
    let cy: cytoscape.Core;
    Promise.all([fetchView<NodeRow[]>("V1"), fetchView<EdgeRow[]>("V2")]).then(([nodes, edges]) => {
      cy = cytoscape({
        container: box.current!,
        elements: [
          ...nodes.map((n) => ({ data: { id: n.id, label: n.label, type: n.type, verdict: n.verdict } })),
          ...edges.map((e) => ({ data: { id: `${e.src_id}-${e.rel}-${e.dst_id}`, source: e.src_id, target: e.dst_id, rel: e.rel } })),
        ],
        style: [
          { selector: "node", style: {
            "background-color": (el: any) => TYPE_COLOR[el.data("type")] ?? "#666",
            "background-opacity": (el: any) => VERDICT_OPACITY[el.data("verdict")] ?? 1,
            label: "data(label)", "font-size": 8, "text-wrap": "wrap", "text-max-width": "120px",
            width: 28, height: 28, "text-valign": "bottom" } },
          { selector: "edge", style: {
            label: "data(rel)", "font-size": 6, "curve-style": "bezier",
            "target-arrow-shape": "triangle", width: 1.5, "line-color": "#bbb", "target-arrow-color": "#bbb" } },
          { selector: ".hidden", style: { display: "none" } },
        ],
        layout: { name: "breadthfirst", directed: true, padding: 20 },
      });
      cy.on("tap", "node", (ev) => onSelect(ev.target.id()));
      cyRef.current = cy;
    });
    return () => cy?.destroy();
  }, [onSelect]);
  useEffect(() => {
    const cy = cyRef.current; if (!cy) return;
    cy.nodes().forEach((n) => n.toggleClass("hidden", !!hidden && !hidden.has(n.id())));
  }, [hidden]);
  return <div ref={box} style={{ width: "100%", height: "100%" }} />;
}
