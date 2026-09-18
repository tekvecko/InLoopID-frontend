import sys
sys.path.append("/data/data/com.termux/files/home/InloopID/backend")
from app import app, db
from models import VerifiableCredentialAnchor

with app.app_context():
    # Identifikace smluv bez řádného WebCrypto šifrování
    invalid_contracts = VerifiableCredentialAnchor.query.filter(
        (VerifiableCredentialAnchor.iv == 'IV_PENDING') |
        (VerifiableCredentialAnchor.wrapped_key == 'WRAPPED_KEY_PENDING') |
        (VerifiableCredentialAnchor.encrypted_payload == None)
    ).all()
    
    count = len(invalid_contracts)
    for contract in invalid_contracts:
        db.session.delete(contract)
        
    db.session.commit()
    print(f"[+] Databáze vyčištěna. Smazáno {count} starých/nekompatibilních záznamů.")
