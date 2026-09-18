import os
import sqlite3

# 1. Oprava models.py
models_path = "/data/data/com.termux/files/home/InloopID/backend/models.py"
if os.path.exists(models_path):
    with open(models_path, "r") as f:
        lines = f.readlines()
    
    content_str = "".join(lines)
    if "clearance_level = db.Column" not in content_str:
        with open(models_path, "w") as f:
            for line in lines:
                f.write(line)
                # Přidá definici nového sloupce hned pod definici statusu
                if "status = db.Column" in line:
                    f.write("    clearance_level = db.Column(db.String(50), default='standard')\n")
        print("[+] models.py úspěšně opraven: přidán clearance_level.")
    else:
        print("[i] models.py již clearance_level obsahuje.")
else:
    print("[-] Nebyl nalezen soubor models.py")

# 2. Bezpečná oprava SQLite databáze
db_path = "/data/data/com.termux/files/home/InloopID/backend/instance/inloopid.db"
if not os.path.exists(db_path):
    db_path = "/data/data/com.termux/files/home/InloopID/instance/inloopid.db"

if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("ALTER TABLE verifiable_credential_anchor ADD COLUMN clearance_level VARCHAR(50) DEFAULT 'standard'")
        conn.commit()
        print("[+] Databáze úspěšně zmigrována: sloupec clearance_level byl přidán.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("[i] Sloupec v databázi již existuje.")
        else:
            print(f"[-] DB poznámka: {e}")
    finally:
        conn.close()
else:
    print("[i] Databáze zatím neexistuje, vytvoří se sama se správnými sloupci.")
