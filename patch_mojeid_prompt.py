import os

routes_path = "/data/data/com.termux/files/home/InloopID/backend/routes.py"

if os.path.exists(routes_path):
    with open(routes_path, "r") as f:
        content = f.read()

    # Řádek, který aktuálně odesílá uživatele na MojeID
    old_line = "return current_app.config['OAUTH_REGISTRY'].mojeid.authorize_redirect('http://localhost:5000/api/v1/mojeid/callback', claims=json.dumps({\"userinfo\": {}}))"
    
    # Nový řádek obohacený o vynucený prompt
    new_line = "return current_app.config['OAUTH_REGISTRY'].mojeid.authorize_redirect('http://localhost:5000/api/v1/mojeid/callback', claims=json.dumps({\"userinfo\": {}}), prompt='login')"

    if old_line in content:
        content = content.replace(old_line, new_line)
        with open(routes_path, "w") as f:
            f.write(content)
        print("[+] Backend: routes.py upraven. MojeID nyní bude vždy vyžadovat nové přihlášení (prompt=login).")
    else:
        print("[-] Chyba: Původní řádek nebyl nalezen. Možná již byl upraven.")
else:
    print("[-] Chyba: Soubor routes.py nebyl nalezen.")
