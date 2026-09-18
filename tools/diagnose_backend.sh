#!/data/data/com.termux/files/usr/bin/bash

echo "====================================================="
echo " DIAGNOSTIKA BACKENDU (FOREGROUND BĚH)"
echo "====================================================="

# 1. Bezpečné ukončení případných visících procesů
pkill -f start_prod.py 2>/dev/null || true

# 2. Start v popředí pro zachycení logů
cd ~/InloopID/backend
python3 start_prod.py
