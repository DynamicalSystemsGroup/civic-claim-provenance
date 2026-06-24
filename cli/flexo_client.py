"""Flexo MMS Layer-1 client. Adapted from ADCS-lifecycle-demo backends/flexo.py
and flexo-conflict-resolution-policy-research experiment-1/run.sh."""
from __future__ import annotations
import httpx

class FlexoClient:
    def __init__(self, base_url, org, repo, token=None, auth_url=None,
                 user="user01", password="password1", timeout=180):
        self.base = base_url.rstrip("/")
        self.org, self.repo = org, repo
        self.token = token
        self.auth_url = (auth_url or "").rstrip("/")
        self.user, self.password = user, password
        self.timeout = timeout

    def _branch_url(self, branch, verb):
        return f"{self.base}/orgs/{self.org}/repos/{self.repo}/branches/{branch}/{verb}"

    def _headers(self, content_type=None, accept=None):
        h = {"Authorization": f"Bearer {self.token}"}
        if content_type:
            h["Content-Type"] = content_type
        if accept:
            h["Accept"] = accept
        return h

    def login(self) -> str:
        # Remote uses a pre-issued token; local stack issues one via auth /login.
        if self.token:
            return self.token
        r = httpx.get(f"{self.auth_url}/login", auth=(self.user, self.password), timeout=30)
        r.raise_for_status()
        self.token = r.json()["token"]
        return self.token

    def ensure_branch(self, branch: str, base: str = "master") -> None:
        """Create branch if absent (idempotent). Mirrors ADCS _ensure_branch pattern."""
        url = f"{self.base}/orgs/{self.org}/repos/{self.repo}/branches/{branch}"
        r = httpx.head(url, headers=self._headers(), timeout=30)
        if r.status_code in (200, 204):
            return
        body = (
            f'<> <http://purl.org/dc/terms/title> "{branch}"@en ;\n'
            f'   <https://mms.openmbee.org/rdf/ontology/ref> <./{base}> .'
        )
        self.put_turtle(url, body)

    def put_turtle(self, url, body) -> int:
        r = httpx.put(url, headers=self._headers("text/turtle"), content=body, timeout=self.timeout)
        return r.status_code  # caller treats 2xx or 409 (exists) as OK

    def update(self, branch, sparql) -> int:
        r = httpx.post(self._branch_url(branch, "update"),
                       headers=self._headers("application/sparql-update"),
                       content=sparql, timeout=self.timeout)
        r.raise_for_status()
        return r.status_code

    def query(self, branch, sparql) -> dict:
        r = httpx.post(self._branch_url(branch, "query"),
                       headers=self._headers("application/sparql-query", "application/json"),
                       content=sparql, timeout=self.timeout)
        r.raise_for_status()
        return r.json()
