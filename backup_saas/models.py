from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, UTC

db = SQLAlchemy()

class CompanyWorkspace(db.Model):
    __tablename__ = 'company_workspaces'
    tenant_id = db.Column(db.String(100), primary_key=True)
    company_name = db.Column(db.String(255), nullable=False)
    ico = db.Column(db.String(20), nullable=True)
    admin_email = db.Column(db.String(255), nullable=False)
    public_key_jwk = db.Column(db.Text, nullable=False) 
    encrypted_private_key = db.Column(db.Text, nullable=False) 
    private_key_iv = db.Column(db.String(50), nullable=False) 
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

class IdentityNode(db.Model):
    __tablename__ = 'identity_nodes'
    id = db.Column(db.Integer, primary_key=True)
    did_uri = db.Column(db.String(255), unique=True, nullable=False, index=True)
    email_hash = db.Column(db.String(64), unique=True, nullable=True, index=True) 
    public_key_jwk = db.Column(db.Text, nullable=False) 
    encrypted_keystore = db.Column(db.Text, nullable=True) 
    keystore_iv = db.Column(db.String(50), nullable=True)
    role = db.Column(db.String(50), nullable=False)      
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

class VerifiableCredentialAnchor(db.Model):
    __tablename__ = 'verifiable_credential_anchors'
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(100), db.ForeignKey('company_workspaces.tenant_id'), nullable=False, index=True)
    credential_id = db.Column(db.String(255), unique=True, nullable=False)
    issuer_did = db.Column(db.String(255), db.ForeignKey('identity_nodes.did_uri'), nullable=False)
    subject_did = db.Column(db.String(255), db.ForeignKey('identity_nodes.did_uri'), nullable=False)
    content_hash = db.Column(db.String(64), nullable=False, index=True)     
    proof_signature = db.Column(db.Text, nullable=False)
    hr_tsa_token = db.Column(db.Text, nullable=True)
    encrypted_payload = db.Column(db.Text, nullable=False)                  
    iv = db.Column(db.String(50), nullable=False)                            
    wrapped_key = db.Column(db.Text, nullable=False)                        
    subject_signature = db.Column(db.Text, nullable=True)
    employee_tsa_token = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='anchored') 
    withdrawn_at = db.Column(db.DateTime, nullable=True) 
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

class BlindAuditLog(db.Model):
    __tablename__ = 'blind_audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(255), nullable=False)                       
    actor_did = db.Column(db.String(255), nullable=True)                     
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

class HRAgendaItem(db.Model):
    __tablename__ = 'hr_agenda'
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(100), db.ForeignKey('company_workspaces.tenant_id'), nullable=False)
    email_hash = db.Column(db.String(64), index=True, nullable=False)
    encrypted_data = db.Column(db.Text, nullable=False)
    iv = db.Column(db.String(50), nullable=False)
    wrapped_key = db.Column(db.Text, nullable=True) 
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

class OnboardingTask(db.Model):
    __tablename__ = 'onboarding_tasks'
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(100), db.ForeignKey('company_workspaces.tenant_id'), nullable=False)
    email_hash = db.Column(db.String(64), index=True, nullable=False)
    task_type = db.Column(db.String(50), nullable=False) 
    status = db.Column(db.String(50), default='pending') 
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
