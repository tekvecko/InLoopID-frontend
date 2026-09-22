import subprocess
import json
import os
from celery_app import celery

RUST_BINARY = os.path.abspath(os.path.join(os.path.dirname(__file__), "../inloopid-core/target/release/inloopid-core"))

@celery.task(name='zk.generate_proof_async')
def generate_rust_zk_proof_async(attribute_data: str, threshold: int = 18):
    if not os.path.exists(RUST_BINARY):
        return {"error": "Rust binární soubor nebyl zkompilován."}
    
    try:
        result = subprocess.run(
            [RUST_BINARY, "prove", attribute_data, str(threshold)],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        return {"error": "Chyba při provádění v Rust jádru", "details": e.stderr.strip()}
    except Exception as ex:
        return {"error": str(ex)}

@celery.task(name='zk.verify_proof_async')
def verify_rust_zk_proof_async(attribute_data: str, threshold: int, expected_commitment: str):
    if not os.path.exists(RUST_BINARY):
        return {"error": "Rust binární soubor nebyl zkompilován."}
    
    try:
        result = subprocess.run(
            [RUST_BINARY, "verify", attribute_data, str(threshold), expected_commitment],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout.strip())
    except Exception as ex:
        return {"error": str(ex)}

@celery.task(name='zk.issue_tsa_async')
def issue_eidas_tsa_token_async(commitment: str):
    if not os.path.exists(RUST_BINARY):
        return {"error": "Rust binární soubor nebyl zkompilován."}
    
    try:
        result = subprocess.run(
            [RUST_BINARY, "tsa", commitment],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout.strip())
    except Exception as ex:
        return {"error": str(ex)}
