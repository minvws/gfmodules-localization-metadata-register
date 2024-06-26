#!/usr/bin/env bash

set -e

DB_HOST=${1:-localhost}
DB_USER=${2:-postgres}
DB_PASS=${3:-postgres}
DB_NAME=${4:-postgres}

export PGPASSWORD=$DB_PASS

GREEN="\033[32m"
YELLOW="\033[33m"
BLUE="\033[34m"
NC="\033[0m"

shopt -s nullglob

echo -e "${GREEN}👀 Checking seed migrations for ${BLUE}$DB_NAME${GREEN} on ${BLUE}$DB_HOST${NC}"

# check if the seed_migrations table exists
if
    psql -h $DB_HOST -U $DB_USER -d $DB_NAME -t -c "\dt" | grep 'seed_migrations' > /dev/null
    [ $? -eq 1 ]; then
    echo -e "${YELLOW}⚠️ Seed migration table does not exists. Creating seed migrations table.${NC}"

    # create the seed_migrations table
    echo "CREATE TABLE seed_migrations (id serial PRIMARY KEY, name VARCHAR(255) NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);" | psql -h $DB_HOST -U $DB_USER -d $DB_NAME -q -o /dev/null
fi

for file in seeds/*.sql; do
    # Check each SQL file to see if it's already in the migrations table
    if psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT name FROM seed_migrations WHERE name = '$file';" | grep -q $file; then
        echo -e "${YELLOW}⏩ File $file is already in the seed_migrations table. Skipping.${NC}"
    else
        echo -e "${GREEN}▶️ Running seed_migrations $file${NC}"
        psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f $file -q -o /dev/null
        echo "INSERT INTO seed_migrations (name) VALUES ('$file');" | psql -h $DB_HOST -U $DB_USER -d $DB_NAME -o /dev/null
    fi
done

for file in seeds/*.py; do
    # Check each SQL file to see if it's already in the migrations table
    if psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT name FROM seed_migrations WHERE name = '$file';" | grep -q $file; then
        echo -e "${YELLOW}⏩ File $file is already in the seed_migrations table. Skipping.${NC}"
    else
        echo -e "${GREEN}▶️ Running seed_migrations $file${NC}"
        python $file
        echo "INSERT INTO seed_migrations (name) VALUES ('$file');" | psql -h $DB_HOST -U $DB_USER -d $DB_NAME -o /dev/null
    fi
done

shopt -u nullglob
