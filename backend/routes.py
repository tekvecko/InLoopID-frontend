import os
import hashlib
import tempfile
import subprocess
import requests
from flask import Blueprint, request, jsonify
from models import VerifiableCredentialAnchor

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
    from tasks import async_issue_tsa_timestamp

    data = request.get_json() or {}
    credential_id = data.get('credential_id')

    if not credential_id:
        return jsonify({"error": "Chybí 'credential_id'"}), 400

    content_hash = hashlib.sha256(credential_id.encode('utf-8')).hexdigest()

    anchor = VerifiableCredentialAnchor(
        credential_id=credential_id,
        content_hash=content_hash
    )

    db.session.add(anchor)
    db.session.commit()

    task_id = None
    if anchor.id:
        task = async_issue_tsa_timestamp.delay(anchor.id)
        task_id = task.id

    return jsonify({
        "message": "Kotva byla úspěšně vytvořena. TSA razítkování probíhá asynchronně.",
        "anchor_id": anchor.id,
        "content_hash": anchor.content_hash,
        "tsa_status": anchor.tsa_status,
        "task_id": task_id
    }), 202


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
