import os
path = os.path.expanduser("~/InloopID/backend/routes.py")
with open(path, "r", encoding="utf-8") as f: content = f.read()

# Odstranění starých demo endpointů a vložení robustní verze
if "# ENTERPRISE DEMO ENDPOINTY" in content:
    content = content.split("# ENTERPRISE DEMO ENDPOINTY")[0]

new_endpoints = """
# ENTERPRISE DEMO ENDPOINTY
import os, smtplib, base64, re
from email.message import EmailMessage
from flask import request, jsonify, current_app
from itsdangerous import URLSafeTimedSerializer
import PyPDF2

@api_bp.route('/api/v1/demo/request-access', methods=['POST'])
def demo_request():
    email = request.json.get('email')
    if not email: return jsonify({"error": "Chybí email"}), 400
    serializer = URLSafeTimedSerializer(current_app.secret_key)
    token = serializer.dumps(email, salt='demo-activation')
    return jsonify({"status": "ok", "token": token})

@api_bp.route('/api/v1/demo/send-email', methods=['POST'])
def demo_send_email():
    try:
        data = request.json
        msg = EmailMessage()
        msg['Subject'] = 'InLoopID: Smlouva k podpisu'
        msg['From'] = os.environ.get('SMTP_USER', 'hr@inloopid.cz')
        msg['To'] = data['email']
        msg.set_content("V příloze naleznete kryptograficky zajištěný dokument.")
        if data.get('pdf_b64'):
            msg.add_attachment(base64.b64decode(data['pdf_b64']), maintype='application', subtype='pdf', filename='Smlouva.pdf')
        
        with smtplib.SMTP(os.environ.get('SMTP_HOST', 'localhost'), int(os.environ.get('SMTP_PORT', 1025))) as s:
            s.send_message(msg)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
"""
with open(path, "w", encoding="utf-8") as f: f.write(content + new_endpoints)
