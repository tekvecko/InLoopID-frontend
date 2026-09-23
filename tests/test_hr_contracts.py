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

def test_get_contracts_empty_or_list(client):
    res = client.get('/api/v1/hr/contracts')
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'success'
    assert isinstance(data['data'], list)

def test_create_hr_contract(client):
    payload = {
        "tenant_id": "tenant_test",
        "email": "jan.novak@example.com",
        "name": "Jan Novák",
        "position": "Developer",
        "content_hash": "a1b2c3d4e5f67890a1b2c3d4e5f67890a1b2c3d4e5f67890a1b2c3d4e5f67890",
        "encrypted_payload": "enc_data_blob",
        "iv": "iv_spec",
        "wrapped_key": "wrapped_key_spec",
        "clearance_level": "SECRET"
    }
    res = client.post('/api/v1/hr/contracts', json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data['status'] == 'success'
    assert 'credential_id' in data

def test_get_contract_detail_and_approve(client):
    payload = {
        "tenant_id": "tenant_test",
        "email": "petr.svoboda@example.com",
        "content_hash": "1122334455667788990011223344556677889900112233445566778899001122",
        "encrypted_payload": "enc_data_blob_2"
    }
    res_create = client.post('/api/v1/hr/contracts', json=payload)
    assert res_create.status_code == 201
    cred_id = res_create.get_json()['credential_id']

    res_detail = client.get(f'/api/v1/hr/contracts/{cred_id}')
    assert res_detail.status_code == 200
    detail_data = res_detail.get_json()['data']
    assert detail_data['credential_id'] == cred_id

    res_approve = client.post(f'/api/v1/hr/contracts/{cred_id}/approve')
    assert res_approve.status_code == 200
    assert res_approve.get_json()['status'] == 'success'

def test_get_nonexistent_contract(client):
    res = client.get('/api/v1/hr/contracts/non_existent_id_999')
    assert res.status_code == 404
    assert res.get_json()['status'] == 'error'
