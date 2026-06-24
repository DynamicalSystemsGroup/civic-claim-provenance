# Flexo backing

**Default: a local Flexo stack in Docker — no token needed.** The auth service issues
a token from `user01`/`password1` via `/login`; the CLI does this automatically.

The full Layer-1 stack is the external openmbee deployment (not vendored here):
```bash
git clone https://github.com/openmbee/flexo-mms-deployment.git
cd flexo-mms-deployment/docker-compose && docker compose up -d
# wait for: layer1-service ... Responding at http://0.0.0.0:8080
```
Then, from this repo:
```bash
cp flexo/.env.example .env     # local defaults already filled in (no token)
./flexo/init.sh                # provision org/repo + load the stub + refresh the cache
```
The CLI defaults (`FLEXO_URL=http://localhost:8080`, `FLEXO_AUTH_URL=http://localhost:8082`,
`user01`/`password1`) match these, so even an empty `.env` works once Docker is up.

Named graphs are preserved inside one `main` branch; V1–V5 query the union.

## Hosted remote (alternative)
The only path that needs a pre-issued token. Set in `.env`:
```bash
FLEXO_URL=https://try-layer1.starforge.app
FLEXO_TOKEN=eyJhbGci...      # when set, the login flow is skipped
```
Same contract, different URL — the dashboard never assumes remote availability.
