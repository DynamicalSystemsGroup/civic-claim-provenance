import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_seed_offline_then_serve_shapes():
    subprocess.run([sys.executable, "-m", "cli.ccp", "seed-offline"], check=True, cwd=ROOT)
    v1 = json.loads((ROOT / "views/cache/V1.json").read_text())
    v2 = json.loads((ROOT / "views/cache/V2.json").read_text())
    assert len(v1) == 6 and len(v2) == 7
    assert {n["type"] for n in v1} == {"claim", "evidence", "assumption", "judgment", "attestation"}
    assert {e["rel"] for e in v2} == {"supports", "judges", "dependsOn", "assumes", "attestsOver"}
    # cross-view integrity: every edge endpoint exists as a node id
    ids = {n["id"] for n in v1}
    for e in v2:
        assert e["src_id"] in ids and e["dst_id"] in ids
