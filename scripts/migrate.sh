#!/usr/bin/env bash
# Run database migrations in order
# Usage: ./scripts/migrate.sh
# Loads connection details from .env file

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
MIGRATIONS_DIR="$PROJECT_DIR/backend/db/migrations"
ENV_FILE="$PROJECT_DIR/.env"

# Load .env
if [ -f "$ENV_FILE" ]; then
    set -a
    source "$ENV_FILE"
    set +a
else
    echo "Error: .env file not found at $ENV_FILE"
    echo "Copy .env.sample to .env and fill in values."
    exit 1
fi

# Build connection string
export PGHOST="${POSTGRES_HOST:-localhost}"
export PGPORT="${POSTGRES_PORT:-5432}"
export PGDATABASE="${POSTGRES_DB:-fab_ui_dev}"
export PGUSER="${POSTGRES_USER:-fab_ui}"
export PGPASSWORD="${POSTGRES_PASSWORD}"

echo "Running migrations against $PGDATABASE@$PGHOST:$PGPORT as $PGUSER..."

for migration in "$MIGRATIONS_DIR"/*.sql; do
    filename=$(basename "$migration")
    echo "  Applying $filename..."
    psql -v ON_ERROR_STOP=1 -f "$migration" 2>&1
done

echo "Migrations complete."
