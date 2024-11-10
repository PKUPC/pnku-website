import sys

from pathlib import Path


sys.path.append(str((Path(__file__).parent / '..').resolve()))
from src import secret


CONFIG_TEMPLATE = """map $cookie_user_token $user_hash {{
    "" $remote_addr;
    default $cookie_user_token;
}}

upstream backend_admin {{
    server {admin_ip}:{admin_port} fail_timeout=0s;
}}

upstream backend_worker {{
    hash $user_hash;
{worker_config}
}}

server {{
    listen 80;
    server_name _;

    client_max_body_size 20m;
    proxy_intercept_errors on;

    location / {{
        root /app/frontend-build/;
        index index.html;
        add_header Cache-Control "no-cache";
        try_files $uri $uri/ /index.html =404;
    }}

    location /assets/ {{
        root /app/frontend-build/;
        expires 7d;
        add_header Cache-Control "public";
    }}

    location /mion/ {{
        root /app/frontend-build/;
        expires 7d;
        add_header Cache-Control "public";
    }}

    location /media/ {{
        alias /app/data/media/;
        expires 1d;
        add_header Cache-Control "public";
    }}

    location /m/ {{
        alias /app/data/m/;
        expires 1d;
        add_header Cache-Control "public";
    }}

    location /t/ {{
        alias /app/data/upload/;
        expires 1d;
        add_header Cache-Control "public";
    }}

    location /service/ {{
        proxy_pass      http://backend_worker;
        proxy_redirect $host/ $http_host/;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
    }}

    location /service/ws {{
        proxy_pass      http://backend_worker/service/ws;
        proxy_http_version 1.1;
        proxy_redirect $host/ $http_host/;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;

        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }}

    location {admin_url}/ {{
        if ($cookie_admin_2fa != '{admin_2fa}') {{
            return 404;
        }}
        proxy_pass      http://backend_admin{admin_url}/;
        proxy_redirect $host/ $http_host/;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
    }}

    location {admin_url}/admin/static/ {{
        proxy_pass      http://backend_admin{admin_url}/admin/static/;
        proxy_redirect $host/ $http_host/;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;

        expires 1d;
        add_header Cache-Control "public";
    }}
}}
"""

worker_config_str = ''

for i in range(secret.N_WORKERS):
    worker_config = secret.WORKER_API_SERVER_KWARGS(i)
    worker_config_str += '    server {}:{} fail_timeout=0s;\n'.format(worker_config['host'], worker_config['port'])

print(
    CONFIG_TEMPLATE.format(
        admin_ip=secret.REDUCER_ADMIN_SERVER_ADDR[0],
        admin_port=secret.REDUCER_ADMIN_SERVER_ADDR[1],
        worker_config=worker_config_str,
        admin_url=secret.ADMIN_URL,
        admin_2fa=secret.ADMIN_2FA_COOKIE,
    )
)
