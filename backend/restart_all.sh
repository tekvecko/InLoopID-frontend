#!/usr/bin/env bash
set -e
cd "$HOME/InloopID/backend"

echo "=== 1. Ukončování běhu starých procesů ==="
pkill -9 -f "python" || true
pkill -9 -f "redis-server" || true
sleep 1

echo "=== 2. Spuštění Redis ==="
redis-server --daemonize yes
sleep 1

echo "=== 3. Spuštění Celery Workeru a Flasku ==="
source venv/bin/activate
nohup python -m celery -A celery_app worker --loglevel=info -P solo > celery.log 2>&1 &
nohup python app.py > flask.log 2>&1 &
sleep 2

echo "=== Stav procesů ==="
pgrep -fl "redis|python|celery"
