import os
import hashlib
import tempfile
import subprocess
import requests
from flask import Blueprint, request, jsonify
from models import VerifiableCredentialAnchor, IdentityNode

api_bp = Blueprint('api_v1', __name__, url_prefix='/api/v1')

FREETSA_CACERT_URL = "https://www.freetsa.org/files/cacert.pem"

def verify_tsr(content_hash_hex: str, tsr_hex: str) -> tuple[bool, str]:
    """
    Ověří OpenSSL eIDAS časové razítko (TSR) vůči certifikátu FreeTSA CA.
    """
    cacert_path = os.path.join(tempfile.gettempdir(), "freetsa_cacert.pem")

    if not os.path.exists(cacert_path):
        res = requests.get(FREETSA_CACERT_URL, timeout=10)
        res.raise_for_status()
        with open(cacert_path, "wb") as f:
            f.write(res.content)

    tmp_tsr_path = None
    try:
        tsr_bytes = bytes.fromhex(tsr_hex)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".tsr") as tmp_tsr:
            tmp_tsr.write(tsr_bytes)
            tmp_tsr_path = tmp_tsr.name

        cmd = [
            "openssl", "ts", "-verify",
            "-in", tmp_tsr_path,
            "-digest", content_hash_hex,
            "-CAfile", cacert_path
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0 and "Verification: OK" in result.stdout:
            return True, "Verification: OK"
        else:
            return False, f"STDOUT: {result.stdout.strip()} | STDERR: {result.stderr.strip()}"

    except Exception as e:
        return False, str(e)
    finally:
        if tmp_tsr_path and os.path.exists(tmp_tsr_path):
            os.remove(tmp_tsr_path)


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
    issuer = IdentityNode.query.filter_by(did_uri=issuer_did, is_active=True).first()
    if not issuer:
        return jsonify({"error": "Neregistrovaný nebo neaktivní vydavatel"}), 403

    credential_id = data.get('credential_id')
    content_hash = data.get('content_hash')

    anchor = VerifiableCredentialAnchor(
        credential_id=credential_id,
        issuer_did=issuer_did,
        subject_did=data.get('subject_did'),
        content_hash=content_hash,
        proof_signature=data.get('proof_signature'),
        encrypted_payload=data.get('encrypted_payload'),
        iv=data.get('iv'),
        wrapped_key=data.get('wrapped_key')
    )

    db.session.add(anchor)
    db.session.commit()

    task_id = None
    try:
        from tasks import async_issue_tsa_timestamp
        if anchor.id:
            task = async_issue_tsa_timestamp.delay(anchor.id)
            task_id = task.id
    except Exception:
        pass

    return jsonify({
        "message": "Kotva byla úspěšně vytvořena.",
        "anchor_id": anchor.id,
        "content_hash": anchor.content_hash,
        "tsa_status": getattr(anchor, 'tsa_status', None),
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
