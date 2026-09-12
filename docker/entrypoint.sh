#!/bin/sh
set -e
# Apply migrations before serving so a fresh image has tables.
# Kept out of /app so a compose bind-mount of the source tree cannot hide it.
alembic upgrade head
exec "$@"
