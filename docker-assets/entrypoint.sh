#!/bin/bash

mkdir -p /app/log/nginx
mkdir -p /app/log/backend

python3 /app/backend/scripts/gen_nginx_config.py > /etc/nginx/sites-enabled/website.conf
python3 /app/backend/scripts/gen_nginx_config.py > /app/log/nginx/website.conf

python3 -u /app/backend/run_reducer_admin.py >> /app/log/backend/reducer.log 2>&1 &
python3 -u /app/backend/run_worker_api.py >> /app/log/backend/worker.log 2>&1 &

nginx -g 'daemon off;'
