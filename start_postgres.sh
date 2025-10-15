#!/bin/bash
# Start PostgreSQL if not already running
if ! ps aux | grep "[p]ostgres -D" > /dev/null; then
    mkdir -p ~/.postgres/data ~/.postgres/run
    if [ ! -f ~/.postgres/data/PG_VERSION ]; then
        initdb -D ~/.postgres/data
    fi
    nohup postgres -D ~/.postgres/data -k ~/.postgres/run > ~/.postgres/server.log 2>&1 &
    sleep 3
    echo "PostgreSQL started"
else
    echo "PostgreSQL already running"
fi
