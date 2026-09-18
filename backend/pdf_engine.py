import os
from fpdf import FPDF, XPos, YPos, XPos, YPos

# Absolutní cesty k fontům
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(BASE_DIR, 'static', 'fonts')

class ContractPDF(FPDF):
    def header(self):
        self.set_font('Roboto', 'B', 16)
        self.cell(0, 10, 'PRACOVNÍ SMLOUVA', border=False, align='C')
        self.ln(6)
        self.set_font('Roboto', '', 10)
        self.cell(0, 10, 'uzavřená dle § 33 a násl. zákona č. 262/2006 Sb., zákoník práce', align='C')
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font('Roboto', '', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f'Strana {self.page_no()}/{{nb}} | Generováno platformou InLoopID | Audit Trail: Šifrováno AES-256', align='C')

def generate_contract_pdf(contract_data):
    pdf = ContractPDF()
    
    # Cesty k souborům fontů
    regular_font = os.path.join(FONT_DIR, 'Roboto-Regular.ttf')
    bold_font = os.path.join(FONT_DIR, 'Roboto-Bold.ttf')
    italic_font = os.path.join(FONT_DIR, 'Roboto-Italic.ttf')
    
    # Validace kritických fontů
    if not os.path.exists(regular_font) or not os.path.exists(bold_font):
        raise FileNotFoundError(f"Chybí kritické soubory fontů v adresáři: {FONT_DIR}")

    pdf.add_font('Roboto', '', regular_font)
    pdf.add_font('Roboto', 'B', bold_font)
    
    # Dynamická registrace kurzívy (bezpečný fallback)
    has_italic = os.path.exists(italic_font)
    if has_italic:
        pdf.add_font('Roboto', 'I', italic_font)
    
    pdf.add_page()
    
    # --- I. Smluvní strany ---
    pdf.set_font('Roboto', 'B', 12)
    pdf.cell(0, 10, 'I. Smluvní strany', new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font('Roboto', 'B', 10)
    pdf.cell(40, 6, 'Zaměstnavatel:', border=False)
    pdf.set_font('Roboto', '', 10)
    pdf.cell(0, 6, contract_data.get('employer_name', 'Název společnosti (Doplní Tenant)'), new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font('Roboto', 'B', 10)
    pdf.cell(40, 6, 'Sídlo:', border=False)
    pdf.set_font('Roboto', '', 10)
    pdf.cell(0, 6, contract_data.get('employer_address', 'Adresa sídla'), new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font('Roboto', 'B', 10)
    pdf.cell(40, 6, 'IČO:', border=False)
    pdf.set_font('Roboto', '', 10)
    pdf.cell(0, 6, contract_data.get('employer_ico', '00000000'), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    
    pdf.set_font('Roboto', 'B', 10)
    pdf.cell(40, 6, 'Zaměstnanec:', border=False)
    pdf.set_font('Roboto', '', 10)
    pdf.cell(0, 6, contract_data.get('employee_name', 'Jméno a příjmení (Doplní MojeID)'), new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font('Roboto', 'B', 10)
    pdf.cell(40, 6, 'E-mail:', border=False)
    pdf.set_font('Roboto', '', 10)
    pdf.cell(0, 6, contract_data.get('employee_email', 'email@uchazece.cz'), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)
    
    # --- II. Předmět smlouvy ---
    pdf.set_font('Roboto', 'B', 12)
    pdf.cell(0, 10, 'II. Předmět smlouvy', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Roboto', '', 10)
    
    p2_text = (
        f"1. Zaměstnanec se zavazuje pro zaměstnavatele vykonávat práci druhu: {contract_data.get('position', 'Nespecifikováno')}.\n"
        f"2. Místem výkonu práce je sjednáno: {contract_data.get('workplace', 'Nespecifikováno')}.\n"
        f"3. Den nástupu do práce byl sjednán na: {contract_data.get('start_date', 'Zatím nespecifikováno')}."
    )
    pdf.multi_cell(0, 6, p2_text)
    pdf.ln(4)
    
    # --- III. Trvání a zkušební doba ---
    pdf.set_font('Roboto', 'B', 12)
    pdf.cell(0, 10, 'III. Zkušební doba a trvání pracovního poměru', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Roboto', '', 10)
    
    p3_text = (
        f"1. Pracovní poměr se sjednává na dobu {contract_data.get('duration', 'neurčitou')}.\n"
        f"2. Sjednává se zkušební doba v délce {contract_data.get('probation_months', 3)} měsíců ode dne vzniku pracovního poměru."
    )
    pdf.multi_cell(0, 6, p3_text)
    pdf.ln(4)

    # --- IV. Mzda a pracovní doba ---
    pdf.set_font('Roboto', 'B', 12)
    pdf.cell(0, 10, 'IV. Mzda a pracovní doba', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Roboto', '', 10)
    
    p4_text = (
        f"1. Týdenní pracovní doba činí {contract_data.get('weekly_hours', 40)} hodin.\n"
        f"2. Zaměstnanci přísluší za vykonanou práci základní hrubá mzda ve výši {contract_data.get('salary', '0')} Kč měsíčně. "
        "Mzda je splatná v kalendářním měsíci následujícím po měsíci, ve kterém zaměstnanci vzniklo právo na mzdu."
    )
    pdf.multi_cell(0, 6, p4_text)
    pdf.ln(8)

    # --- V. Závěrečná ustanovení ---
    pdf.set_font('Roboto', 'B', 12)
    pdf.cell(0, 10, 'V. Závěrečná ustanovení', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Roboto', '', 10)
    
    p5_text = (
        "1. Práva a povinnosti výslovně neupravené touto smlouvou se řídí platným zákoníkem práce a vnitřními předpisy zaměstnavatele.\n"
        "2. Tato smlouva je generována a uzavírána elektronicky na platformě InLoopID v souladu s Nařízením eIDAS.\n"
        "3. Kryptografické pečetě a identifikační údaje (MojeID) jsou trvalou a neoddělitelnou součástí auditní stopy tohoto dokumentu."
    )
    pdf.multi_cell(0, 6, p5_text)
    pdf.ln(20)
    
    # --- Podpisy ---
    pdf.set_font('Roboto', 'B', 10)
    pdf.cell(90, 8, 'Za zaměstnavatele (HR Administrátor):', border=0)
    pdf.cell(90, 8, 'Zaměstnanec (Uchazeč):', border=0, new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font('Roboto', '', 10)
    pdf.set_text_color(0, 51, 153)
    pdf.cell(90, 6, '[ ELEKTRONICKÁ PEČEŤ ENTERPRISE ]', border=0)
    pdf.cell(90, 6, '[ AUTORIZOVÁNO PŘES MojeID ]', border=0, new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_text_color(0, 0, 0)
    # BEZPEČNÝ FALLBACK: Použije 'I', pouze pokud byl načten Roboto-Italic.ttf, jinak 'Regular'
    pdf.set_font('Roboto', 'I' if has_italic else '', 8)
    pdf.cell(90, 5, 'Kryptografický podpis (ECC P-256)', border=0)
    pdf.cell(90, 5, 'Biometrické ověření Passkey', border=0, new_x="LMARGIN", new_y="NEXT")
    
    return pdf.output()
