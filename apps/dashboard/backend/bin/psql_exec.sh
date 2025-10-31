#!/usr/bin/env bash
# Safe wrapper to run psql using absolute Homebrew-installed psql binary.
# Usage:
#   ./psql_exec.sh "<SQL STATEMENT>"
#   ./psql_exec.sh -f path/to/file.sql
#   ./psql_exec.sh -d postgresql://user:pass@host:5432/db "<SQL>"

set -euo pipefail

PSQL_BIN="/opt/homebrew/opt/postgresql@16/bin/psql"
if [ ! -x "$PSQL_BIN" ]; then
  echo "ERROR: psql binary not found at $PSQL_BIN" >&2
  exit 2
fi

# Default DB URL
DBURL_DEFAULT="postgresql://dashboard_user:password@localhost:5432/dashboard_db"

# Parse args
if [ "$#" -eq 0 ]; then
  echo "Usage: $0 [-d <DBURL>] [-f file.sql] | <SQL statement>" >&2
  exit 1
fi

DBURL="$DBURL_DEFAULT"

# allow optional -d DBURL first
if [ "$1" = "-d" ]; then
  shift
  DBURL="$1"
  shift
fi

if [ "$1" = "-f" ]; then
  shift
  SQLFILE="$1"
  if [ ! -f "$SQLFILE" ]; then
    echo "SQL file not found: $SQLFILE" >&2
    exit 2
  fi
  exec "$PSQL_BIN" -d "$DBURL" -f "$SQLFILE"
else
  # join remaining args into one SQL string
  SQL=""
  for a in "$@"; do
    SQL+="$a "
  done
  exec "$PSQL_BIN" -d "$DBURL" -c "$SQL"
fi
