import pytest
from app import create_app, db

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_b2b_registration_flow(client):
    payload = {
        "company_name": "InLoop Systems s.r.o.",
        "admin_email": "admin@inloopsystems.cz",
        "ico": "12345678",
        "tariff": "enterprise"
    }
    res = client.post('/api/v1/b2b/register', json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data['status'] == 'success'
    assert 'tenant_id' in data

    res_dup = client.post('/api/v1/b2b/register', json=payload)
    assert res_dup.status_code == 409
    assert "již existuje" in res_dup.get_json()['error']

    res_bad = client.post('/api/v1/b2b/register', json={"company_name": "Test"})
    assert res_bad.status_code == 400

def test_mojeid_challenge_and_callback(client):
    init_payload = {
        "document_hash": "doc_hash_abcdef123456",
        "tenant_id": "tenant_test"
    }
    res_init = client.post('/auth/mojeid/challenge', json=init_payload)
    assert res_init.status_code == 200
    init_data = res_init.get_json()
    assert 'auth_url' in init_data
    assert 'state' in init_data
    state_token = init_data['state']

    cb_payload = {
        "code": "mojeid_auth_code_xyz",
        "state": state_token
    }
    res_cb = client.post('/auth/mojeid/callback', json=cb_payload)
    assert res_cb.status_code == 200
    cb_data = res_cb.get_json()
    assert cb_data['success'] is True
    assert cb_data['document_hash'] == "doc_hash_abcdef123456"

def test_identity_recovery_flow(client):
    rec_init_payload = {
        "email_hash": "hash_of_user_email",
        "tenant_id": "tenant_test"
    }
    res_init = client.post('/auth/recovery/init', json=rec_init_payload)
    assert res_init.status_code == 200
    state_token = res_init.get_json()['state']

    rec_complete_payload = {
        "code": "mojeid_recovery_code",
        "state": state_token,
        "new_did_uri": "did:inloopid:recovered_user_01",
        "public_key_jwk": {"kty": "RSA", "n": "new_pub_key_val"}
    }
    res_complete = client.post('/auth/recovery/complete', json=rec_complete_payload)
    assert res_complete.status_code == 200
    comp_data = res_complete.get_json()
    assert comp_data['success'] is True
    assert 'employee_token' in comp_data
    assert comp_data['did_uri'] == "did:inloopid:recovered_user_01"
