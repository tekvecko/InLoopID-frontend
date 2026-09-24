from flask import Blueprint, request, jsonify
import uuid
from datetime import datetime, UTC
from models import db, VerifiableCredentialAnchor, BlindAuditLog
from zk_tasks import verify_rust_zk_proof_async

verifier_bp = Blueprint('verifier_bp', __name__)

# Paměťový nebo databázový store pro active challenges (pro produkci možno přenést do DB/Redis)
ACTIVE_CHALLENGES = {}

@verifier_bp.route('/api/v1/verifier/challenge', methods=['POST'])
def create_verification_challenge():
    """
    Třetí strana (např. banka) si vyžádá ověření atributu pomocí ZK predikátu.
    Vrátí challenge (nonce) a požadovaná kritéria.
    """
    data = request.get_json() or {}
    verifier_id = data.get('verifier_id', 'unknown_verifier')
    predicate_type = data.get('predicate_type', 'salary_threshold')
    threshold = data.get('threshold', 35000)

    challenge_nonce = str(uuid.uuid4())
    
    ACTIVE_CHALLENGES[challenge_nonce] = {
        "verifier_id": verifier_id,
        "predicate_type": predicate_type,
        "threshold": threshold,
        "created_at": datetime.now(UTC),
        "status": "pending"
    }

    return jsonify({
        "status": "success",
        "challenge_nonce": challenge_nonce,
        "verifier_id": verifier_id,
        "request": {
            "predicate_type": predicate_type,
            "threshold": threshold
        },
        "message": "Verification challenge successfully generated."
    }), 201


@verifier_bp.route('/api/v1/verifier/verify-presentation', methods=['POST'])
def verify_external_presentation():
    """
    Zaměstnancem předložený ZK proof a presentation response oproti challenge verifikátora.
    """
    data = request.get_json() or {}
    challenge_nonce = data.get('challenge_nonce')
    proof = data.get('proof')
    credential_id = data.get('credential_id')
    attribute_data = data.get('attribute_data')

    if not challenge_nonce or challenge_nonce not in ACTIVE_CHALLENGES:
        return jsonify({
            "status": "error",
            "message": "Neplatná nebo vypršená challenge (nonce)."
        }), 400

    challenge_info = ACTIVE_CHALLENGES[challenge_nonce]
    if challenge_info["status"] != "pending":
        return jsonify({
            "status": "error",
            "message": "Tato challenge již byla použita."
        }), 400

    if not proof or not credential_id:
        return jsonify({
            "status": "error",
            "message": "Chybí povinné parametry 'proof' nebo 'credential_id'."
        }), 400

    # Ověříme, zda VC anchor existuje v systému
    anchor = VerifiableCredentialAnchor.query.filter_by(credential_id=credential_id).first()
    if not anchor:
        return jsonify({
            "status": "error",
            "message": "Odkazovaný Verifiable Credential nebyl v systému nalezen."
        }), 404

    threshold = challenge_info["threshold"]

    # Spustíme asynchronní ověření přes Celery a Rust jádro
    task = verify_rust_zk_proof_async.delay(
        str(attribute_data or anchor.content_hash),
        int(threshold),
        str(proof)
    )

    # Označíme challenge jako zpracovávanou
    challenge_info["status"] = "processing"
    challenge_info["task_id"] = task.id

    # Zaznamenáme do blind audit logu (bez úniku osobních údajů)
    try:
        audit_log = BlindAuditLog(
            action=f"EXTERNAL_VERIFIER_REQUEST:{challenge_info['verifier_id']}",
            actor_did=credential_id,
            ip_address=request.remote_addr
        )
        db.session.add(audit_log)
        db.session.commit()
    except Exception:
        db.session.rollback()

    return jsonify({
        "status": "queued",
        "challenge_nonce": challenge_nonce,
        "task_id": task.id,
        "message": "External ZK verification dispatched to verification engine."
    }), 202


@verifier_bp.route('/api/v1/verifier/challenge/<challenge_nonce>', methods=['GET'])
def get_challenge_status(challenge_nonce):
    """
    Zjištění stavu ověření pro danou výzvu třetí strany.
    """
    if challenge_nonce not in ACTIVE_CHALLENGES:
        return jsonify({"status": "error", "message": "Challenge nenalezena."}), 404

    info = ACTIVE_CHALLENGES[challenge_nonce]
    return jsonify({
        "challenge_nonce": challenge_nonce,
        "verifier_id": info["verifier_id"],
        "status": info["status"],
        "task_id": info.get("task_id")
    }), 200
