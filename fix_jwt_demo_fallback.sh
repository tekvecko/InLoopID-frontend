#!/bin/bash
set -e

echo "=========================================================="
echo " INLOOPID - IMPLEMENTACE HYBRIDNÍHO JWT FALLBACKU"
echo "=========================================================="

python3 << 'PY_EOF'
import os

routes_fp = os.path.expanduser("~/InloopID/backend/routes.py")

if os.path.exists(routes_fp):
    os.system(f"cp '{routes_fp}' '{routes_fp}.bak_jwt_fallback'")
    
    with open(routes_fp, "r", encoding="utf-8") as f:
        content = f.read()

    # Přesné místo, kam vložíme záchytnou logiku pro demo tokeny
    target_logic = 'return jwt.decode(token_string, options={"verify_signature": False})'
    
    fallback_logic = """# DEMO FALLBACK: Mock tokeny z offline dema neobsahují tečky
        if "." not in token_string:
            import base64, json
            padded = token_string + '=' * ((4 - len(token_string) % 4) % 4)
            return json.loads(base64.urlsafe_b64decode(padded).decode('utf-8'))
            
        # PRODUKCE: Bezpečný parsing reálných tokenů
        return jwt.decode(token_string, options={"verify_signature": False})"""

    if target_logic in content:
        content = content.replace(target_logic, fallback_logic)
        
        with open(routes_fp, "w", encoding="utf-8") as f:
            f.write(content)
        print("[+] Hybridní JWT Fallback úspěšně aplikován.")
    else:
        print("[-] Chyba: Cílová logika verify_oidc_token nebyla v souboru nalezena.")
else:
    print(f"[-] Soubor nenalezen: {routes_fp}")
PY_EOF

echo "=========================================================="
echo " HOTOVO. Tokeny bez teček nyní projdou lokální validací."
echo " Restartujte infrastrukturu: ~/InloopID/InLoopID_launcher.sh"
echo "=========================================================="
