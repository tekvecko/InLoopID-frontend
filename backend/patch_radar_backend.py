import os, re, sys

print("=== INLOOPID: Update Backendu (Hlídač Expirací) ===")

# --- 1. Úprava models.py ---
models_path = "/data/data/com.termux/files/home/InloopID/backend/models.py"
with open(models_path, "r") as f: models_content = f.read()

if "valid_until = db.Column" not in models_content:
    models_content = models_content.replace(
        "status = db.Column(db.String(50), default='anchored')",
        "status = db.Column(db.String(50), default='anchored')\n    valid_until = db.Column(db.DateTime, nullable=True)"
    )
    with open(models_path, "w") as f: f.write(models_content)
    print("[+] Model VerifiableCredentialAnchor rozšířen o 'valid_until'.")

# --- 2. Úprava routes.py ---
routes_path = "/data/data/com.termux/files/home/InloopID/backend/routes.py"
with open(routes_path, "r") as f: routes_content = f.read()

# a) Přidání zpracování valid_until do ukládání smlouvy
if "valid_until_dt = None" not in routes_content:
    old_anchor = """        new_contract = VerifiableCredentialAnchor(
            tenant_id=tenant_id,
            credential_id=contract_id,
            issuer_did=f"did:inloop:{tenant_id}",
            subject_did=subject_did,
            content_hash=data.get('content_hash', 'HASH_PENDING'),
            proof_signature='HR_SIG_PENDING',
            hr_tsa_token=get_qualified_timestamp(data.get('content_hash', 'HASH_PENDING')),
            encrypted_payload=data.get('encrypted_payload'),
            iv=data.get('iv', 'IV_PENDING'),
            wrapped_key=data.get('wrapped_key', 'WRAPPED_KEY_PENDING'),
            status='pending_signature'
        )"""

    new_anchor = """        valid_until_dt = None
        if data.get('valid_until'):
            try:
                from datetime import datetime
                valid_until_dt = datetime.fromisoformat(data['valid_until'].replace('Z', '+00:00'))
            except:
                pass

        new_contract = VerifiableCredentialAnchor(
            tenant_id=tenant_id,
            credential_id=contract_id,
            issuer_did=f"did:inloop:{tenant_id}",
            subject_did=subject_did,
            content_hash=data.get('content_hash', 'HASH_PENDING'),
            proof_signature='HR_SIG_PENDING',
            hr_tsa_token=get_qualified_timestamp(data.get('content_hash', 'HASH_PENDING')),
            encrypted_payload=data.get('encrypted_payload'),
            iv=data.get('iv', 'IV_PENDING'),
            wrapped_key=data.get('wrapped_key', 'WRAPPED_KEY_PENDING'),
            status='pending_signature',
            valid_until=valid_until_dt
        )"""
    routes_content = routes_content.replace(old_anchor, new_anchor)

# b) Nový Právní Radar s výpočtem expirací
old_radar = r"@api_bp\.route\('/hr/compliance-radar', methods=\['GET'\]\)\ndef compliance_radar\(\):.*?return jsonify\(\{\"status\": \"success\", \"radar\": report\}\), 200"
new_radar = """@api_bp.route('/hr/compliance-radar', methods=['GET'])
def compliance_radar():
    tenant_id = request.args.get('tenant_id')
    credentials = VerifiableCredentialAnchor.query.filter_by(tenant_id=tenant_id).all()
    report = { "safe": 0, "withdrawal_risk": 0, "pending_signatures": 0, "expiring_soon": 0, "expired": 0, "details": [] }
    now = datetime.now(UTC)

    for cred in credentials:
        is_expired = False
        is_expiring_soon = False
        
        if getattr(cred, 'valid_until', None):
            vu = cred.valid_until if cred.valid_until.tzinfo else cred.valid_until.replace(tzinfo=UTC)
            delta_exp = vu - now
            if delta_exp.days < 0:
                report['expired'] += 1
                report['details'].append({"id": cred.credential_id, "state": "EXPIRED", "desc": "Platnost vypršela!"})
                is_expired = True
            elif delta_exp.days <= 30:
                report['expiring_soon'] += 1
                report['details'].append({"id": cred.credential_id, "state": "EXPIRING_SOON", "desc": f"Končí za {delta_exp.days} dnů"})
                is_expiring_soon = True

        if cred.status in ['anchored', 'pending_signature']:
            report['pending_signatures'] += 1
            if not is_expired and not is_expiring_soon:
                report['details'].append({"id": cred.credential_id, "state": "PENDING_SIGNATURE", "desc": "Čeká na podpis"})
        elif cred.status == 'signed':
            delta = now - cred.created_at.replace(tzinfo=UTC)
            if delta.days <= 7:
                report['withdrawal_risk'] += 1
                if not is_expired and not is_expiring_soon:
                    report['details'].append({"id": cred.credential_id, "state": "WITHDRAWAL_RISK", "desc": f"Lhůta ({7 - delta.days} dnů)"})
            else:
                report['safe'] += 1
                if not is_expired and not is_expiring_soon:
                    report['details'].append({"id": cred.credential_id, "state": "LOCKED_SAFE", "desc": "Platná"})

    return jsonify({"status": "success", "radar": report}), 200"""
routes_content = re.sub(old_radar, new_radar, routes_content, flags=re.DOTALL)

with open(routes_path, "w") as f: f.write(routes_content)
print("[+] API cesty upraveny pro ukládání a čtení expirací.")

