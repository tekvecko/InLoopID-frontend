import os

# Detekce přesného umístění backendových souborů
app_path = "/data/data/com.termux/files/home/InloopID/backend/app.py"
if not os.path.exists(app_path):
    app_path = "/data/data/com.termux/files/home/InloopID/app.py"

req_path = "/data/data/com.termux/files/home/InloopID/backend/requirements.txt"
if not os.path.exists(req_path):
    req_path = "/data/data/com.termux/files/home/InloopID/requirements.txt"

# 1. Úprava app.py pro dynamické načítání DATABASE_URL
with open(app_path, "r") as f:
    content = f.read()

old_db = "app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inloopid.db'"
new_db = "app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///inloopid.db')"

if old_db in content:
    content = content.replace(old_db, new_db)
    with open(app_path, "w") as f:
        f.write(content)
    print("[+] Aplikace modifikována: Přidána podpora pro dynamický routing databáze.")
else:
    print("[-] Parametr databáze nebyl nalezen, nebo již byl upraven.")

# 2. Instalace ovladače pro PostgreSQL
with open(req_path, "r") as f:
    reqs = f.read()

if "psycopg2-binary" not in reqs:
    with open(req_path, "a") as f:
        f.write("\npsycopg2-binary==2.9.9\n")
    print("[+] Soubor požadavků aktualizován: Přidán ovladač psycopg2-binary.")
