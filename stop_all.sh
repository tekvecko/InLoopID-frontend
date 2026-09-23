#!/usr/bin/env bash

echo "=== Zastavování služeb InloopID ==="

if pgrep -f "celery -A celery_app" > /dev/null; then
    pkill -f "celery -A celery_app"
    echo "✓ Celery worker zastaven."
fi

if pgrep -f "python app.py" > /dev/null; then
    pkill -f "python app.py"
    echo "✓ Flask backend zastaven."
fi

if pgrep -f "vite" > /dev/null; then
    pkill -f "vite"
    echo "✓ Frontend server zastaven."
fi

echo "---"
read -p "Chceš zastavit i Redis server? (y/N): " stop_redis
if [[ "$stop_redis" =~ ^[Yy]$ ]]; then
    redis-cli shutdown 2>/dev/null || pkill -x "redis-server"
    echo "✓ Redis server zastaven."
fi

echo "Služby byly korektně ukončeny."
