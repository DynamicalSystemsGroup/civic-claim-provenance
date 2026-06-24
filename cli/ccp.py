"""ccp — the pipeline CLI. seed-offline | load | refresh | serve."""
from __future__ import annotations
import json, os
from pathlib import Path
import typer
from cli.trig_to_views import trig_to_views

app = typer.Typer(help="Civic Claim Provenance pipeline")
ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "views" / "cache"

def _write_cache(views: dict):
    CACHE.mkdir(parents=True, exist_ok=True)
    for name, data in views.items():
        (CACHE / f"{name}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False))

def _client():
    from cli.flexo_client import FlexoClient
    return FlexoClient(os.environ.get("FLEXO_URL", "https://try-layer1.starforge.app"),
                       os.environ.get("FLEXO_ORG", "civic"),
                       os.environ.get("FLEXO_REPO", "composting"),
                       token=os.environ.get("FLEXO_TOKEN"),
                       auth_url=os.environ.get("FLEXO_AUTH_URL"))

@app.command("seed-offline")
def seed_offline(trig: str = "fixtures/graph-explorer-stub.trig"):
    """Build the cache directly from a .trig (no Flexo)."""
    _write_cache(trig_to_views(trig))
    typer.echo(f"cache written from {trig}")

@app.command()
def load(trig: str, branch: str = os.environ.get("FLEXO_BRANCH", "main")):
    """Load a .trig into Flexo (named graphs preserved on one branch)."""
    from rdflib import Dataset
    c = _client(); c.login()
    ds = Dataset(); ds.parse(trig, format="trig")
    for ctx in ds.contexts():
        nt = ctx.serialize(format="nt").strip()
        if not nt:
            continue
        gname = str(ctx.identifier)
        body = f"INSERT DATA {{ GRAPH <{gname}> {{\n{nt}\n}} }}"
        c.update(branch, body)
    typer.echo(f"loaded {trig} into {branch}")

@app.command()
def refresh(branch: str = os.environ.get("FLEXO_BRANCH", "main")):
    """Materialize the cache from Flexo via SPARQL."""
    from cli.views import materialize
    c = _client(); c.login()
    _write_cache(materialize(c, branch))
    typer.echo("cache refreshed from Flexo")

@app.command()
def serve(host: str = "127.0.0.1", port: int = 8000):
    """Run the dashboard backend (serves the cache + /refresh)."""
    import uvicorn
    uvicorn.run("server.app:api", host=host, port=port)

if __name__ == "__main__":
    app()
