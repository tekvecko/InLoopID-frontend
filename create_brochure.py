import os
from fpdf import FPDF, XPos, YPos

# Definice přesné cesty k fontům
FONT_DIR = os.path.expanduser("~/InloopID/backend/static/fonts")
FONT_REG = os.path.join(FONT_DIR, "Roboto-Regular.ttf")
FONT_BOLD = os.path.join(FONT_DIR, "Roboto-Bold.ttf")

class PRBrochure(FPDF):
    def __init__(self):
        super().__init__()
        # Kontrola existence fontů
        if not os.path.exists(FONT_REG) or not os.path.exists(FONT_BOLD):
            raise FileNotFoundError(f"Fonty nebyly nalezeny v {FONT_DIR}. Zkontroluj cestu.")
        
        # Načítání fontů bez zastaralého parametru uni=True
        self.add_font("Roboto", "", FONT_REG)
        self.add_font("Roboto", "B", FONT_BOLD)

    def header(self):
        self.set_font("Roboto", "B", 20)
        self.cell(0, 10, "InLoopID: Digitální suverenita", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(37, 99, 235)
        self.line(10, 25, 200, 25)
        self.ln(10)

    def chapter_title(self, title):
        self.set_font("Roboto", "B", 14)
        self.set_fill_color(241, 245, 249)
        self.cell(0, 10, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
        self.ln(5)

    def chapter_body(self, body):
        self.set_font("Roboto", "", 11)
        self.multi_cell(0, 7, body)
        self.ln(5)

# Generování brožury
try:
    pdf = PRBrochure()
    pdf.add_page()

    # Intro - použijeme Regular font místo chybějícího Italic, ale odlišíme ho barvou
    pdf.set_font("Roboto", "", 12)
    pdf.set_text_color(71, 85, 105) # Břidlicově šedá (Slate-600)
    pdf.multi_cell(0, 7, "Profesionální standard pro bezpečné, auditovatelné a právně nevyvratitelné HR procesy.")
    pdf.set_text_color(0, 0, 0) # Návrat k černé barvě
    pdf.ln(10)

    # Část 1
    pdf.chapter_title("I. Pro Management: Strategická suverenita")
    pdf.chapter_body("InLoopID není jen software. Je to pojistka proti kybernetickým rizikům a legislativním sankcím. Zero-Knowledge architektura zajišťuje, že data opouštějí vaše prostředí již zašifrovaná. Fungujeme jako 'Slepý notář' – nevidíme obsah vašich smluv, nemůžeme je ztratit ani zneužít. Vaše firemní know-how a citlivá data zaměstnanců zůstávají ve vašem vlastnictví.")

    # Část 2
    pdf.chapter_title("II. Pro HR: Compliance a Automatizace")
    pdf.chapter_body("Eliminujte administrativní zátěž a chyby, které vedou k pokutám. Systém automaticky hlídá limity DPP/DPČ, zkušební doby a povinné zákonné doložky. V případě kontroly z inspektorátu práce generujete kryptograficky validovaný report, který prokazuje nezměnitelnost dokumentů od okamžiku podpisu.")

    # Část 3
    pdf.chapter_title("III. Pro Zaměstnance: Důvěra a jednoduchost")
    pdf.chapter_body("Využíváme MojeID/BankID. Zaměstnanec má jistotu, že jedná s ověřenou institucí. InLoopID vrací lidem kontrolu nad jejich digitální identitou. Proces podpisu je rychlý, intuitivní a transparentní.")

    # Uložení do správné složky
    output_path = os.path.expanduser("~/InloopID/InLoopID_PR_Brochure.pdf")
    pdf.output(output_path)
    print(f"Brožura byla úspěšně vygenerována: {output_path}")

except Exception as e:
    print(f"Chyba při generování PDF: {e}")
