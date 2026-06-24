export type NodeType = "claim" | "evidence" | "assumption" | "judgment" | "attestation";
export type Verdict = "passed" | "failed" | "cantTell" | "—";
export type EdgeRel = "supports" | "judges" | "dependsOn" | "assumes" | "attestsOver";
export interface NodeRow { id: string; type: NodeType; label: string; verdict: Verdict; }
export interface EdgeRow { src_id: string; dst_id: string; rel: EdgeRel; }

const API = (import.meta.env.VITE_API as string) ?? "http://127.0.0.1:8000";

export async function fetchView<T>(name: "V1" | "V2" | "V3" | "V4" | "V5"): Promise<T> {
  const r = await fetch(`${API}/views/${name}`);
  if (!r.ok) throw new Error(`view ${name}: ${r.status}`);
  return r.json() as Promise<T>;
}
