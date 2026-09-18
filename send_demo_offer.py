#!/usr/bin/env python3
import smtplib
import os
import sys
from email.message import EmailMessage
from dotenv import load_dotenv

# Terminálové formátování
C_OK = '\033[92m'
C_INFO = '\033[94m'
C_ERR = '\033[91m'
C_END = '\033[0m'

def send_offer(recipient_email, company_name):
    # Explicitní definice cesty k backendovému .env souboru
    env_path = os.path.expanduser('~/InloopID/backend/.env')
    
    print(f"{C_INFO}[System] Inicializace rozesílacího modulu...{C_END}")
    print(f"{C_INFO}[Config] Načítání prostředí z: {env_path}{C_END}")

    if not os.path.exists(env_path):
        print(f"{C_ERR}[Kritická chyba] Konfigurační soubor nebyl nalezen. Ujistěte se, že cesta existuje.{C_END}")
        sys.exit(1)

    load_dotenv(dotenv_path=env_path)

    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', 465))
    smtp_user = os.environ.get('SMTP_EMAIL')
    smtp_pass = os.environ.get('SMTP_PASSWORD')

    if not smtp_user or not smtp_pass:
        print(f"{C_ERR}[Konfigurační chyba] Proměnné SMTP_EMAIL a SMTP_PASSWORD nejsou definovány v {env_path}.{C_END}")
        sys.exit(1)

    msg = EmailMessage()
    msg['Subject'] = f'Digitalizace HR a 100% právní jistota pro {company_name}'
    msg['From'] = f"InLoopID Enterprise <{smtp_user}>"
    msg['To'] = recipient_email

    # Fallback textová verze
    text_content = f"""
    Vážené vedení společnosti {company_name},
    
    představujeme Vám InLoopID - platformu pro bezpečné digitální uzavírání pracovněprávních vztahů.
    
    JAK TO FUNGUJE (PIPELINE):
    1. Import a Příprava: Nahrajete data zaměstnanců. Systém automaticky sestaví přesné návrhy smluv.
    2. Zero-Knowledge Šifrování: Smlouvy jsou zašifrovány přímo u Vás. My do nich nevidíme.
    3. Ověření přes MojeID: Uchazeč prokazuje svou totožnost státem garantovanou e-identitou.
    4. Podpis a eIDAS Pečeť: Po podpisu je dokument zafixován kvalifikovaným časovým razítkem.
    
    PRÁVNÍ GARANCE:
    - Zero-Knowledge architektura Vás chrání před úniky dat (GDPR).
    - MojeID eliminuje podvody s identitou.
    - eIDAS časové razítko zaručuje absolutní nevyvratitelnost u soudu.
    
    Rádi Vám systém předvedeme na 15minutovém demo hovoru.
    
    Tým InLoopID
    """
    msg.set_content(text_content)

    # Prémiová HTML verze
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #334155; background-color: #f8fafc; margin: 0; padding: 0; }}
            .container {{ max-width: 650px; margin: 40px auto; background: #ffffff; border-radius: 24px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; }}
            .header {{ background-color: #0f172a; padding: 40px 30px; text-align: center; border-bottom: 4px solid #2563eb; }}
            .header h1 {{ color: #ffffff; margin: 0; font-size: 28px; font-weight: 800; letter-spacing: -0.5px; }}
            .header p {{ color: #94a3b8; margin: 10px 0 0 0; font-size: 16px; }}
            .content {{ padding: 40px 30px; }}
            .intro {{ font-size: 18px; color: #1e293b; font-weight: 600; margin-bottom: 25px; }}
            .section-title {{ color: #0f172a; font-size: 14px; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 700; border-bottom: 1px solid #e2e8f0; padding-bottom: 8px; margin-top: 35px; margin-bottom: 20px; }}
            
            /* Pipeline styl */
            .pipeline {{ margin: 0; padding: 0; list-style: none; }}
            .pipeline li {{ display: flex; align-items: flex-start; margin-bottom: 20px; background: #f8fafc; padding: 20px; border-radius: 16px; border: 1px solid #f1f5f9; }}
            .step-num {{ background: #2563eb; color: white; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; margin-right: 15px; flex-shrink: 0; line-height: 28px; text-align: center; }}
            .step-content h3 {{ margin: 0 0 5px 0; color: #0f172a; font-size: 16px; }}
            .step-content p {{ margin: 0; color: #64748b; font-size: 14px; }}
            
            /* Garanční bloky */
            .guarantees {{ display: grid; grid-template-columns: 1fr; gap: 15px; }}
            .guarantee-box {{ border-left: 4px solid #10b981; background: #ecfdf5; padding: 15px 20px; border-radius: 0 12px 12px 0; }}
            .guarantee-box h4 {{ color: #065f46; margin: 0 0 5px 0; font-size: 15px; }}
            .guarantee-box p {{ color: #047857; margin: 0; font-size: 13px; }}
            
            .cta-container {{ text-align: center; margin-top: 40px; padding-top: 30px; border-top: 1px solid #e2e8f0; }}
            .cta-button {{ display: inline-block; background-color: #2563eb; color: #ffffff !important; text-decoration: none; padding: 16px 36px; border-radius: 12px; font-weight: bold; font-size: 16px; box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2); transition: background-color 0.3s; }}
            .footer {{ text-align: center; padding: 20px; color: #94a3b8; font-size: 12px; background: #f8fafc; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>INLOOP<span style="color: #3b82f6;">ID</span></h1>
                <p>Enterprise platforma pro digitální onboarding</p>
            </div>
            
            <div class="content">
                <p class="intro">Vážené vedení společnosti {company_name},</p>
                <p>při správě HR agendy čelí většina společností zásadnímu problému: jak digitalizovat podepisování pracovních smluv, radikálně zrychlit procesy, a přitom <strong>nevystavit firmu riziku úniku citlivých osobních dat (GDPR)</strong>.</p>
                
                <h2 class="section-title">Jak funguje proces (Pipeline)</h2>
                <ul class="pipeline">
                    <li>
                        <div class="step-num">1</div>
                        <div class="step-content">
                            <h3>Migrace a Příprava</h3>
                            <p>Systém načte Vaše data a automaticky sestaví přesné návrhy pracovních smluv. Integrovaný radar ihned ohlídá zákonné limity (např. délku zkušební doby).</p>
                        </div>
                    </li>
                    <li>
                        <div class="step-num">2</div>
                        <div class="step-content">
                            <h3>Zero-Knowledge Šifrování</h3>
                            <p>Dokumenty jsou nevratně zašifrovány přímo na Vašem zařízení. Naše servery plní pouze roli transportní vrstvy – do obsahu smluv nikdy nevidíme.</p>
                        </div>
                    </li>
                    <li>
                        <div class="step-num">3</div>
                        <div class="step-content">
                            <h3>Ověření státní identitou (MojeID)</h3>
                            <p>Konec podvodům. Zaměstnanec nekliká pouze na odkaz v e-mailu, ale musí prokázat svou totožnost prostřednictvím bankovní identity nebo MojeID.</p>
                        </div>
                    </li>
                    <li>
                        <div class="step-num">4</div>
                        <div class="step-content">
                            <h3>Podpis a eIDAS Pečeť</h3>
                            <p>Po elektronickém podpisu oběma stranami je dokument zafixován kvalifikovaným časovým razítkem, čímž vzniká nevyvratitelný právní originál.</p>
                        </div>
                    </li>
                </ul>

                <h2 class="section-title">Garantovaná právní jistota</h2>
                <div class="guarantees">
                    <div class="guarantee-box">
                        <h4>Fyzické vlastnictví dat (GDPR)</h4>
                        <p>Díky architektuře "Slepého notáře" nenese Vaše společnost riziko úniku dat z cloudu. Kapsli se smlouvami lze navíc exportovat pro offline zálohování.</p>
                    </div>
                    <div class="guarantee-box">
                        <h4>Legislativní soulad</h4>
                        <p>Kvalifikovaná časová razítka (TSA) dle nařízení eIDAS zaručují, že dokumenty obstojí při jakékoliv kontrole z inspektorátu práce či u soudu.</p>
                    </div>
                </div>

                <div class="cta-container">
                    <p style="margin-bottom: 20px; font-weight: 600; color: #475569;">Přechod na náš systém lze zvládnout za jediné odpoledne.</p>
                    <a href="https://inloopid.com/b2b/register" class="cta-button">Domluvit 15minutové Demo</a>
                </div>
            </div>
            
            <div class="footer">
                Tento e-mail byl zaslán zástupcům společnosti {company_name}.<br>
                © 2026 InLoopID. Zabezpečené digitální HR procesy.
            </div>
        </div>
    </body>
    </html>
    """
    
    msg.add_alternative(html_content, subtype='html')

    print(f"{C_INFO}[Network] Navazování spojení se serverem {smtp_server}:{smtp_port}...{C_END}")
    
    try:
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        print(f"{C_OK}[ÚSPĚCH] Profesionální nabídka odeslána na e-mail: {recipient_email} (Klient: {company_name}){C_END}")
    except Exception as e:
        print(f"{C_ERR}[CHYBA] Odeslání selhalo. Zkontrolujte spojení a platnost údajů v .env souboru. Detail výjimky: {str(e)}{C_END}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"{C_INFO}Použití: python send_demo_offer.py <email_prijemce> <nazev_firmy>{C_END}")
        print(f"{C_INFO}Příklad: python send_demo_offer.py ceo@targetcompany.cz 'Target Company a.s.'{C_END}")
        sys.exit(1)
        
    recipient = sys.argv[1]
    company = sys.argv[2]
    send_offer(recipient, company)
