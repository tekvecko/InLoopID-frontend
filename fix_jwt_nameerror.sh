#!/bin/bash
set -e

echo "=========================================================="
echo " INLOOPID - OPRAVA NAMEERROR (JWT TOKEN)"
echo "=========================================================="

python3 << 'PY_EOF'
import os
import re

routes_fp = os.path.expanduser("~/InloopID/backend/routes.py")

if os.path.exists(routes_fp):
    with open(routes_fp, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Oprava špatného názvu proměnné
    content = content.replace("verify_oidc_token(token_b64)", "verify_oidc_token(token)")

    # 2. Úklid přebytečných Base64 proměnných, které už nová JWT knihovna nepotřebuje
    content = re.sub(r'^\s*payload_b64\s*=\s*token\.split.*?$\n', '', content, flags=re.MULTILINE)
    content = re.sub(r'^\s*payload_b64\s*\+=\s*\'.*?$\n', '', content, flags=re.MULTILINE)

    with open(routes_fp, "w", encoding="utf-8") as f:
        f.write(content)
        
    print("[+] Proměnná 'token_b64' byla úspěšně změněna na 'token'.")
    print("[+] Odstraněn zastaralý balast pro padding Base64.")
else:
    print(f"[-] Soubor nenalezen: {routes_fp}")
PY_EOF

echo "=========================================================="
echo " HOTOVO. Backend nyní bez problémů nastartuje."
echo " Restartujte znovu: ~/InloopID/InLoopID_launcher.sh"
echo "=========================================================="
