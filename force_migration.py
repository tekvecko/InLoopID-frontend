import sqlite3
import os

# Najdeme všechny možné cesty, kde by se databáze mohla skrývat
db_paths = [
    "/data/data/com.termux/files/home/InloopID/instance/inloopid.db",
    "/data/data/com.termux/files/home/InloopID/backend/instance/inloopid.db"
]

db_found = False

for db_path in db_paths:
    if os.path.exists(db_path):
        db_found = True
        print(f"[!] Nalezena databáze na cestě: {db_path}")
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Vynutíme přidání sloupce
            print("[...] Spouštím migraci (ALTER TABLE)...")
            cursor.execute("ALTER TABLE verifiable_credential_anchors ADD COLUMN clearance_level VARCHAR(50) DEFAULT 'standard'")
            conn.commit()
            print("[+] SUKCES: Sloupec clearance_level byl úspěšně přidán do fyzické tabulky.")
            
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("[i] INFO: Sloupec clearance_level v této databázi již fyzicky existuje.")
            else:
                print(f"[-] KRITICKÁ CHYBA při migraci databáze: {e}")
        finally:
            conn.close()

if not db_found:
    print("[-] CHYBA: Databázový soubor inloopid.db nebyl nalezen ani na jedné z očekávaných cest.")
