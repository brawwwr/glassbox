# NEXT — Phase 3, Langfuse (updated 21 Sep 2026)

State at last pause: Langfuse cloned to `~/langfuse`; first start failed (Postgres password mismatch);
volumes wiped with `docker compose down -v`; no `.env` files exist yet.

## [PC-Ubuntu]

```bash
cd ~/glassbox && git pull
bash scratch/03_langfuse_env.sh          # asks for a login e-mail + password, writes both .env files
cd ~/langfuse && docker compose up -d
sleep 45 && docker compose ps            # everything running/healthy, incl. langfuse-web
```

If `langfuse-web` keeps restarting:

```bash
docker compose logs --tail 30 langfuse-web
```

## [Browser on PC]

http://localhost:3000 → log in with the e-mail/password you typed → project `glassbox` should exist.

## [PC-Ubuntu] once logged in

```bash
cd ~/glassbox
uv add langfuse python-dotenv
uv pip show langfuse | head -2           # tell Claude the version
```

Then Claude writes the traced agent into the repo (Mac) → you `git pull` and run it.
