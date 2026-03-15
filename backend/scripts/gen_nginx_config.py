import sys

from pathlib import Path


sys.path.append(str((Path(__file__).parent / '..').resolve()))

from jinja2 import Template

from src import secret


CONFIG_TEMPLATE = """map $cookie_user_token $user_hash {
    "" $remote_addr;
    default $cookie_user_token;
}

upstream backend_admin {
    server {{ admin_ip }}:{{ admin_port }} fail_timeout=0s;
}

upstream backend_worker {
    hash $user_hash;
{%- for worker_config in worker_configs %}
    server {{ worker_config.host }}:{{ worker_config.port }} fail_timeout=0s;
{%- endfor %}
}

upstream backend_syncer {
    server {{ syncer_ip }}:{{ syncer_port }} fail_timeout=0s;
}

server {
    listen 80;
    server_name _;

    client_max_body_size 20m;
    proxy_intercept_errors on;

    location / {
        root /app/frontend-build/;
        index index.html;
        add_header Cache-Control "no-cache";
        try_files $uri $uri/ /index.html =404;
    }

    location /assets/ {
        root /app/frontend-build/;
        expires 7d;
        add_header Cache-Control "public";
    }

    location /mion/ {
        root /app/frontend-build/;
        expires 7d;
        add_header Cache-Control "public";
    }

    location /media/ {
        {%- if hide_media %}
        if ($cookie_admin_2fa != '{{ admin_2fa }}') {
            return 404;
        }
        {%- endif %}
        alias /app/data/media/;
        expires 1d;
        add_header Cache-Control "public";
    }

    location /m/ {
        alias /app/data/m/;
        expires 1d;
        add_header Cache-Control "public";
    }

    location /t/ {
        alias /app/data/upload/;
        expires 1d;
        add_header Cache-Control "public";
    }

    location /service/ {
        proxy_pass      http://backend_worker;
        proxy_redirect $host/ $http_host/;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
    }

    location /service/ws {
        proxy_pass      http://backend_worker/service/ws;
        proxy_http_version 1.1;
        proxy_redirect $host/ $http_host/;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;

        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    {%- if use_syncer %}

    location /service/sync {
        proxy_pass      http://backend_syncer/service/sync;
        proxy_http_version 1.1;
        proxy_redirect $host/ $http_host/;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;

        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    {%- endif %}

    location {{ admin_url }}/ {
        if ($cookie_admin_2fa != '{{ admin_2fa }}') {
            return 404;
        }
        proxy_pass      http://backend_admin{{ admin_url }}/;
        proxy_redirect $host/ $http_host/;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
    }

    location {{ admin_url }}/admin/static/ {
        proxy_pass      http://backend_admin{{ admin_url }}/admin/static/;
        proxy_redirect $host/ $http_host/;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;

        expires 1d;
        add_header Cache-Control "public";
    }
}
"""

# 生成 worker 配置列表
worker_configs = [secret.WORKER_API_SERVER_KWARGS(i) for i in range(secret.N_WORKERS)]

template = Template(CONFIG_TEMPLATE)

hide_media = secret.HASH_MEDIA_FILENAME

print(
    template.render(
        admin_ip=secret.REDUCER_ADMIN_SERVER_ADDR[0],
        admin_port=secret.REDUCER_ADMIN_SERVER_ADDR[1],
        worker_configs=worker_configs,
        admin_url=secret.ADMIN_URL,
        admin_2fa=secret.ADMIN_2FA_COOKIE,
        hide_media=hide_media,
        use_syncer=secret.USE_SYNCER,
        syncer_ip=secret.SYNCER_KWARGS['host'],
        syncer_port=secret.SYNCER_KWARGS['port'],
    )
)
