#!/bin/bash

set -e

BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}.sql.gz"
RETENTION_DAYS=7
RETENTION_WEEKS=4
RETENTION_MONTHS=6

POSTGRES_HOST="${POSTGRES_HOST:-postgres}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-english_trainer}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD}"
POSTGRES_DB="${POSTGRES_DB:-english_trainer_prod}"

echo "Starting database backup at $(date)"

mkdir -p "${BACKUP_DIR}"

PGPASSWORD="${POSTGRES_PASSWORD}" pg_dump \
    -h "${POSTGRES_HOST}" \
    -p "${POSTGRES_PORT}" \
    -U "${POSTGRES_USER}" \
    -d "${POSTGRES_DB}" \
    --format=custom \
    --compress=9 \
    --verbose \
    > "${BACKUP_FILE}"

BACKUP_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
echo "Backup completed: ${BACKUP_FILE} (${BACKUP_SIZE})"

echo "Cleaning old backups..."

find "${BACKUP_DIR}" -name "backup_*.sql.gz" -mtime +${RETENTION_DAYS} -type f -delete
echo "Deleted backups older than ${RETENTION_DAYS} days"

find "${BACKUP_DIR}" -name "backup_*.sql.gz" -mtime +$((RETENTION_DAYS * 7)) -type f -delete
echo "Deleted backups older than ${RETENTION_WEEKS} weeks"

find "${BACKUP_DIR}" -name "backup_*.sql.gz" -mtime +$((RETENTION_DAYS * 30)) -type f -delete
echo "Deleted backups older than ${RETENTION_MONTHS} months"

echo "Backup process completed at $(date)"
