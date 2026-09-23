from flask import Blueprint, jsonify, request
from models import db, VerifiableCredentialAnchor, IdentityNode
import uuid
import datetime

hr_bp = Blueprint('hr', __name__)

@hr_bp.route('/api/v1/hr/contracts', methods=['GET', 'POST'])
def handle_contracts():
    if request.method == 'POST':
        data = request.get_json() or {}

        tenant_id = data.get('tenant_id', 'demo_tenant_01')
        email = data.get('email')
        name = data.get('name')
        position = data.get('position')
        content_hash = data.get('content_hash')
        encrypted_payload = data.get('encrypted_payload')
        clearance_level = data.get('clearance_level', 'STANDARD')

        if not email or not encrypted_payload or not content_hash:
            return jsonify({"error": "Missing required fields (email, encrypted_payload, content_hash)"}), 400

        credential_id = f"contract-{uuid.uuid4()}"

        anchor = VerifiableCredentialAnchor(
            tenant_id=tenant_id,
            credential_id=credential_id,
            subject_did=f"did:inloopid:{email}",
            content_hash=content_hash,
            encrypted_payload=encrypted_payload,
            iv=data.get('iv', 'mock_iv'),
            wrapped_key=data.get('wrapped_key', 'mock_wrapped_key'),
            status='PENDING_SIGNATURE',
            clearance_level=clearance_level.lower()
        )

        try:
            db.session.add(anchor)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

        return jsonify({
            "status": "success",
            "message": "Pracovní smlouva byla úspěšně zašifrována a odeslána k podpisu.",
            "credential_id": credential_id,
            "email": email
        }), 201

    # GET: Výpis všech smluv
    anchors = VerifiableCredentialAnchor.query.all()
    contracts_payload = []
    for anchor in anchors:
        created_at_iso = anchor.timestamped_at.isoformat() if hasattr(anchor, 'timestamped_at') and anchor.timestamped_at else None
        contracts_payload.append({
            "credential_id": anchor.credential_id,
            "tenant_id": anchor.tenant_id,
            "subject_did": anchor.subject_did,
            "content_hash": anchor.content_hash,
            "encrypted_payload": anchor.encrypted_payload,
            "iv": anchor.iv,
            "wrapped_key": anchor.wrapped_key,
            "status": anchor.status,
            "tsa_status": anchor.tsa_status,
            "clearance_level": anchor.clearance_level,
            "timestamped_at": created_at_iso,
            "proof_signature": anchor.proof_signature
        })

    return jsonify({"status": "success", "data": contracts_payload}), 200


@hr_bp.route('/api/v1/hr/contracts/<credential_id>', methods=['GET'])
def get_contract_detail(credential_id):
    anchor = VerifiableCredentialAnchor.query.filter_by(credential_id=credential_id).first()
    if not anchor:
        return jsonify({"status": "error", "message": "Smlouva nenalezena"}), 404

    timestamped_at_iso = anchor.timestamped_at.isoformat() if anchor.timestamped_at else None

    return jsonify({
        "status": "success",
        "data": {
            "credential_id": anchor.credential_id,
            "tenant_id": anchor.tenant_id,
            "subject_did": anchor.subject_did,
            "issuer_did": anchor.issuer_did,
            "content_hash": anchor.content_hash,
            "encrypted_payload": anchor.encrypted_payload,
            "iv": anchor.iv,
            "wrapped_key": anchor.wrapped_key,
            "status": anchor.status,
            "tsa_status": anchor.tsa_status,
            "clearance_level": anchor.clearance_level,
            "proof_signature": anchor.proof_signature,
            "hr_tsa_token": anchor.hr_tsa_token,
            "eidas_tsr_base64": anchor.eidas_tsr_base64,
            "timestamped_at": timestamped_at_iso
        }
    }), 200


@hr_bp.route('/api/v1/hr/contracts/<credential_id>/approve', methods=['POST'])
def approve_contract(credential_id):
    anchor = VerifiableCredentialAnchor.query.filter_by(credential_id=credential_id).first()
    if not anchor:
        return jsonify({"status": "error", "message": "Smlouva nenalezena"}), 404

    anchor.status = 'PROCESSING'
    anchor.tsa_status = 'IN_PROGRESS'
    db.session.commit()

    try:
        from hr_tasks import issue_hr_contract_vc_async
        task = issue_hr_contract_vc_async.delay(credential_id)
        task_id = task.id
    except Exception as e:
        anchor.status = 'FAILED'
        anchor.tsa_error = f"Chyba při předání Celery: {str(e)}"
        db.session.commit()
        return jsonify({"status": "error", "message": "Nepodařilo se naplánovat emisi VC", "error": str(e)}), 500

    return jsonify({
        "status": "success",
        "message": "Smlouva byla schválena. Zahájena asynchronní emise a ukotvení Verifiable Credential.",
        "credential_id": credential_id,
        "task_id": task_id
    }), 200


@hr_bp.route('/api/v1/hr/revoke-identity', methods=['POST'])
def revoke_identity():
    data = request.get_json() or {}
    email_hash = data.get('email_hash')

    if not email_hash:
        return jsonify({"status": "error", "message": "Chybí povinný parametr 'email_hash'"}), 400

    identities = IdentityNode.query.filter_by(email_hash=email_hash).all()
    if not identities:
        return jsonify({"status": "error", "message": "Identita nenalezena"}), 404

    for identity in identities:
        identity.is_active = False

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({
        "status": "success",
        "message": "Identita byla úspěšně deaktivována (Crypto Shredding - čl. 17 GDPR)."
    }), 200
