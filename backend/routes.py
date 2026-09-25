import os
import hashlib
import tempfile
import subprocess
import requests
from flask import Blueprint, request, jsonify
from models import VerifiableCredentialAnchor, IdentityNode

api_bp = Blueprint('api_v1', __name__, url_prefix='/api/v1')

from tsa_service import verify_tsr


@api_bp.route('/anchor-credential', methods=['POST'])
def create_anchor():
    from app import db

    data = request.get_json() or {}

    required_fields = [
        'credential_id', 'issuer_did', 'subject_did',
        'content_hash', 'proof_signature', 'encrypted_payload',
        'iv', 'wrapped_key'
    ]

    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"Chybí povinný parametr '{field}'"}), 400

    issuer_did = data.get('issuer_did')
    issuer = IdentityNode.query.filter_by(
        did_uri=issuer_did,
        is_active=True,
    ).first()

    if not issuer:
        return jsonify({
            "error": "Neregistrovaný nebo neaktivní vydavatel"
        }), 403

    subject_did = data.get('subject_did')
    subject = IdentityNode.query.filter_by(
        did_uri=subject_did,
        is_active=True,
    ).first()

    if not subject:
        return jsonify({
            "error": "Neregistrovaný nebo neaktivní subjekt"
        }), 403

    credential_id = data.get('credential_id')
    content_hash = data.get('content_hash')

    anchor = VerifiableCredentialAnchor(
        credential_id=credential_id,
        issuer_did=issuer_did,
        subject_did=subject_did,
        content_hash=content_hash,
        proof_signature=data.get('proof_signature'),
        encrypted_payload=data.get('encrypted_payload'),
        iv=data.get('iv'),
        wrapped_key=data.get('wrapped_key')
    )

    db.session.add(anchor)
    db.session.commit()

    task_id = None
    tsa_task_queued = False

    try:
        from anchor_tasks import issue_anchor_tsa_timestamp

        if anchor.id:
            task = issue_anchor_tsa_timestamp.delay(
                anchor.id
            )

            task_id = task.id
            tsa_task_queued = True

    except Exception:
        # Kotva už byla vytvořena, proto ji nemažeme.
        # Selhání dispatchu ale nesmí zůstat skryté.
        anchor.tsa_status = "FAILED"
        anchor.tsa_error = "TSA task dispatch failed"
        db.session.commit()

        import logging
        logging.getLogger(__name__).exception(
            "Nepodařilo se zařadit TSA task pro anchor ID %s",
            anchor.id,
        )

    return jsonify({
        "message": "Kotva byla úspěšně vytvořena.",
        "anchor_id": anchor.id,
        "content_hash": anchor.content_hash,
        "tsa_status": getattr(anchor, 'tsa_status', None),
        "tsa_task_queued": tsa_task_queued,
        "task_id": task_id
    }), 201


@api_bp.route('/anchor-credential/<int:anchor_id>', methods=['GET'])
def get_anchor(anchor_id):
    anchor = VerifiableCredentialAnchor.query.get(anchor_id)
    if not anchor:
        return jsonify({"error": "Kotva nenalezena"}), 404

    return jsonify({
        "anchor_id": anchor.id,
        "credential_id": anchor.credential_id,
        "content_hash": anchor.content_hash,
        "tsa_status": anchor.tsa_status,
        "eidas_tsr_base64": anchor.eidas_tsr_base64,
        "timestamped_at": anchor.timestamped_at.isoformat() if anchor.timestamped_at else None,
        "tsa_error": anchor.tsa_error
    })


@api_bp.route('/anchor-credential/<int:anchor_id>/verify', methods=['GET'])
def verify_anchor_endpoint(anchor_id):
    anchor = VerifiableCredentialAnchor.query.get(anchor_id)
    if not anchor:
        return jsonify({"error": "Kotva nenalezena"}), 404

    if not anchor.eidas_tsr_base64:
        return jsonify({
            "is_valid": False,
            "error": "Tato kotva zatím nemá uložené žádné časové razítko."
        }), 400

    is_valid, log = verify_tsr(anchor.content_hash, anchor.eidas_tsr_base64)

    return jsonify({
        "anchor_id": anchor.id,
        "credential_id": anchor.credential_id,
        "is_valid": is_valid,
        "details": log
    }), 200
