#!/usr/bin/env bash
set -euo pipefail
# Provision org/repo and load the stub fixture into Flexo, then refresh the cache.
# Requires a .env with FLEXO_* (see .env.example). Reuses the ccp CLI.
cd "$(dirname "$0")/.."
[ -f .env ] && set -a && . ./.env && set +a
python3 - <<'PY'
import os, httpx
base=os.environ["FLEXO_URL"].rstrip("/"); org=os.environ.get("FLEXO_ORG","civic"); repo=os.environ.get("FLEXO_REPO","composting")
tok=os.environ.get("FLEXO_TOKEN")
if not tok and os.environ.get("FLEXO_AUTH_URL"):
    tok=httpx.get(os.environ["FLEXO_AUTH_URL"].rstrip("/")+"/login",
                  auth=(os.environ.get("FLEXO_USER","user01"),os.environ.get("FLEXO_PASS","password1")),timeout=30).json()["token"]
h={"Authorization":f"Bearer {tok}","Content-Type":"text/turtle"}
for url in (f"{base}/orgs/{org}", f"{base}/orgs/{org}/repos/{repo}"):
    code=httpx.put(url,headers=h,content=f'<> <http://purl.org/dc/terms/title> "x"@en .',timeout=180).status_code
    print(url, code, "(409=exists OK)" if code==409 else "")
PY
uv run ccp load fixtures/graph-explorer-stub.trig
uv run ccp refresh
echo "Flexo provisioned + cache refreshed."
