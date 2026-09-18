import os

app_path = "/data/data/com.termux/files/home/InloopID/backend/app.py"
if not os.path.exists(app_path):
    app_path = "/data/data/com.termux/files/home/InloopID/app.py"

with open(app_path, "r") as f:
    content = f.read()

header_code = """
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    # CSP: Povolí skripty jen z naší domény a zablokuje cizí iframy a eval()
    response.headers['Content-Security-Policy'] = "default-src 'self' http://localhost:*; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self' http://localhost:* ws://localhost:*;"
    return response
"""

if "def add_security_headers" not in content:
    # Vložíme kód před if __name__ == '__main__':
    content = content.replace("if __name__ == '__main__':", header_code + "\nif __name__ == '__main__':")
    with open(app_path, "w") as f:
        f.write(content)
    print("[+] KROK 2.1 HOTOV: CSP a bezpečnostní hlavičky (XSS obrana) byly přidány do app.py.")
else:
    print("[-] Hlavičky již existují.")
