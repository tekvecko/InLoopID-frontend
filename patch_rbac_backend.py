import os
import sqlite3

base_dir = "/data/data/com.termux/files/home/InloopID/backend"
if not os.path.exists(base_dir):
    base_dir = "/data/data/com.termux/files/home/InloopID"

models_path = os.path.join(base_dir, "models.py")
routes_path = os.path.join(base_dir, "routes.py")

# 1. UPRAVA MODELS.PY
if os.path.exists(models_path):
    with open(models_path, "r") as f:
        models_content = f.read()

    if "clearance_level =" not in models_content:
        old_col = "status = db.Column(db.String(50), default='pending_signature')"
        new_col = "status = db.Column(db.String(50), default='pending_signature')\n    clearance_level = db.Column(db.String(50), default='standard')"
        models_content = models_content.replace(old_col, new_col)
        with open(models_path, "w") as f:
            f.write(models_content)
        print("[+] Backend: models.py aktualizován o úroveň prověrky (clearance_level).")
else:
    print("[-] models.py nenalezen.")

# 2. UPRAVA ROUTES.PY
if os.path.exists(routes_path):
    with open(routes_path, "r") as f:
        routes_content = f.read()

    changed = False
    
    # Úprava POST endpointu (vytváření smlouvy)
    if "clearance_level = data.get('clearance_level', 'standard')" not in routes_content:
        routes_content = routes_content.replace(
            "valid_until = data.get('valid_until')", 
            "valid_until = data.get('valid_until')\n    clearance_level = data.get('clearance_level', 'standard')"
        )
        routes_content = routes_content.replace(
            "valid_until=valid_until", 
            "valid_until=valid_until,\n        clearance_level=clearance_level"
        )
        changed = True

    # Úprava GET endpointu (serializace seznamu)
    if "'clearance_level': c.clearance_level" not in routes_content:
        routes_content = routes_content.replace(
            "'status': c.status", 
            "'status': c.status,\n            'clearance_level': c.clearance_level"
        )
        changed = True

    if changed:
        with open(routes_path, "w") as f:
            f.write(routes_content)
        print("[+] Backend: routes.py nyní podporuje zápis a čtení RBAC hladin.")

# 3. BEZPEČNÁ MIGRACE SQLITE DATABÁZE
db_paths = [
    "/data/data/com.termux/files/home/InloopID/instance/inloopid.db",
    "/data/data/com.termux/files/home/InloopID/backend/instance/inloopid.db"
]

db_found = False
for db_path in db_paths:
    if os.path.exists(db_path):
        db_found = True
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("ALTER TABLE contract ADD COLUMN clearance_level VARCHAR(50) DEFAULT 'standard'")
            conn.commit()
            print(f"[+] Databáze úspěšně zmigrována: Přidán sloupec clearance_level.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("[+] Databáze již sloupec clearance_level obsahuje.")
            else:
                print(f"[-] Migrace ignorována: {e}")
        finally:
            conn.close()
        break

if not db_found:
    print("[!] Lokální SQLite databáze nebyla nalezena. Vytvoří se automaticky při novém spuštění.")
