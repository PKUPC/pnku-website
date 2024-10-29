FROM node:20 AS frontend_builder

WORKDIR /app

RUN npm install -g pnpm

COPY ./frontend/package.json ./
COPY ./frontend/pnpm-lock.yaml ./

RUN pnpm install

COPY ./frontend/ ./

RUN pnpm build

FROM python:3.11-slim-bookworm

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    nginx-extras libnginx-mod-http-brotli-filter libnginx-mod-http-brotli-static\
    && rm -rf /var/lib/apt/lists/*

RUN rm /etc/nginx/sites-enabled/default
COPY ./docker-assets/nginx.conf /etc/nginx/

WORKDIR /app

COPY ./docker-assets/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN mkdir -p /app/backend
COPY ./backend/requirements.txt /app/backend/requirements.txt
RUN pip3 install -r /app/backend/requirements.txt

COPY ./backend /app/backend

COPY --from=frontend_builder /app/build /app/frontend-build

ENTRYPOINT ["/entrypoint.sh"]
