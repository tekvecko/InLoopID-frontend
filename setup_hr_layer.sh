#!/bin/bash
set -e

echo "=========================================================="
echo " INLOOPID - SEPARACE HR API VRSTVY (BLUEPRINT)"
echo "=========================================================="

# 1. Vytvoření izolovaného Blueprintu pro HR
cat << 'PY_EOF' > ~/InloopID/backend/hr_routes.py
from flask import Blueprint, jsonify, request
from models import VerifiableCredentialAnchor

hr_bp = Blueprint('hr', __name__)

@hr_bp.route('/api/v1/hr/contracts', methods=['GET'])
def get_encrypted_contracts():
    # Tento endpoint vrací data pro klientské dešifrování v prohlížeči.
    # POZOR: Server neprovádí žádné dešifrování, pouze servíruje bloby.
    
    # Zde by v produkci byla kontrola JWT tokenu HR pracovníka
    # if not is_authorized_hr(request): return jsonify({"error": "Unauthorized"}), 403

    anchors = VerifiableCredentialAnchor.query.all()
    
    contracts_payload = []
    for anchor in anchors:
        contracts_payload.append({
            "credential_id": anchor.credential_id,
            "subject_did": anchor.subject_did,
            "encrypted_payload": anchor.encrypted_payload,
            "iv": anchor.iv,
            "wrapped_key": anchor.wrapped_key,
            "status": anchor.status,
            "timestamp": anchor.hr_tsa_token
        })

    return jsonify({"status": "success", "data": contracts_payload}), 200
PY_EOF
echo "[+] Vytvořen soubor hr_routes.py"

# 2. Bezpečná registrace Blueprintu do app.py
python3 << 'PY_EOF'
import os

fp = os.path.expanduser("~/InloopID/backend/app.py")
with open(fp, "r", encoding="utf-8") as f:
    content = f.read()

# Zkontrolujeme, zda už není registrován
if "hr_bp" not in content:
    # Přidáme import za stávající routes
    content = content.replace(
        "from routes import api_bp", 
        "from routes import api_bp\nfrom hr_routes import hr_bp"
    )
    # Zaregistrujeme blueprint pod api_bp
    content = content.replace(
        "app.register_blueprint(api_bp)", 
        "app.register_blueprint(api_bp)\napp.register_blueprint(hr_bp)"
    )
    
    with open(fp, "w", encoding="utf-8") as f:
        f.write(content)
    print("[+] Blueprint 'hr_bp' úspěšně zaregistrován do app.py")
else:
    print("[!] Blueprint 'hr_bp' již je v app.py registrován.")
PY_EOF

echo "=========================================================="
echo " HOTOVO. Pro načtení nové logiky restartujte server."
echo "=========================================================="
