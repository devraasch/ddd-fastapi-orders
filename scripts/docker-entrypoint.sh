#!/bin/sh
set -e
cd /app
if [ "${SKIP_MIGRATIONS:-0}" = "1" ]; then
  echo "SKIP_MIGRATIONS=1: pulando alembic upgrade head"
else
  echo "Aplicando migrações (alembic upgrade head)..."
  if ! uv run alembic upgrade head; then
    echo "Migração falhou. No Docker Compose, DATABASE_URL deve apontar para o host " \
         "'db' (já injetada em environment no docker-compose). Ver credenciais POSTGRES_*. " \
         "No host, confirme que o Postgres escuta a porta mapeada." >&2
    exit 1
  fi
fi
exec "$@"
