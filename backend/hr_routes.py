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
