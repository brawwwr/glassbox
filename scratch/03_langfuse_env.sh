#!/usr/bin/env bash
# Phase 3 — generate Langfuse secrets and both .env files.
#
#   cd ~/glassbox && git pull && bash scratch/03_langfuse_env.sh
#
# Writes:
#   ~/langfuse/.env   (22 lines: all compose secrets + DATABASE_URL + LANGFUSE_INIT_* so the login,
#                      org, project and API keys are created on first start)
#   ~/glassbox/.env   (LANGFUSE_PUBLIC_KEY / SECRET_KEY / HOST for the agent; git-ignored)
# Nothing is committed. Both files are chmod 600. Re-running overwrites both (only do that after
# `docker compose down -v`, or Postgres will still have the old password).

set -euo pipefail

[ -d ~/langfuse ] || { echo "~/langfuse not found. Clone it first: git clone https://github.com/langfuse/langfuse.git ~/langfuse"; exit 1; }

if [ -f ~/langfuse/.env ]; then
  echo "~/langfuse/.env already exists. Overwrite? Only safe after 'docker compose down -v'. [y/N]"
  read -r ans; [ "${ans:-N}" = "y" ] || { echo "aborted"; exit 1; }
fi

read -r -p "Langfuse login e-mail (local only): " LF_EMAIL
while :; do
  read -r -s -p "Langfuse login password (8+ chars): " LF_PASSWORD; echo
  [ "${#LF_PASSWORD}" -ge 8 ] && break
  echo "too short, try again"
done

rnd()  { openssl rand -hex 32; }
uuid() { cat /proc/sys/kernel/random/uuid; }
PK="pk-lf-$(uuid)"; SK="sk-lf-$(uuid)"; PGPW="$(rnd)"; MINIOPW="$(rnd)"

cat > ~/langfuse/.env << EOF
SALT=$(rnd)
ENCRYPTION_KEY=$(rnd)
NEXTAUTH_SECRET=$(rnd)
NEXTAUTH_URL=http://localhost:3000
POSTGRES_PASSWORD=$PGPW
DATABASE_URL=postgresql://postgres:$PGPW@postgres:5432/postgres
CLICKHOUSE_PASSWORD=$(rnd)
REDIS_AUTH=$(rnd)
MINIO_ROOT_PASSWORD=$MINIOPW
LANGFUSE_S3_EVENT_UPLOAD_SECRET_ACCESS_KEY=$MINIOPW
LANGFUSE_S3_MEDIA_UPLOAD_SECRET_ACCESS_KEY=$MINIOPW
LANGFUSE_S3_BATCH_EXPORT_SECRET_ACCESS_KEY=$MINIOPW
LANGFUSE_INIT_ORG_ID=glassbox-org
LANGFUSE_INIT_ORG_NAME=GlassBox
LANGFUSE_INIT_PROJECT_ID=glassbox
LANGFUSE_INIT_PROJECT_NAME=glassbox
LANGFUSE_INIT_PROJECT_PUBLIC_KEY=$PK
LANGFUSE_INIT_PROJECT_SECRET_KEY=$SK
LANGFUSE_INIT_USER_EMAIL=$LF_EMAIL
LANGFUSE_INIT_USER_NAME=Evan
LANGFUSE_INIT_USER_PASSWORD=$LF_PASSWORD
EOF

printf 'LANGFUSE_PUBLIC_KEY=%s\nLANGFUSE_SECRET_KEY=%s\nLANGFUSE_HOST=http://localhost:3000\n' "$PK" "$SK" > ~/glassbox/.env
chmod 600 ~/langfuse/.env ~/glassbox/.env

echo
echo "wrote ~/langfuse/.env ($(wc -l < ~/langfuse/.env) lines) and ~/glassbox/.env"
if git -C ~/glassbox status --short | grep -q '\.env'; then
  echo "WARNING: git sees .env — check .gitignore before committing!"
else
  echo "git ignores .env: OK"
fi
echo
echo "Next:  cd ~/langfuse && docker compose up -d && sleep 45 && docker compose ps"
