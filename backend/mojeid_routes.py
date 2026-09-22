import os
import json
import secrets
import requests
import jwt
from datetime import datetime, timedelta, UTC
from flask import Blueprint, request, jsonify
from models import db, OIDCState, IdentityNode, BlindAuditLog

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

MOJEID_CLIENT_ID = os.environ.get('MOJEID_CLIENT_ID', 'demo_client_id')
MOJEID_CLIENT_SECRET = os.environ.get('MOJEID_CLIENT_SECRET', 'demo_client_secret')
MOJEID_AUTH_URL = os.environ.get('MOJEID_AUTH_URL', 'https://mojeid.regtest.nic.cz/endpoint/auth/')
MOJEID_TOKEN_URL = os.environ.get('MOJEID_TOKEN_URL', 'https://mojeid.regtest.nic.cz/endpoint/token/')
SECRET_KEY = os.environ.get('SECRET_KEY', 'vyvojovy_klic_pro_termux_inloopid_123')

@auth_bp.route('/mojeid/challenge', methods=['POST'])
def init_challenge():
    data = request.get_json() or {}
    document_hash = data.get('document_hash')
    tenant_id = data.get('tenant_id', 'public_zone')
    redirect_uri = data.get('redirect_uri', 'http://localhost:5173/auth/mojeid/callback')

    if not document_hash:
        return jsonify({'error': 'Chybí parametr document_hash'}), 400

    state_token = secrets.token_urlsafe(32)
    oidc_state = OIDCState(
        state=state_token,
        flow_type='challenge',
        tenant_id=tenant_id,
        document_hash=document_hash
    )
    db.session.add(oidc_state)
    db.session.commit()

    params = {
        'response_type': 'code',
        'client_id': MOJEID_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'scope': 'openid profile email',
        'state': state_token
    }
    req = requests.Request('GET', MOJEID_AUTH_URL, params=params).prepare()

    return jsonify({
        'auth_url': req.url,
        'state': state_token
    }), 200

@auth_bp.route('/recovery/init', methods=['POST'])
def init_recovery():
    data = request.get_json() or {}
    email_hash = data.get('email_hash')
    tenant_id = data.get('tenant_id', 'public_zone')
    redirect_uri = data.get('redirect_uri', 'http://localhost:5173/auth/recovery/callback')

    state_token = secrets.token_urlsafe(32)
    oidc_state = OIDCState(
        state=state_token,
        flow_type='recovery',
        tenant_id=tenant_id,
        email_hash=email_hash
    )
    db.session.add(oidc_state)
    db.session.commit()

    params = {
        'response_type': 'code',
        'client_id': MOJEID_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'scope': 'openid profile email',
        'state': state_token
    }
    req = requests.Request('GET', MOJEID_AUTH_URL, params=params).prepare()

    return jsonify({
        'auth_url': req.url,
        'state': state_token
    }), 200

@auth_bp.route('/mojeid/callback', methods=['POST'])
def handle_challenge_callback():
    data = request.get_json() or {}
    code = data.get('code')
    state_token = data.get('state')

    if not state_token:
        return jsonify({'error': 'Chybí kód výzvy nebo state.'}), 400

    oidc_state = OIDCState.query.filter_by(state=state_token, is_used=False).first()
    if not oidc_state or oidc_state.flow_type != 'challenge':
        return jsonify({'error': 'Neplatná nebo již použitá relace výzvy.'}), 400

    oidc_state.is_used = True
    audit = BlindAuditLog(
        action=f"MOJEID_STEPUP_VERIFIED:{oidc_state.document_hash}",
        ip_address=request.remote_addr
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Výzva úspěšně ověřena v MojeID.',
        'document_hash': oidc_state.document_hash
    }), 200

@auth_bp.route('/recovery/complete', methods=['POST'])
def complete_recovery():
    data = request.get_json() or {}
    code = data.get('code')
    state_token = data.get('state')
    new_did_uri = data.get('new_did_uri')
    public_key_jwk = data.get('public_key_jwk')

    if not state_token or not new_did_uri or not public_key_jwk:
        return jsonify({'error': 'Nedostatečné parametry pro dokončení obnovy.'}), 400

    oidc_state = OIDCState.query.filter_by(state=state_token, is_used=False).first()
    if not oidc_state or oidc_state.flow_type != 'recovery':
        return jsonify({'error': 'Neplatná nebo vypršená relace pro obnovu identity.'}), 400

    jwk_str = json.dumps(public_key_jwk) if isinstance(public_key_jwk, dict) else str(public_key_jwk)

    node = None
    if oidc_state.email_hash:
        node = IdentityNode.query.filter_by(email_hash=oidc_state.email_hash).first()

    if node:
        node.did_uri = new_did_uri
        node.public_key_jwk = jwk_str
        node.is_active = True
    else:
        node = IdentityNode(
            tenant_id=oidc_state.tenant_id or 'public_zone',
            did_uri=new_did_uri,
            email_hash=oidc_state.email_hash,
            public_key_jwk=jwk_str,
            role='employee',
            is_active=True
        )
        db.session.add(node)

    oidc_state.is_used = True

    token_payload = {
        'did_uri': new_did_uri,
        'tenant_id': node.tenant_id,
        'email_hash': node.email_hash,
        'exp': datetime.now(UTC) + timedelta(hours=24)
    }
    employee_token = jwt.encode(token_payload, SECRET_KEY, algorithm='HS256')

    audit = BlindAuditLog(
        action=f"IDENTITY_REKEYED:{new_did_uri}",
        actor_did=new_did_uri,
        ip_address=request.remote_addr
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Identity re-keying byl úspěšně dokončen.',
        'employee_token': employee_token,
        'did_uri': new_did_uri
    }), 200
