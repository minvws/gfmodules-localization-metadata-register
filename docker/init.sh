#!/usr/bin/env bash

set -e

DB_STARTUP_WAIT=1

DB_HOST=${1}
DB_USER=${2:-postgres}
DB_PASS=${3:-postgres}
DB_NAME=${4:-postgres}

export PGPASSWORD=$DB_PASS

echo "Waiting for db container to finish startup"
sleep $DB_STARTUP_WAIT

echo "Migrating"
tools/./migrate_db.sh $DB_HOST $DB_USER $DB_PASS $DB_NAME

echo "Seeding"
tools/./seed.sh $DB_HOST $DB_USER $DB_PASS $DB_NAME

echo "Start main process"
python -m app.main
