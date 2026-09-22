import subprocess
import json
import os

RUST_BINARY = os.path.abspath(os.path.join(os.path.dirname(__file__), "../inloopid-core/target/release/inloopid-core"))

def generate_rust_zk_proof(attribute_data: str, threshold: int = 18):
    if not os.path.exists(RUST_BINARY):
        return {"error": "Rust binární soubor nebyl zkompilován."}, 500
    
    try:
        result = subprocess.run(
            [RUST_BINARY, "prove", attribute_data, str(threshold)],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout.strip()), 200
    except subprocess.CalledProcessError as e:
        return {"error": "Chyba při provádění v Rust jádru", "details": e.stderr.strip()}, 400
    except Exception as ex:
        return {"error": str(ex)}, 500
