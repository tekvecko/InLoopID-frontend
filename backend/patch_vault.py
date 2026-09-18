import re
import textwrap

file_path = "/data/data/com.termux/files/home/InloopID/backend/routes.py"

with open(file_path, 'r') as f:
    content = f.read()

# Bezpečné odebrání staré funkce employee_vault
content = re.sub(r"@api_bp\.route\('/employee/vault'.*?(?=@api_bp\.route|\Z)", "", content, flags=re.DOTALL)

new_code = """
@api_bp.route('/employee/vault', methods=['GET'])
def employee_vault():
    from flask import request, jsonify
    import base64, json
    from models import VerifiableCredentialAnchor, IdentityNode

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Chybí ověřovací token MojeID"}), 401

    try:
        token_b64 = auth_header.split(' ')[1]
        claims = json.loads(base64.b64decode(token_b64).decode('utf-8'))
        email_hash = claims.get('email_hash')
        
        name = f"{claims.get('first_name', '')} {claims.get('last_name', '')}".strip()
        if not name: name = claims.get('email')

        identity = IdentityNode.query.filter_by(email_hash=email_hash).first()
        subject_dids = [f"pending:{email_hash}"]
        if identity:
            subject_dids.append(identity.did_uri)

        documents = VerifiableCredentialAnchor.query.filter(
            VerifiableCredentialAnchor.subject_did.in_(subject_dids)
        ).order_by(VerifiableCredentialAnchor.created_at.desc()).all()

        doc_list = []
        for d in documents:
            doc_list.append({
                "id": d.credential_id,
                "status": d.status,
                "encrypted_payload": d.encrypted_payload,
                "created_at": d.created_at.isoformat()
            })

        return jsonify({
            "name": name,
            "email": claims.get('email'),
            "documents_count": len(documents),
            "documents": doc_list
        }), 200
    except Exception as e:
        return jsonify({"error": f"Neplatný token: {str(e)}"}), 400

@api_bp.route('/employee/sign-contract', methods=['POST'])
def sign_contract():
    from flask import request, jsonify
    import base64, json
    from models import VerifiableCredentialAnchor, IdentityNode, BlindAuditLog, db

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Chybí token"}), 401
        
    try:
        token_b64 = auth_header.split(' ')[1]
        claims = json.loads(base64.b64decode(token_b64).decode('utf-8'))
        email_hash = claims.get('email_hash')
        
        identity = IdentityNode.query.filter_by(email_hash=email_hash).first()
        subject_dids = [f"pending:{email_hash}"]
        if identity: subject_dids.append(identity.did_uri)

        data = request.get_json()
        contract = VerifiableCredentialAnchor.query.filter_by(credential_id=data['contract_id']).first()
        
        if contract and contract.subject_did in subject_dids:
            contract.status = 'signed'
            db.session.add(BlindAuditLog(action=f"CONTRACT_SIGNED_{contract.credential_id}", actor_did=contract.subject_did))
            db.session.commit()
            return jsonify({"status": "success"}), 200
            
        return jsonify({"error": "Smlouva nenalezena nebo nemáte přístup."}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 400
"""

with open(file_path, 'w') as f:
    f.write(content.strip() + "\n\n" + textwrap.dedent(new_code).strip() + "\n")

print("[+] Backend API rozšířeno o stahování a podpis smluv.")
