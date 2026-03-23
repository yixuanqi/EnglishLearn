#!/bin/bash

set -e

BACKUP_DIR="/backups"
POSTGRES_HOST="${POSTGRES_HOST:-postgres}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-english_trainer}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD}"
POSTGRES_DB="${POSTGRES_DB:-english_trainer_prod}"

if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file>"
    echo "Available backups:"
    ls -lh "${BACKUP_DIR}"/*.sql.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "${BACKUP_FILE}" ]; then
    echo "Error: Backup file not found: ${BACKUP_FILE}"
    exit 1
fi

echo "Restoring database from ${BACKUP_FILE} at $(date)"

echo "Dropping existing database..."
PGPASSWORD="${POSTGRES_PASSWORD}" dropdb \
    -h "${POSTGRES_HOST}" \
    -p "${POSTGRES_PORT}" \
    -U "${POSTGRES_USER}" \
    --if-exists \
    "${POSTGRES_DB}"

echo "Creating new database..."
PGPASSWORD="${POSTGRES_PASSWORD}" createdb \
    -h "${POSTGRES_HOST}" \
    -p "${POSTGRES_PORT}" \
    -U "${POSTGRES_USER}" \
    "${POSTGRES_DB}"

echo "Restoring database..."
PGPASSWORD="${POSTGRES_PASSWORD}" pg_restore \
    -h "${POSTGRES_HOST}" \
    -p "${POSTGRES_PORT}" \
    -U "${POSTGRES_USER}" \
    -d "${POSTGRES_DB}" \
    --verbose \
    --no-owner \
    --no-acl \
    "${BACKUP_FILE}"

echo "Database restore completed at $(date)"
