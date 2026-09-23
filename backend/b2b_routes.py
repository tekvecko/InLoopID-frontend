import re
import uuid
import json
from flask import Blueprint, request, jsonify
from models import db, CompanyWorkspace

b2b_bp = Blueprint('b2b_bp', __name__)

EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

@b2b_bp.route('/api/v1/b2b/register', methods=['POST', 'OPTIONS'])
@b2b_bp.route('/api/v1/tenant/register', methods=['POST', 'OPTIONS'])
def register_b2b():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200

    data = request.get_json(silent=True) or {}
    company_name = data.get('company_name') or data.get('companyName', '').strip()
    admin_email = (data.get('admin_email') or data.get('email') or data.get('adminEmail', '')).strip()
    ico = data.get('ico')
    tariff = data.get('tariff') or data.get('subscription_plan') or data.get('plan') or 'trial'

    # 1. Kontrola povinných údajů
    if not company_name or not admin_email:
        return jsonify({"error": "Chybí povinné údaje: company_name a admin_email"}), 400

    # 2. Validace formátu e-mailu
    if not re.match(EMAIL_REGEX, admin_email):
        return jsonify({"error": "Neplatný formát e-mailové adresy"}), 400

    # 3. Kontrola duplicity registrace
    existing = CompanyWorkspace.query.filter_by(admin_email=admin_email).first()
    if existing:
        return jsonify({"error": f"B2B workspace pro e-mail '{admin_email}' již existuje."}), 409

    clean_name = ''.join(c for c in company_name.lower().replace(' ', '_') if c.isalnum() or c == '_')[:20]
    tenant_id = f"tenant_{clean_name}_{uuid.uuid4().hex[:6]}"

    dummy_jwk = json.dumps({"kty": "RSA", "alg": "RS256", "use": "sig", "n": "init_key"})
    
    pub_key = data.get('public_key_jwk') or data.get('public_key')
    if isinstance(pub_key, dict):
        pub_key = json.dumps(pub_key)
    elif not pub_key:
        pub_key = dummy_jwk

    new_workspace = CompanyWorkspace(
        tenant_id=tenant_id,
        company_name=company_name,
        ico=ico,
        admin_email=admin_email,
        public_key_jwk=pub_key,
        encrypted_private_key=data.get('encrypted_private_key', 'init_encrypted_privkey'),
        private_key_iv=data.get('private_key_iv', 'init_iv_00000000'),
        subscription_plan=tariff,
        subscription_status='active'
    )

    try:
        db.session.add(new_workspace)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Chyba uložení do databáze: {str(e)}"}), 500

    return jsonify({
        "status": "success",
        "message": "B2B workspace byl úspěšně zaregistrován.",
        "tenant_id": tenant_id,
        "company_name": company_name,
        "admin_email": admin_email,
        "subscription_plan": tariff
    }), 201
