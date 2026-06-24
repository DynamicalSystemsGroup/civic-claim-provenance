"""Dashboard backend: serve the JSON cache + a refresh hook. CORS open for Vite dev."""
from __future__ import annotations
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "views" / "cache"
VIEWS = {"V1", "V2", "V3", "V4", "V5"}

api = FastAPI(title="Civic Claim Provenance backend")
api.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@api.get("/views/{name}")
def get_view(name: str):
    if name not in VIEWS:
        raise HTTPException(404, f"unknown view {name}")
    f = CACHE / f"{name}.json"
    if not f.exists():
        raise HTTPException(404, f"{name} not materialized — run `ccp seed-offline`")
    return json.loads(f.read_text())

@api.post("/refresh")
def refresh(trig: str = "fixtures/graph-explorer-stub.trig"):
    from cli.trig_to_views import trig_to_views
    views = trig_to_views(str(ROOT / trig))
    CACHE.mkdir(parents=True, exist_ok=True)
    for n, data in views.items():
        (CACHE / f"{n}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False))
    return {"refreshed": sorted(views.keys())}
