#!/bin/bash

service cron start
echo "0 4 * * * /usr/sbin/logrotate /etc/logrotate.d/nginx" | crontab -

mkdir -p /app/log/nginx
mkdir -p /app/log/backend

python3 /app/backend/scripts/gen_nginx_config.py > /etc/nginx/sites-enabled/website.conf
python3 /app/backend/scripts/gen_nginx_config.py > /app/log/nginx/website.conf

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
python3 -u /app/backend/run_all.py >> /app/log/backend/${TIMESTAMP}.log 2>&1 &

nginx -g 'daemon off;'
