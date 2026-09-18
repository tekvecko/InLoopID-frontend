#!/bin/bash
set -e

echo "=========================================================="
echo " INLOOPID - GENEROVÁNÍ CLOUDOVÉ INFRASTRUKTURY (DOCKER)"
echo "=========================================================="

# 1. Backend Dockerfile (Python 3.13)
cat << 'DOCKER_EOF' > ~/InloopID/backend/Dockerfile
FROM python:3.13-slim

WORKDIR /opt/inloopid/backend

# Security: Vytvoření neprivilegovaného uživatele pro běh služby
RUN useradd -m -s /bin/bash inloopid_service

# Instalace Python závislostí
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt waitress

# Kopírování aplikační logiky
COPY . .
RUN chown -R inloopid_service:inloopid_service /opt/inloopid

USER inloopid_service
EXPOSE 5000

CMD ["python3", "start_prod.py"]
DOCKER_EOF
echo "[+] Backend Dockerfile vygenerován."

# 2. Frontend Nginx konfigurace pro reverzní proxy
cat << 'NGINX_EOF' > ~/InloopID/frontend/nginx.conf
server {
    listen 80;
    server_name localhost;

    # Servírování statických React souborů
    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
    }

    # Zabezpečené směrování na backend
    location /api/ {
        proxy_pass http://backend:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
NGINX_EOF

# 3. Frontend Dockerfile (Multi-stage build pro minimální velikost)
cat << 'DOCKER_EOF' > ~/InloopID/frontend/Dockerfile
# Fáze 1: Kompilace
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Fáze 2: Produkční běh
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
DOCKER_EOF
echo "[+] Frontend Dockerfile a Nginx konfigurace vygenerována."

# 4. Docker Compose Topologie
cat << 'YAML_EOF' > ~/InloopID/docker-compose.yml
version: '3.8'

services:
  backend:
    build: 
      context: ./backend
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  frontend:
    build:
      context: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
YAML_EOF
echo "[+] Docker Compose manifest vygenerován."

echo "=========================================================="
echo " HOTOVO. Infrastruktura je připravena na synchronizaci."
echo "=========================================================="
