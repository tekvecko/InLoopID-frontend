import os
import logging
import smtplib
from email.message import EmailMessage
from datetime import datetime

# Konfigurace přes proměnné prostředí
SMTP_SERVER = os.environ.get("SMTP_SERVER", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")

SPOOL_DIR = os.path.expanduser("~/InloopID/backend/mail_spool")

def send_transactional_email(to_address, subject, html_content):
    """
    Odešle e-mail přes SMTP, nebo jej uloží do lokálního spooleru pro účely auditu a dema.
    """
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = "InLoopID Enterprise <noreply@inloopid.com>"
    msg['To'] = to_address
    msg.set_content("Tento e-mail vyžaduje e-mailového klienta s podporou HTML.")
    msg.add_alternative(html_content, subtype='html')

    if SMTP_SERVER and SMTP_USER and SMTP_PASS:
        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)
            logging.info(f"[MAIL ENGINE] Zpráva odeslána na {to_address} přes {SMTP_SERVER}.")
            return True
        except Exception as e:
            logging.error(f"[MAIL ENGINE] Kritické selhání SMTP: {e}")
            return False
    else:
        # Fallback do lokálního adresáře (Zero-Config Demo Režim)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_email = to_address.replace("@", "_at_").replace(".", "_")
        file_name = f"{timestamp}_{safe_email}.html"
        file_path = os.path.join(SPOOL_DIR, file_name)
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            logging.info(f"[MAIL ENGINE - DEMO] E-mail simulován. Uloženo do: {file_path}")
            return True
        except Exception as e:
            logging.error(f"[MAIL ENGINE] Nelze zapsat do spooleru: {e}")
            return False

def generate_onboarding_template(company_name, tenant_id):
    """Generuje korporátní HTML šablonu pro nové klienty."""
    return f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #0B1120; color: #f8fafc; padding: 40px;">
            <div style="max-w-2xl mx-auto; background-color: #112240; padding: 30px; border-radius: 12px; border: 1px solid #1e3a8a;">
                <h2 style="color: #60a5fa;">Vítejte v InLoopID Enterprise</h2>
                <p>Vážený administrátore,</p>
                <p>Váš Zero-Knowledge kryptografický workspace pro společnost <strong>{company_name}</strong> byl úspěšně inicializován.</p>
                <div style="background-color: #0A192F; padding: 15px; border-left: 4px solid #3b82f6; margin: 20px 0; font-family: monospace;">
                    <strong>Tenant ID:</strong> {tenant_id}<br/>
                    <strong>Stav eIDAS uzlu:</strong> Synchronizováno
                </div>
                <p>Z bezpečnostních důvodů nebyl privátní klíč odeslán na naše servery. Pro přístup do HR Vaultu použijte lokální Master Key, který jste vygenerovali během registrace.</p>
                <p style="color: #64748b; font-size: 12px; margin-top: 40px;">
                    Toto je automatizovaná zpráva systému InLoopID. Neodpovídejte na ni.
                </p>
            </div>
        </body>
    </html>
    """
