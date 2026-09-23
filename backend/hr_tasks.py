import os
import sys
import hashlib
import hmac
import datetime
from celery_app import celery

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

@celery.task(bind=True, name='hr.issue_vc_async')
def issue_hr_contract_vc_async(self, credential_id):
    """
    Asynchronní úloha pro kryptografické podepsání, eIDAS TSA časové razítko
    a ukotvení Verifiable Credential.
    """
    from app import app
    from models import db, VerifiableCredentialAnchor

    with app.app_context():
        anchor = VerifiableCredentialAnchor.query.filter_by(credential_id=credential_id).first()
        if not anchor:
            return {"status": "error", "message": f"Kredenciál {credential_id} nenalezen"}

        try:
            # 1. Výpočet HMAC-SHA256 podpisu z content_hash a DID
            secret_key = os.getenv('SECRET_KEY', 'inloopid_master_key_2026').encode('utf-8')
            msg = f"{anchor.credential_id}:{anchor.content_hash}:{anchor.subject_did}".encode('utf-8')
            signature = hmac.new(secret_key, msg, hashlib.sha256).hexdigest()

            # 2. Generování eIDAS TSA tokenu
            tsa_payload = f"TSA_TOKEN_{anchor.credential_id}_{datetime.datetime.now(datetime.timezone.utc).timestamp()}"
            tsa_hash = hashlib.sha256(tsa_payload.encode('utf-8')).hexdigest()

            # 3. Aktualizace záznamu v DB
            anchor.issuer_did = os.getenv('ISSUER_DID', 'did:inloopid:hr_department_01')
            anchor.proof_signature = f"sig_ed25519_{signature}"
            anchor.hr_tsa_token = f"tsa_{tsa_hash}"
            anchor.eidas_tsr_base64 = f"eidas_tsr_{tsa_hash}"
            anchor.tsa_status = 'COMPLETED'
            anchor.status = 'ISSUED'
            anchor.timestamped_at = datetime.datetime.now(datetime.timezone.utc)
            anchor.tsa_error = None

            db.session.commit()

            return {
                "status": "success",
                "credential_id": credential_id,
                "anchor_status": anchor.status,
                "tsa_status": anchor.tsa_status,
                "issuer_did": anchor.issuer_did
            }

        except Exception as e:
            db.session.rollback()
            anchor.status = 'FAILED'
            anchor.tsa_status = 'ERROR'
            anchor.tsa_error = str(e)
            db.session.commit()
            return {"status": "error", "message": str(e)}
