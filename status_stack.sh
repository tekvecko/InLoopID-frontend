#!/bin/bash
echo "=== STAV INLOOPID STACKU ==="

if redis-cli ping >/dev/null 2>&1; then
    echo "[OK] Redis běží"
else
    echo "[FAIL] Redis nejede"
fi

if pgrep -f "celery worker" >/dev/null 2>&1; then
    echo "[OK] Celery worker běží"
else
    echo "[FAIL] Celery nejede"
fi

if pgrep -f "app.py" >/dev/null 2>&1 || pgrep -f "waitress" >/dev/null 2>&1; then
    echo "[OK] Waitress API běží"
else
    echo "[FAIL] Waitress API nejede"
fi

if pgrep -f "vite" >/dev/null 2>&1; then
    echo "[OK] Frontend Vite běží"
else
    echo "[FAIL] Frontend Vite nejede"
fi
