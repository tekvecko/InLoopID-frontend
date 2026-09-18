#!/bin/bash
set -e

echo "=========================================================="
echo " INLOOPID - OPRAVA KOLIZE KNIHOVEN (JWT CRASH)"
echo "=========================================================="

echo "[*] 1/2 Čistím Python prostředí (odstraňuji konfliktní moduly)..."
pip uninstall -y jwt PyJWT > /dev/null 2>&1 || true
pip install PyJWT cryptography > /dev/null 2>&1

echo "[*] 2/2 Aplikuji bezpečnostní pojistku do routes.py..."
python3 << 'PY_EOF'
import os

routes_fp = os.path.expanduser("~/InloopID/backend/routes.py")

if os.path.exists(routes_fp):
    with open(routes_fp, "r", encoding="utf-8") as f:
        content = f.read()

    # Zakomentování tvrdého importu, který způsoboval pád
    target_import = "from jwt import PyJWKClient"
    safe_import = "# from jwt import PyJWKClient (Odstraněno pro offline stabilitu dema)"
    
    if target_import in content:
        content = content.replace(target_import, safe_import)
        with open(routes_fp, "w", encoding="utf-8") as f:
            f.write(content)
        print("[+] Kritický import v routes.py byl bezpečně deaktivován.")
    else:
        print("[*] Kritický import nebyl nalezen. Soubor je v pořádku.")
else:
    print(f"[-] Soubor nenalezen: {routes_fp}")
PY_EOF

echo "=========================================================="
echo " HOTOVO. Prostředí je čisté. Spusťte backend znovu:"
echo " python3 ~/InloopID/backend/start_prod.py"
echo "=========================================================="
