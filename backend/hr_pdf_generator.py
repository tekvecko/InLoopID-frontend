import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_employment_contract_pdf(contract_data, output_path):
    """
    Vygeneruje oficiální PDF pracovní smlouvy v souladu se Zákoníkem práce ČR.
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=40, leftMargin=40,
        topMargin=40, bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        alignment=1,
        textColor=colors.HexColor('#0f172a')
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        alignment=1,
        textColor=colors.HexColor('#64748b')
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=15,
        textColor=colors.HexColor('#1e293b')
    )
    
    bold_body = ParagraphStyle(
        'BoldBodyCustom',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    story = []

    story.append(Paragraph("PRACOVNÍ SMLOUVA", title_style))
    story.append(Paragraph("uzavřená dle § 34 zákona č. 262/2006 Sb., zákoník práce, v platném znění", subtitle_style))
    story.append(Spacer(1, 20))

    story.append(Paragraph("<b>I. Smluvní strany</b>", bold_body))
    story.append(Spacer(1, 5))
    
    employer_name = contract_data.get('employer_name', 'InLoopID s.r.o.')
    employer_id = contract_data.get('employer_ico', '12345678')
    employer_address = contract_data.get('employer_address', 'Brno, Česká republika')
    
    text_parties = f"""
    <b>Zaměstnavatel:</b> {employer_name}, IČO: {employer_id}<br/>
    Sídlem: {employer_address}<br/>
    (dále jen „zaměstnavatel na straně jedné“)<br/><br/>
    a<br/><br/>
    <b>Zaměstnanec:</b> Hash identifikátor: {contract_data.get('employee_email_hash', 'Neznámý')[:32]}...<br/>
    (dále jen „zaměstnanec na straně druhé“)<br/>
    uzavírají tuto pracovní smlouvu:
    """
    story.append(Paragraph(text_parties, body_style))
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>II. Druh práce a místo výkonu</b>", bold_body))
    story.append(Paragraph(f"1. Druh práce: <b>{contract_data.get('contract_type', 'Pracovník vývoje')}</b>", body_style))
    story.append(Paragraph("2. Místo výkonu práce: Česká republika / Remote / Termux Node", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>III. Den nástupu do práce a mzdové podmínky</b>", bold_body))
    story.append(Paragraph("1. Den nástupu do práce: " + contract_data.get('start_date', 'Ihned'), body_style))
    story.append(Paragraph("2. Mzdové podmínky se řídí mzdovým výměrem, který je nedílnou součástí této smlouvy.", body_style))
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>IV. Závěrečná ustanovení</b>", bold_body))
    story.append(Paragraph("Tato smlouva je vyhotovena v elektronické podobě a opatřena pokročilými elektronickými/biometrickými podpisy obou stran s garancí neměnnosti (SHA-256 hash otisk). Archivace probíhá po dobu 30 let dle archivačních pravidel ČR.", body_style))
    story.append(Spacer(1, 30))

    sig_data = [
        [
            Paragraph("<b>Za zaměstnavatele:</b><br/><br/>Stav: " + ("Podepsáno ✓" if contract_data.get('employer_signed') else "Čeká na podpis"), body_style),
            Paragraph("<b>Za zaměstnance:</b><br/><br/>Stav: " + ("Podepsáno ✓" if contract_data.get('employee_signed') else "Čeká na podpis"), body_style)
        ],
        [
            Paragraph(f"<font size=8>Proof: {contract_data.get('employer_signature_proof', '-')}</font>", body_style),
            Paragraph(f"<font size=8>Proof: {contract_data.get('employee_signature_proof', '-')}</font>", body_style)
        ]
    ]
    
    t = Table(sig_data, colWidths=[250, 250])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    
    story.append(t)
    doc.build(story)
    return output_path
