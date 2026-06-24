import { Graph } from "./graph/Graph";
export default function App() {
  return <div style={{ height: "100vh" }}><Graph onSelect={(id) => console.log(id)} /></div>;
}
