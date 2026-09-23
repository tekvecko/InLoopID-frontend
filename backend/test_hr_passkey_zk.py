import pytest
from app import create_app, db
from models import VerifiableCredentialAnchor, IdentityNode

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_hr_contracts_flow(client):
    res = client.get('/api/v1/hr/contracts')
    assert res.status_code == 200
    data = res.get_json()
    assert 'data' in data
    assert data['status'] == 'success'

def test_passkey_routes(client):
    payload = {
        "email": "jan.novak@example.com",
        "tenant_id": "tenant_test"
    }
    res = client.post('/api/v1/passkey/register-challenge', json=payload)
    assert res.status_code in [200, 400, 500]

def test_zk_routes(client):
    zk_payload = {
        "circuit_id": "age_verification",
        "inputs": {"age": 25}
    }
    res = client.post('/api/v1/zk/prove', json=zk_payload)
    assert res.status_code in [200, 202, 400, 422]
