from flask import Blueprint, request, jsonify, send_file
from datetime import datetime, UTC, timedelta
import hashlib
import tempfile
from models import db, EmploymentContract, AttendanceRecord
from hr_pdf_generator import generate_employment_contract_pdf

hr_compliance_bp = Blueprint('hr_compliance_bp', __name__, url_prefix='/api/hr/compliance')

@hr_compliance_bp.route('/contract/create', methods=['POST'])
def create_employment_contract():
    data = request.json or {}
    tenant_id = data.get('tenant_id')
    email_hash = data.get('employee_email_hash')
    payload = data.get('encrypted_payload')
    iv = data.get('iv')
    contract_type = data.get('contract_type', 'pracovni_smlouva')

    if not tenant_id or not email_hash or not payload:
        return jsonify({'error': 'Chybí povinná data pro vytvoření smlouvy.'}), 400

    doc_raw = (tenant_id + email_hash + payload + str(datetime.now(UTC))).encode('utf-8')
    doc_hash = hashlib.sha256(doc_raw).hexdigest()
    retention_date = datetime.now(UTC) + timedelta(days=365 * 30)

    contract = EmploymentContract(
        tenant_id=tenant_id,
        employee_email_hash=email_hash,
        contract_type=contract_type,
        encrypted_payload=payload,
        iv=iv,
        document_hash=doc_hash,
        retention_expires_at=retention_date,
        delivery_status='pending_delivery'
    )
    db.session.add(contract)
    db.session.commit()

    return jsonify({
        'status': 'success',
        'message': 'Pracovní smlouva byla uložena s dodržením archivačních pravidel ČR.',
        'document_hash': doc_hash,
        'retention_expires_at': retention_date.isoformat()
    }), 201

@hr_compliance_bp.route('/contracts', methods=['GET'])
def get_employee_contracts():
    tenant_id = request.args.get('tenant_id')
    email_hash = request.args.get('email_hash')

    query = EmploymentContract.query
    if tenant_id:
        query = query.filter_by(tenant_id=tenant_id)
    if email_hash:
        query = query.filter_by(employee_email_hash=email_hash)

    contracts = query.all()
    result = []
    for c in contracts:
        result.append({
            'document_hash': c.document_hash,
            'contract_type': c.contract_type,
            'employer_signed': c.employer_signed,
            'employee_signed': c.employee_signed,
            'delivery_status': c.delivery_status,
            'retention_expires_at': c.retention_expires_at.isoformat(),
            'created_at': c.created_at.isoformat()
        })
    return jsonify({'status': 'success', 'contracts': result})

@hr_compliance_bp.route('/contract/sign', methods=['POST'])
def sign_employment_contract():
    data = request.json or {}
    doc_hash = data.get('document_hash')
    signer_role = data.get('role')
    signature_proof = data.get('signature_proof')

    contract = EmploymentContract.query.filter_by(document_hash=doc_hash).first()
    if not contract:
        return jsonify({'error': 'Smlouva nenalezena.'}), 404

    if signer_role == 'employer':
        contract.employer_signed = True
        contract.employer_signature_proof = signature_proof
    elif signer_role == 'employee':
        contract.employee_signed = True
        contract.employee_signature_proof = signature_proof
        contract.delivery_status = 'signed_and_delivered'
        contract.delivered_at = datetime.now(UTC)
    else:
        return jsonify({'error': 'Neznámá role podepisujícího.'}), 400

    db.session.commit()
    return jsonify({
        'status': 'success',
        'message': f'Dokument podepsán rolí: {signer_role}',
        'delivery_status': contract.delivery_status
    })

@hr_compliance_bp.route('/contract/pdf/<doc_hash>', methods=['GET'])
def download_contract_pdf(doc_hash):
    contract = EmploymentContract.query.filter_by(document_hash=doc_hash).first()
    if not contract:
        return jsonify({'error': 'Smlouva nenalezena.'}), 404

    contract_data = {
        'employer_name': 'InLoopID s.r.o.',
        'employer_ico': '28391029',
        'employer_address': 'Brno, Česká republika',
        'employee_email_hash': contract.employee_email_hash,
        'contract_type': contract.contract_type,
        'start_date': contract.created_at.strftime('%d.%m.%Y'),
        'employer_signed': contract.employer_signed,
        'employee_signed': contract.employee_signed,
        'employer_signature_proof': contract.employer_signature_proof or 'N/A',
        'employee_signature_proof': contract.employee_signature_proof or 'N/A'
    }

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    tmp.close()
    
    generate_employment_contract_pdf(contract_data, tmp.name)
    
    return send_file(
        tmp.name,
        as_attachment=True,
        download_name=f"pracovni_smlouva_{doc_hash[:8]}.pdf",
        mimetype='application/pdf'
    )

@hr_compliance_bp.route('/attendance/log', methods=['POST'])
def log_attendance():
    data = request.json or {}
    tenant_id = data.get('tenant_id')
    email_hash = data.get('employee_email_hash')
    date_str = data.get('date')
    hours = data.get('hours_worked', 8.0)
    overtime = data.get('overtime_hours', 0.0)
    status = data.get('status', 'present')

    if not tenant_id or not email_hash or not date_str:
        return jsonify({'error': 'Chybí parametry pro evidenci docházky.'}), 400

    work_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    record = AttendanceRecord.query.filter_by(
        tenant_id=tenant_id,
        employee_email_hash=email_hash,
        date=work_date
    ).first()

    if record:
        record.hours_worked = hours
        record.overtime_hours = overtime
        record.status = status
    else:
        record = AttendanceRecord(
            tenant_id=tenant_id,
            employee_email_hash=email_hash,
            date=work_date,
            hours_worked=hours,
            overtime_hours=overtime,
            status=status
        )
        db.session.add(record)

    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Docházka byla zaevidována dle § 96.'})
