#!/bin/bash
set -ex

DB="${POSTGRES_DB:-postgres}"

echo "Running init-db.sh against database: ${DB}"

# Create additional databases if they don't exist
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$DB" <<-EOSQL
    SELECT 'CREATE DATABASE deepfix_portal'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'deepfix_portal')\gexec
    SELECT 'CREATE DATABASE mlflow'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'mlflow')\gexec
EOSQL
