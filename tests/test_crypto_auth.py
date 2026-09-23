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

def test_zk_prove_and_verify(client):
    # Test ZK proof dispatch
    prove_payload = {
        "circuit_id": "age_verification",
        "threshold": 18,
        "inputs": {"age": 25}
    }
    res_prove = client.post('/api/v1/zk/prove', json=prove_payload)
    assert res_prove.status_code == 202
    data_prove = res_prove.get_json()
    assert "task_id" in data_prove

    # Test ZK verification dispatch
    verify_payload = {
        "circuit_id": "age_verification",
        "threshold": 18,
        "commitment": "mock_commitment_hash_abc123"
    }
    res_verify = client.post('/api/v1/zk/verify', json=verify_payload)
    assert res_verify.status_code == 202
    data_verify = res_verify.get_json()
    assert "task_id" in data_verify

def test_passkey_full_flow(client):
    email = "test.user@inloopid.cz"

    # 1. Vyžádání challenge pro registrování passkey
    res_chal = client.post('/api/v1/passkey/register-challenge', json={"email": email})
    assert res_chal.status_code == 200
    chal_data = res_chal.get_json()
    assert chal_data['status'] == 'ok'
    assert 'options' in chal_data
    assert chal_data['options']['user']['name'] == email

    # 2. Ověření a uložení passkey credentialu
    verify_payload = {
        "email": email,
        "credential": {
            "id": "mock_cred_id_789",
            "rawId": "raw_id_bytes_base64",
            "type": "public-key"
        }
    }
    res_ver = client.post('/api/v1/passkey/register-verify', json=verify_payload)
    assert res_ver.status_code == 200
    ver_data = res_ver.get_json()
    assert ver_data['status'] == 'success'
    assert ver_data['verified'] is True

    # 3. Kontrola stavu passkey pro uživatele
    res_status = client.get(f'/api/v1/passkey/status/{email}')
    assert res_status.status_code == 200
    status_data = res_status.get_json()
    assert status_data['email'] == email
    assert status_data['has_passkey'] is True
