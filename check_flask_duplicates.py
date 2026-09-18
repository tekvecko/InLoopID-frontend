#!/usr/bin/env python3
import os

routes_path = os.path.expanduser("~/InloopID/backend/routes.py")
app_path = os.path.expanduser("~/InloopID/backend/app.py")

print("==========================================================")
print(" INLOOPID - DIAGNOSTIKA DUPLICIT (READ-ONLY)")
print("==========================================================")

def analyze_file(path, search_term):
    if not os.path.exists(path):
        print(f"[!] CHYBA: Soubor nenalezen: {path}")
        return
    
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    matches = []
    for i, line in enumerate(lines):
        if search_term in line:
            matches.append((i + 1, line.strip()))
            
    print(f"\n[*] Hledám '{search_term}' v souboru {os.path.basename(path)}:")
    if len(matches) == 0:
        print("  -> 0 výskytů (To může být také chyba, pokud je funkce vyžadována).")
    elif len(matches) == 1:
        print(f"  -> OK: 1 výskyt na řádku {matches[0][0]}.")
    else:
        print(f"  -> [!] KRITICKÉ: Nalezeno {len(matches)} výskytů!")
        for line_num, content in matches:
            print(f"     L{line_num}: {content}")

analyze_file(routes_path, "def register_identity")
analyze_file(routes_path, "def compliance_health_report")
analyze_file(app_path, "register_blueprint(api_bp)")

print("\n==========================================================")
