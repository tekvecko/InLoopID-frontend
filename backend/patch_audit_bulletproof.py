import re
import textwrap

file_path = "/data/data/com.termux/files/home/InloopID/backend/routes.py"

with open(file_path, 'r') as f:
    content = f.read()

# 1. Záloha pro strýčka Příhodu
with open(file_path + ".bak_bulletproof", 'w') as f:
    f.write(content)

# 2. Úplné odstranění staré funkce generující PDF
content = re.sub(r"@api_bp\.route\('/hr/compliance-report/pdf'.*?(?=@api_bp\.route|\Z)", "", content, flags=re.DOTALL)

# 3. Nová, strukturálně neprůstřelná verze
new_code = """
@api_bp.route('/hr/compliance-report/pdf', methods=['GET'])
def compliance_report_pdf():
    from flask import request, send_file, current_app
    from models import VerifiableCredentialAnchor, CompanyWorkspace
    from fpdf import FPDF, XPos, YPos, XPos, YPos
    import tempfile, os, textwrap
    from datetime import datetime, UTC

    tenant_id = request.args.get('tenant_id')
    if not tenant_id:
        return "Chybí tenant_id", 400

    comp = CompanyWorkspace.query.filter_by(tenant_id=tenant_id).first()
    company_name = comp.company_name if comp else tenant_id
    credentials = VerifiableCredentialAnchor.query.filter_by(tenant_id=tenant_id).order_by(VerifiableCredentialAnchor.created_at.desc()).all()
    
    safe = 0; risk = 0; pending = 0
    now = datetime.now(UTC)

    for cred in credentials:
        if cred.status in ['anchored', 'pending_signature']:
            pending += 1
        elif cred.status == 'signed':
            delta = now - cred.created_at.replace(tzinfo=UTC)
            if delta.days <= 7: risk += 1
            else: safe += 1

    pdf = FPDF()
    font_dir = os.path.join(current_app.root_path, 'static', 'fonts')
    os.makedirs(font_dir, exist_ok=True)
    
    pdf.add_font('Roboto', '', os.path.join(font_dir, 'Roboto-Regular.ttf'))
    pdf.add_font('Roboto', 'B', os.path.join(font_dir, 'Roboto-Bold.ttf'))
    
    pdf.add_page()
    pdf.set_font("Roboto", "B", 16)
    pdf.cell(0, 10, "INLOOPID - KRYPTOGRAFICKÝ AUDIT (SLEPÝ NOTÁŘ)", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(10)
    
    pdf.set_font("Roboto", "B", 12)
    pdf.cell(0, 8, f"Subjekt: {company_name}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Roboto", "", 10)
    pdf.cell(0, 6, f"ID (Tenant): {tenant_id}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Vygenerováno: {now.strftime('%d.%m.%Y %H:%M:%S')} UTC", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)

    pdf.set_font("Roboto", "B", 12)
    pdf.cell(0, 8, "SOUHRN PRÁVNÍHO RADARU:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Roboto", "", 10)
    pdf.cell(0, 6, f"Dokumenty čekající na podpis: {pending}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Dokumenty v ochranné lhůtě (do 7 dnů): {risk}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Nedotknutelné / Uzavřené dokumenty: {safe}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)

    pdf.set_font("Roboto", "B", 12)
    pdf.cell(0, 8, "KRYPTOGRAFICKÝ ZÁZNAM (Nulová Znalost):", new_x="LMARGIN", new_y="NEXT")
    
    for cred in credentials:
        did_val = cred.subject_did if cred.subject_did else "DID_PENDING"
        hash_val = cred.content_hash if cred.content_hash else "HASH_PENDING"
        
        pdf.set_font("Roboto", "B", 8)
        pdf.cell(0, 5, f"ID: {cred.credential_id} | STATUS: {cred.status.upper()}", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font("Roboto", "", 8)
        
        # Manuální iterace - nejstabilnější metoda tisku dlouhých řetězců
        pdf.cell(0, 4, "DID:", new_x="LMARGIN", new_y="NEXT")
        for line in textwrap.wrap(did_val, width=80, break_long_words=True):
            pdf.cell(0, 4, f"  {line}", new_x="LMARGIN", new_y="NEXT")
            
        pdf.cell(0, 4, "HASH:", new_x="LMARGIN", new_y="NEXT")
        for line in textwrap.wrap(hash_val, width=80, break_long_words=True):
            pdf.cell(0, 4, f"  {line}", new_x="LMARGIN", new_y="NEXT")
            
        pdf.ln(3)

    fd, temp_path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    pdf.output(temp_path)

    return send_file(temp_path, as_attachment=True, download_name=f"InLoopID_Audit_{tenant_id}.pdf")
"""

with open(file_path, 'w') as f:
    f.write(content.strip() + "\n\n" + textwrap.dedent(new_code).strip() + "\n")

print("[+] Generátor byl úspěšně přepsán na neprůstřelnou metodu 'cell'.")
