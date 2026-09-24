import sys
import os

# Přidáme aktuální adresář do cesty
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import VerifiableCredentialAnchor

with app.app_context():
    existing = VerifiableCredentialAnchor.query.filter_by(credential_id='test_vc_anchor_01').first()
    if not existing:
        anchor = VerifiableCredentialAnchor(
            credential_id='test_vc_anchor_01',
            content_hash='mock_content_hash_for_testing_salary_45000',
            tsa_status='verified'
        )
        db.session.add(anchor)
        db.session.commit()
        print("OK: Testovací VerifiableCredentialAnchor úspěšně vytvořen v databázi!")
    else:
        print("INFO: Testovací kotva již v databázi existuje.")
