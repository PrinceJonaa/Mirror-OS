#!/usr/bin/env bash
# Run the repo init.sql against the local dashboard_db using the safe wrapper
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

SQL_FILE="$ROOT_DIR/init.sql"
if [ ! -f "$SQL_FILE" ]; then
  echo "init.sql not found at $SQL_FILE" >&2
  exit 2
fi

# Use the helper if present
HELPER="$ROOT_DIR/bin/psql_exec.sh"
if [ -x "$HELPER" ]; then
  "$HELPER" -f "$SQL_FILE"
else
  # fallback to absolute psql
  /opt/homebrew/opt/postgresql@16/bin/psql -d postgresql://dashboard_user:password@localhost:5432/dashboard_db -f "$SQL_FILE"
fi
