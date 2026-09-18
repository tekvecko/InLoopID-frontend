#!/bin/bash
set -e

echo "=========================================================="
echo " INLOOPID - APLIKACE DEBUG ROADMAPY (FÁZE 1)"
echo "=========================================================="

echo "[*] Instaluji PyJWT pro asymetrickou validaci tokenů..."
pip install PyJWT cryptography > /dev/null 2>&1

python3 << 'PY_EOF'
import os
import re

# 1. Oprava Case Sensitivity (Roadmap Bod 3)
bc_path = os.path.expanduser("~/InloopID/backend/blockchain_anchor.py")
if os.path.exists(bc_path):
    os.system(f"cp '{bc_path}' '{bc_path}.bak_roadmap'")
    with open(bc_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Nahrazení chybného InLoopID za InloopID
    content = content.replace("~/InLoopID/", "~/InloopID/")
    
    with open(bc_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("[+] Bod 3: Cesty v blockchain_anchor.py byly sjednoceny na lowercase 'l'.")

# 2. Hardening CSP (Roadmap Bod 2)
app_path = os.path.expanduser("~/InloopID/backend/app.py")
if os.path.exists(app_path):
    os.system(f"cp '{app_path}' '{app_path}.bak_roadmap'")
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Chirurgické odstranění 'unsafe-inline' pro striktní XSS obranu
    if "'unsafe-inline'" in content:
        content = content.replace(" 'unsafe-inline'", "")
        with open(app_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("[+] Bod 2: CSP hlavičky v app.py byly zbaveny unsafe-inline direktiv.")
PY_EOF

echo "=========================================================="
echo " ZÁKLADNÍ BEZPEČNOSTNÍ HARDENING DOKONČEN."
echo " Architektura je připravena k refaktoringu JWT validace."
echo "=========================================================="
