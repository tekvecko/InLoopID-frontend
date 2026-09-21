import os
import tempfile
import subprocess
import requests
import logging
from datetime import datetime
from celery_app import celery

logger = logging.getLogger(__name__)

@celery.task(bind=True, max_retries=3, default_retry_delay=10)
def async_issue_tsa_timestamp(self, anchor_id: int):
    """
    Asynchronní získání kvalifikovaného eIDAS časového razítka (TSA)
    a jeho ukotvení k Verifiable Credential záznamu.
    """
    from app import db, create_app
    from models import VerifiableCredentialAnchor

    app = create_app()
    with app.app_context():
        anchor = VerifiableCredentialAnchor.query.get(anchor_id)
        if not anchor:
            logger.error(f"[TSA Task] VerifiableCredentialAnchor ID {anchor_id} nenalezen v databázi.")
            return False

        tmp_hash_path = None
        query_tsq_path = None

        try:
            content_hash = anchor.content_hash

            # 1. Příprava dočasného souboru s hex hashem pro OpenSSL TSQ
            with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.hash') as tmp:
                tmp.write(content_hash)
                tmp_hash_path = tmp.name

            query_tsq_path = f"{tmp_hash_path}.tsq"

            # 2. Generování TSQ (Timestamp Request) požadavku přes OpenSSL
            cmd = [
                "openssl", "ts", "-query",
                "-digest", content_hash,
                "-sha256",
                "-cert",
                "-out", query_tsq_path
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # 3. Odeslání TSQ požadavku na TSA server
            tsa_url = os.getenv("TSA_SERVER_URL", "https://freetsa.org/tsr")
            with open(query_tsq_path, "rb") as f:
                tsq_data = f.read()

            response = requests.post(
                tsa_url,
                data=tsq_data,
                headers={"Content-Type": "application/timestamp-query"},
                timeout=15
            )
            response.raise_for_status()

            # 4. Uložení získaného TSR (Timestamp Response) v Hex
            tsr_hex = response.content.hex()

            anchor.eidas_tsr_base64 = tsr_hex
            anchor.tsa_status = "COMPLETED"
            anchor.timestamped_at = datetime.utcnow()
            db.session.commit()

            logger.info(f"[TSA Task] Časové razítko pro anchor ID {anchor_id} bylo úspěšně získáno a uloženo.")
            return True

        except Exception as exc:
            db.session.rollback()
            logger.warning(f"[TSA Task] Chyba při komunikaci s TSA pro anchor ID {anchor_id}: {exc}")

            if self.request.retries >= self.max_retries:
                anchor.tsa_status = "FAILED"
                anchor.tsa_error = str(exc)
                db.session.commit()
                logger.error(f"[TSA Task] Získání TSA razítka pro anchor ID {anchor_id} selhalo po {self.max_retries} pokusech.")
            else:
                raise self.retry(exc=exc)

        finally:
            if tmp_hash_path and os.path.exists(tmp_hash_path):
                os.remove(tmp_hash_path)
            if query_tsq_path and os.path.exists(query_tsq_path):
                os.remove(query_tsq_path)
