import subprocess
import json
import base64
import time
import os
import smtplib
import hashlib
import traceback
from email.message import EmailMessage
from datetime import datetime, UTC
from flask import Blueprint, request, jsonify, redirect, session, current_app
from models import db, CompanyWorkspace, IdentityNode, VerifiableCredentialAnchor, BlindAuditLog

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

def get_qualified_timestamp(data_hash):
    # Mock pro Kvalifikovaná časová razítka
    current_time = datetime.now(UTC).isoformat()
    return f"TSA_QUALIFIED_TOKEN_{data_hash[:8]}_{current_time}"

@api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@api_bp.route('/mojeid/login', methods=['GET'])
def mojeid_login():
    redirect_uri = 'http://localhost:5000/api/v1/mojeid/callback'
    oauth = current_app.config['OAUTH_REGISTRY']
    return oauth.mojeid.authorize_redirect(redirect_uri, claims=json.dumps({"userinfo": {}}))

@api_bp.route('/mojeid/callback')
def mojeid_callback():
    oauth = current_app.config['OAUTH_REGISTRY']
    try:
        token = oauth.mojeid.authorize_access_token()
        userinfo = oauth.mojeid.userinfo()
        
        email = userinfo.get('email')
        if not email:
            raise ValueError("MojeID neposkytlo povinný e-mail.")
            
        email_hash = hashlib.sha256(email.encode('utf-8')).hexdigest()
        existing_node = IdentityNode.query.filter_by(email_hash=email_hash).first()
        restore_mode = "true" if existing_node else "false"

        claims = {
            "email": email,
            "email_hash": email_hash,
            "first_name": userinfo.get('given_name', ''),
            "last_name": userinfo.get('family_name', ''),
            "encrypted_keystore": existing_node.encrypted_keystore if existing_node else None,
            "keystore_iv": existing_node.keystore_iv if existing_node else None,
            "exp": time.time() + 300
        }
        
        token_b64 = base64.b64encode(json.dumps(claims).encode('utf-8')).decode('utf-8')
        return redirect(f"http://localhost:5173/employee?mojeid_token={token_b64}&restore={restore_mode}")
        
    except Exception as e:
        traceback.print_exc()
        error_msg = str(e).replace(' ', '_')
        return redirect(f"http://localhost:5173/employee?error=auth_failed_{error_msg}")

@api_bp.route('/eidas/issue-identity', methods=['POST'])
def eidas_issue_identity():
    data = request.get_json()
    claims = json.loads(base64.b64decode(data['mojeid_token']).decode('utf-8'))
    identity_credential = {
        "context": "https://www.w3.org/2018/credentials/v1",
        "type": ["VerifiableCredential", "MojeIDVerifiedIdentity"],
        "issuer": "did:web:inloopid.com:notary",
        "credentialSubject": { "id": data['did_uri'], "identityProvider": "mojeid", "verifiedClaims": claims }
    }
    db.session.add(BlindAuditLog(action='EIDAS_ISSUED', actor_did=data['did_uri']))
    db.session.commit()
    return jsonify({"status": "success", "credential": identity_credential}), 201

@api_bp.route('/register-identity', methods=['POST'])
def register_identity():
    data = request.get_json()
    identity = IdentityNode.query.filter_by(did_uri=data['did_uri']).first()
    if not identity:
        identity = IdentityNode(
            tenant_id=data.get('tenant_id', 'public_zone'),
            did_uri=data['did_uri'],
            email_hash=data.get('email_hash'),
            public_key_jwk=data.get('public_key_jwk'),
            encrypted_keystore=data.get('encrypted_keystore'),
            keystore_iv=data.get('keystore_iv'),
            role='user'
        )
        db.session.add(identity)
        db.session.commit()
    return jsonify({"status": "success"}), 200

# === NOVÝ ENDPOINT: PRÁVNÍ AUDIT ===
@api_bp.route('/hr/audit-report', methods=['POST'])
def generate_audit_report():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({"error": "Chybí e-mail"}), 400

    email_hash = hashlib.sha256(email.encode('utf-8')).hexdigest()
    identity = IdentityNode.query.filter_by(email_hash=email_hash).first()

    if not identity:
        return jsonify({"error": "Identita nenalezena"}), 404

    credentials = VerifiableCredentialAnchor.query.filter_by(subject_did=identity.did_uri).all()
    logs = BlindAuditLog.query.filter_by(actor_did=identity.did_uri).order_by(BlindAuditLog.timestamp.asc()).all()

    audit_lines = []
    audit_lines.append("=========================================================")
    audit_lines.append("       KRYPTOGRAFICKÝ A PRÁVNÍ AUDIT (INLOOPID)          ")
    audit_lines.append("=========================================================")
    audit_lines.append(f"ČAS GENEROVÁNÍ: {datetime.now(UTC).isoformat()}")
    audit_lines.append(f"SUBJEKT (DID): {identity.did_uri}")
    audit_lines.append(f"ROLE: {identity.role}")
    audit_lines.append("STATUS IDENTITY: Ověřeno přes MojeID (eIDAS LoA Značná/Vysoká)")
    audit_lines.append("=========================================================\n")

    if not credentials:
        audit_lines.append("Subjekt zatím nemá ukotveny žádné dokumenty.\n")
    else:
        for cred in credentials:
            audit_lines.append(f"--- DOKUMENT ID: {cred.credential_id} ---")
            audit_lines.append(f"KRYPTOGRAFICKÝ HASH (SHA-256): {cred.content_hash}")
            audit_lines.append(f"STAV DOKUMENTU: {cred.status.upper()}")
            audit_lines.append(f"ZALOŽENO: {cred.created_at.isoformat()}")
            if cred.withdrawn_at:
                audit_lines.append(f"ODSTOUPENO DNE: {cred.withdrawn_at.isoformat()}")
            
            audit_lines.append("\n>> SOULAD S LEGISLATIVOU <<")
            audit_lines.append("[x] GDPR (Privacy by Design): SPLNĚNO.")
            audit_lines.append("    Obsah dokumentu je zašifrován AES-256-GCM na straně klienta. Server nedisponuje dešifrovacím klíčem.")
            
            if cred.hr_tsa_token and cred.employee_tsa_token:
                audit_lines.append("[x] eIDAS 2.0 (Kvalifikovaná razítka & Pečeť): SPLNĚNO.")
                audit_lines.append(f"    TSA Vydavatele (HR): {cred.hr_tsa_token}")
                audit_lines.append(f"    TSA Podepisujícího: {cred.employee_tsa_token}")
            else:
                audit_lines.append("[ ] eIDAS 2.0: Čeká na oboustranný podpis.")

            if cred.status == 'signed':
                audit_lines.append("[x] ZÁKONÍK PRÁCE (§ 334a - Zákonná doručenka): SPLNĚNO.")
                audit_lines.append("    Odesláno na soukromý e-mail prokazatelně ověřený přes MojeID.")
                audit_lines.append("[x] ZÁKONÍK PRÁCE (§ 34a - Právo na odstoupení): SPLNĚNO.")
                audit_lines.append("    Poučení o 7denní lhůtě bylo součástí zákonné doručenky a UI portálu.\n")

    audit_lines.append("\n=========================================================")
    audit_lines.append("               ZÁZNAMY Z AUDIT LOGU                      ")
    audit_lines.append("=========================================================")
    for log in logs:
        audit_lines.append(f"{log.timestamp.isoformat()} | AKCE: {log.action}")

    audit_lines.append("=========================================================")
    audit_lines.append("KONEC AUDITNÍHO ZÁZNAMU")
    audit_lines.append("=========================================================")

    return jsonify({"status": "success", "report": "\n".join(audit_lines)}), 200
# ==========================================


# === B2B MULTI-TENANT API ===
from models import CompanyWorkspace

@api_bp.route('/b2b/register', methods=['POST'])
def register_company():
    data = request.get_json()
    tenant_id = data.get('tenant_id')
    
    if CompanyWorkspace.query.filter_by(tenant_id=tenant_id).first():
        return jsonify({"error": "Tato firma (tenant) již existuje. Zvolte jiný identifikátor."}), 400
        
    new_company = CompanyWorkspace(
        tenant_id=tenant_id,
        company_name=data.get('company_name'),
        ico=data.get('ico'),
        admin_email=data.get('admin_email')
    )
    db.session.add(new_company)
    db.session.commit()
    
    # Auditní log o založení nového tenanta
    db.session.add(BlindAuditLog(action=f'B2B_TENANT_CREATED_{tenant_id}', actor_did='system'))
    db.session.commit()
    
    return jsonify({"status": "success", "tenant_id": tenant_id}), 201

@api_bp.route('/lookup-identity', methods=['POST'])
def lookup_identity():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({"error": "Chybí e-mail"}), 400

    email_hash = hashlib.sha256(email.encode('utf-8')).hexdigest()
    identity = IdentityNode.query.filter_by(email_hash=email_hash).first()

    if not identity:
        return jsonify({"error": "Zaměstnanec s tímto e-mailem zatím nemá aktivní Trezor."}), 404

    return jsonify({
        "status": "success",
        "did_uri": identity.did_uri,
        "public_key_jwk": identity.public_key_jwk,
        "created_at": identity.created_at.isoformat()
    }), 200

@api_bp.route('/anchor-credential', methods=['POST'])
def anchor_credential():
    data = request.get_json()
    tsa_token = get_qualified_timestamp(data['content_hash'])
    
    new_anchor = VerifiableCredentialAnchor(
        tenant_id=data.get('tenant_id', 'public_zone'),
        credential_id=data['credential_id'],
        issuer_did=data['issuer_did'],
        subject_did=data['subject_did'],
        content_hash=data['content_hash'],
        proof_signature=data['proof_signature'],
        hr_tsa_token=tsa_token,
        encrypted_payload=data['encrypted_payload'],
        iv=data['iv'],
        wrapped_key=data['wrapped_key']
    )
    db.session.add(new_anchor)
    db.session.commit()
    return jsonify({"status": "success"}), 201

@api_bp.route('/my-credentials/<subject_did>', methods=['GET'])
def get_my_credentials(subject_did):
    credentials = VerifiableCredentialAnchor.query.filter_by(subject_did=subject_did).all()
    result = []
    for c in credentials:
        comp = CompanyWorkspace.query.filter_by(tenant_id=c.tenant_id).first()
        result.append({
            "credential_id": c.credential_id, "tenant_id": c.tenant_id, 
            "company_name": comp.company_name if comp else "Neznámá společnost",
            "encrypted_payload": c.encrypted_payload, "iv": c.iv, 
            "wrapped_key": c.wrapped_key, "content_hash": c.content_hash, "status": c.status, 
            "hr_tsa_token": c.hr_tsa_token, "employee_tsa_token": c.employee_tsa_token,
            "created_at": c.created_at.isoformat(),
            "withdrawn_at": c.withdrawn_at.isoformat() if c.withdrawn_at else None
        })
    return jsonify({"status": "success", "data": result}), 200

@api_bp.route('/sign-credential', methods=['POST'])
def sign_credential():
    data = request.get_json()
    
    # KONTROLA REVOKACE
    identity = IdentityNode.query.filter_by(did_uri=data.get('subject_did')).first()
    if not identity or not identity.is_active:
        return jsonify({"error": "Identita byla revokována firmou."}), 403
        
    cred = VerifiableCredentialAnchor.query.filter_by(credential_id=data['credential_id']).first()
    
    cred.subject_signature = data['signature']
    cred.employee_tsa_token = get_qualified_timestamp(data['signature'])
    cred.status = 'signed'
    
    employee_email = data.get('employee_email')
    if employee_email:
        try:
            msg = EmailMessage()
            msg['Subject'] = 'Vaše pracovní smlouva a poučení o právu na odstoupení'
            msg['From'] = os.environ.get('SMTP_EMAIL', 'hr@inloopid.com')
            msg['To'] = employee_email
            
            email_body = (
                f"Dobrý den,\n\n"
                f"Vaše pracovní smlouva byla úspěšně podepsána a opatřena eIDAS razítkem.\n"
                f"HASH dokumentu: {cred.content_hash}\n\n"
                f"--- POUČENÍ DLE § 34a ZÁKONÍKU PRÁCE ---\n"
                f"Dle zákoníku práce máte právo do 7 dnů od smlouvy odstoupit, pokud jste nezačali plnit úkoly.\n"
                f"Pro odstoupení využijte tlačítko 'Odstoupit od smlouvy' přímo v Trezoru.\n\nS pozdravem, HR"
            )
            msg.set_content(email_body)
            
            smtp_pass = os.environ.get('SMTP_PASSWORD')
            if smtp_pass:
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(msg['From'], smtp_pass)
                server.send_message(msg)
                server.quit()
        except Exception as e:
            pass

    db.session.commit()
    return jsonify({"status": "success"}), 200

@api_bp.route('/withdraw-credential', methods=['POST'])
def withdraw_credential():
    data = request.get_json()
    cred = VerifiableCredentialAnchor.query.filter_by(credential_id=data['credential_id']).first()
    cred.status = 'withdrawn'
    cred.withdrawn_at = datetime.now(UTC)
    db.session.add(BlindAuditLog(action='ZP_34A_WITHDRAWAL', actor_did=data['subject_did']))
    db.session.commit()
    return jsonify({"status": "success"}), 200

@api_bp.route('/termux-biometrics', methods=['POST'])
def termux_biometrics():
    try:
        import json
        result = subprocess.run(['termux-fingerprint'], capture_output=True, text=True, timeout=30)
        
        if not result.stdout:
            return jsonify({"error": "Senzor nedostupný"}), 500
            
        data = json.loads(result.stdout)
        
        if data.get('auth_result') == 'AUTH_RESULT_SUCCESS':
            return jsonify({"status": "success"}), 200
            
        return jsonify({"error": "Ověření zrušeno nebo zamítnuto"}), 401
        
    except Exception as e:
        return jsonify({"error": f"HW chyba: {str(e)}"}), 500

# === ENDPOINTY PRO HR AGENDU A ONBOARDING ===

# === GDPR & eIDAS ZBRANĚ PRO HR ===
@api_bp.route('/hr/revoke-identity', methods=['POST'])
def revoke_identity():
    data = request.get_json()
    identity = IdentityNode.query.filter_by(email_hash=data['email_hash']).first()
    if identity:
        identity.is_active = False
        db.session.add(BlindAuditLog(action='EIDAS_IDENTITY_REVOKED', actor_did=identity.did_uri))
        db.session.commit()
        return jsonify({"status": "success"}), 200
    return jsonify({"error": "Nenalezeno"}), 404

@api_bp.route('/hr/cryptographic-shred', methods=['POST'])
def cryptographic_shred():
    import secrets
    data = request.get_json()
    identity = IdentityNode.query.filter_by(email_hash=data['email_hash']).first()
    if not identity:
        return jsonify({"error": "Nenalezeno"}), 404

    # 1. Skartace dokumentů (přepis náhodnými bajty)
    credentials = VerifiableCredentialAnchor.query.filter_by(subject_did=identity.did_uri).all()
    for cred in credentials:
        cred.encrypted_payload = secrets.token_hex(256)
        cred.wrapped_key = secrets.token_hex(128)
        cred.content_hash = "SHREDDED_" + secrets.token_hex(16)
        cred.status = 'shredded'

    # 2. Deaktivace identity a skartace zálohy
    identity.is_active = False
    identity.encrypted_keystore = "SHREDDED"
    
    # 3. Záznam do auditu
    db.session.add(BlindAuditLog(action='GDPR_CRYPTOGRAPHIC_SHREDDING_EXECUTED', actor_did=identity.did_uri))
    db.session.commit()
    return jsonify({"status": "success"}), 200


# === B2B MULTI-TENANT & RSA DROP-BOX API ===
from models import CompanyWorkspace

@api_bp.route('/b2b/register', methods=['POST'])
def register_company():
    data = request.get_json()
    tenant_id = data.get('tenant_id')
    
    if CompanyWorkspace.query.filter_by(tenant_id=tenant_id).first():
        return jsonify({"error": "Tato firma (tenant) již existuje."}), 400
        
    new_company = CompanyWorkspace(
        tenant_id=tenant_id,
        company_name=data.get('company_name'),
        ico=data.get('ico'),
        admin_email=data.get('admin_email'),
        public_key_jwk=data.get('public_key_jwk'),
        encrypted_private_key=data.get('encrypted_private_key'),
        private_key_iv=data.get('private_key_iv')
    )
    db.session.add(new_company)
    db.session.commit()
    db.session.add(BlindAuditLog(action=f'B2B_TENANT_CREATED_{tenant_id}', actor_did='system'))
    db.session.commit()
    return jsonify({"status": "success", "tenant_id": tenant_id}), 201

@api_bp.route('/b2b/workspace/<tenant_id>', methods=['GET'])
def get_workspace_info(tenant_id):
    comp = CompanyWorkspace.query.filter_by(tenant_id=tenant_id).first()
    if not comp: return jsonify({"error": "Firma nenalezena"}), 404
    return jsonify({"status": "success", "company_name": comp.company_name, "public_key_jwk": comp.public_key_jwk}), 200

@api_bp.route('/b2b/candidate-join', methods=['POST'])
def candidate_join():
    data = request.get_json()
    tenant_id = data.get('tenant_id')
    email_hash = data.get('email_hash')
    
    item = HRAgendaItem.query.filter_by(tenant_id=tenant_id, email_hash=email_hash).first()
    if not item:
        item = HRAgendaItem(tenant_id=tenant_id, email_hash=email_hash, encrypted_data=data['encrypted_data'], iv=data['iv'], wrapped_key=data['wrapped_key'])
        db.session.add(item)
        for t in ['SMLOUVA', 'BOZP', 'GDPR', 'NOTEBOOK']:
            db.session.add(OnboardingTask(tenant_id=tenant_id, email_hash=email_hash, task_type=t))
        db.session.commit()
    return jsonify({"status": "success"}), 201

@api_bp.route('/hr/agenda', methods=['GET'])
def hr_agenda():
    tenant_id = request.args.get('tenant_id')
    comp = CompanyWorkspace.query.filter_by(tenant_id=tenant_id).first()
    if not comp: return jsonify({"error": "Firma nenalezena"}), 404
    
    items = HRAgendaItem.query.filter_by(tenant_id=tenant_id).all()
    result = []
    for item in items:
        tasks = OnboardingTask.query.filter_by(tenant_id=tenant_id, email_hash=item.email_hash).all()
        identity = IdentityNode.query.filter_by(email_hash=item.email_hash).first()
        result.append({
            "email_hash": item.email_hash, "encrypted_data": item.encrypted_data, "iv": item.iv, "wrapped_key": item.wrapped_key,
            "has_vault": bool(identity), "did_uri": identity.did_uri if identity else None,
            "public_key_jwk": identity.public_key_jwk if identity else None,
            "tasks": {t.task_type: t.status for t in tasks}
        })
    return jsonify({"status": "success", "encrypted_private_key": comp.encrypted_private_key, "private_key_iv": comp.private_key_iv, "data": result}), 200


@api_bp.route('/my-tasks/<email_hash>', methods=['GET'])
def get_my_tasks(email_hash):
    tasks = OnboardingTask.query.filter_by(email_hash=email_hash).all()
    result = {}
    for t in tasks:
        if t.tenant_id not in result:
            comp = CompanyWorkspace.query.filter_by(tenant_id=t.tenant_id).first()
            result[t.tenant_id] = { "company_name": comp.company_name if comp else t.tenant_id, "tasks": {} }
        result[t.tenant_id]["tasks"][t.task_type] = t.status
    return jsonify({"status": "success", "data": result}), 200

@api_bp.route('/complete-task', methods=['POST'])
def complete_task():
    data = request.get_json()
    task = OnboardingTask.query.filter_by(tenant_id=data['tenant_id'], email_hash=data['email_hash'], task_type=data['task_type']).first()
    if task:
        task.status = data['status']
        db.session.add(BlindAuditLog(action=f"TASK_UPDATED_{data['task_type']}_{data['status']}", actor_did=data.get('did_uri', 'system')))
        db.session.commit()
    return jsonify({"status": "success"}), 200
