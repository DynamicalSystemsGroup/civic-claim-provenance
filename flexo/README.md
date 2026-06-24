# Flexo backing

Default: hosted remote `try-layer1.starforge.app` (Z holds the token) — no Docker.
Set `FLEXO_TOKEN` in `.env` (copy from `.env.example`), then `./flexo/init.sh`.

## Local stack (offline fallback)
The full Layer-1 stack is the external openmbee deployment, not vendored here:
```bash
git clone https://github.com/openmbee/flexo-mms-deployment.git
cd flexo-mms-deployment/docker-compose && docker compose up -d
# wait for: layer1-service ... Responding at http://0.0.0.0:8080
```
Then point `.env` at the local URLs (commented block in `.env.example`) and run `./flexo/init.sh`.
Named graph = preserved inside one `main` branch; V1–V5 query the union.
