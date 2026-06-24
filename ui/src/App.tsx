import { useEffect, useState } from "react";
import { fetchView, NodeRow } from "./data/views";
export default function App() {
  const [nodes, setNodes] = useState<NodeRow[]>([]);
  useEffect(() => { fetchView<NodeRow[]>("V1").then(setNodes).catch(console.error); }, []);
  return <pre>{nodes.length} nodes loaded</pre>;
}
