import pytest
from app import app as flask_app
from models import db, IdentityNode, VerifiableCredentialAnchor

@pytest.fixture
def app():
    flask_app.config.update({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", "SQLALCHEMY_TRACK_MODIFICATIONS": False})
    with flask_app.app_context():
        db.create_all()
        issuer = IdentityNode(did_uri="did:key:z6MkIssuer123", email_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", public_key_jwk="{}", role="issuer", is_active=True)
        db.session.add(issuer)
        db.session.commit()
        yield flask_app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app): return app.test_client()

def test_w3c_interoperability_success(client):
    payload = {
        "credential_id": "urn:uuid:1234-5678", "issuer_did": "did:key:z6MkIssuer123", "subject_did": "did:key:z6MkSubject999",
        "content_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "proof_signature": "SIG_XYZ_123", "encrypted_payload": "BLOB", "iv": "IV", "wrapped_key": "KEY"
    }
    response = client.post('/api/v1/anchor-credential', json=payload)
    assert response.status_code == 201

def test_edge_case_missing_crypto_fields(client):
    payload = {"credential_id": "u1", "issuer_did": "d1"}
    response = client.post('/api/v1/anchor-credential', json=payload)
    assert response.status_code == 400

def test_edge_case_unregistered_issuer(client):
    payload = {
        "credential_id": "u2", "issuer_did": "did:key:FAKE", "subject_did": "sub",
        "content_hash": "hash", "proof_signature": "sig", "encrypted_payload": "blob", "iv": "iv", "wrapped_key": "key"
    }
    response = client.post('/api/v1/anchor-credential', json=payload)
    assert response.status_code == 403

def test_crypto_shredding_article_17(client, app):
    # Voláme endpoint dle vaší implementace v routes.py
    response = client.post('/api/v1/hr/revoke-identity', json={"email_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"})
    assert response.status_code == 200
    with app.app_context():
        identity = IdentityNode.query.filter_by(did_uri="did:key:z6MkIssuer123").first()
        assert identity.is_active == False
