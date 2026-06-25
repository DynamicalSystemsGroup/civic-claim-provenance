"""ccp — the pipeline CLI. seed-offline | load | refresh | serve."""
from __future__ import annotations
import json, os
from pathlib import Path
import typer
from cli.curie import GRAPH_BRANCHES
from cli.trig_to_views import trig_to_views

app = typer.Typer(help="Civic Claim Provenance pipeline")
ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "views" / "cache"

def _write_cache(views: dict):
    CACHE.mkdir(parents=True, exist_ok=True)
    for name, data in views.items():
        (CACHE / f"{name}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False))

def _client():
    # Defaults target a LOCAL Flexo stack in Docker (openmbee/flexo-mms-deployment):
    # no token needed — the auth service issues one from user01/password1 via /login.
    # For the hosted remote, set FLEXO_URL + FLEXO_TOKEN in .env instead.
    from cli.flexo_client import FlexoClient
    return FlexoClient(os.environ.get("FLEXO_URL", "http://localhost:8080"),
                       os.environ.get("FLEXO_ORG", "civic"),
                       os.environ.get("FLEXO_REPO", "composting"),
                       token=os.environ.get("FLEXO_TOKEN"),
                       auth_url=os.environ.get("FLEXO_AUTH_URL", "http://localhost:8082"),
                       user=os.environ.get("FLEXO_USER", "user01"),
                       password=os.environ.get("FLEXO_PASS", "password1"))

@app.command("seed-offline")
def seed_offline(trig: str = "fixtures/graph-explorer-stub.trig"):
    """Build the cache directly from a .trig (no Flexo)."""
    _write_cache(trig_to_views(trig))
    typer.echo(f"cache written from {trig}")

@app.command()
def load(trig: str, base: str = "master"):
    """Load a .trig into Flexo (one branch per named graph, flat INSERT DATA).

    Follows the ADCS-lifecycle-demo pattern: each named graph IRI maps to a
    Flexo branch (last IRI segment), triples are loaded without a GRAPH clause
    because Flexo's /update endpoint rejects quads (QuadsNotAllowedException).
    """
    from rdflib import Dataset
    c = _client(); c.login()
    ds = Dataset(); ds.parse(trig, format="trig")
    for ctx in ds.graphs():
        nt = ctx.serialize(format="nt").strip()
        if not nt:
            continue
        g = str(ctx.identifier)
        if "x-rdflib" in g:
            continue  # skip rdflib internal default graph
        branch = g.rstrip("/:").rsplit(":", 1)[-1]  # e.g. "judgments"
        if branch not in GRAPH_BRANCHES:
            typer.echo(f"  skip unknown graph {g!r} (not in GRAPH_BRANCHES)", err=True)
            continue
        c.ensure_branch(branch, base=base)
        c.update(branch, "INSERT DATA {\n" + nt + "\n}")
        typer.echo(f"  {branch}: {len(nt.splitlines())} triples")
    typer.echo(f"loaded {trig} into Flexo")

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
