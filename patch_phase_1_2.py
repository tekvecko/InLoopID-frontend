import os

base_dir = "/data/data/com.termux/files/home/InloopID"
backend_dir = os.path.join(base_dir, "backend") if os.path.exists(os.path.join(base_dir, "backend")) else base_dir

# 1. Aktualizace závislostí
req_path = os.path.join(backend_dir, "requirements.txt")
with open(req_path, "r") as f: reqs = f.read()
if "celery" not in reqs:
    with open(req_path, "a") as f: f.write("\ncelery==5.3.6\nredis==5.0.1\n")
    print("[+] Requirements aktualizovány o Celery a Redis.")

# 2. Generování samostatného modulu úloh (tasks.py)
tasks_path = os.path.join(backend_dir, "tasks.py")
tasks_code = """import os, smtplib
from email.message import EmailMessage
from celery import Celery

redis_url = os.environ.get('REDIS_URL')

celery_app = Celery(
    'inloopid_tasks',
    broker=redis_url or 'memory://',
    backend=redis_url or 'cache+memory://'
)

# Fallback pro Termux (lokální vývoj bez Redisu)
if not redis_url:
    celery_app.conf.task_always_eager = True

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_invitations_task(self, invitations, company_name, smtp_server, smtp_port, smtp_user, smtp_pass):
    try:
        server = smtplib.SMTP_SSL(smtp_server, int(smtp_port)) if int(smtp_port) == 465 else smtplib.SMTP(smtp_server, int(smtp_port))
        if int(smtp_port) != 465: server.starttls()
        server.login(smtp_user, smtp_pass)
        
        for email, link in invitations:
            msg = EmailMessage()
            msg['Subject'] = f'Pozvánka do Onboarding portálu: {company_name}'
            msg['From'] = smtp_user
            msg['To'] = email
            
            html_content = f'''
            <html>
            <body style="font-family: Arial, sans-serif; background-color: #020617; color: #ffffff; padding: 40px; text-align: center;">
                <div style="max-width: 600px; margin: 0 auto; background-color: #0f172a; padding: 40px; border-radius: 24px; border: 1px solid #1e293b; box-shadow: 0 10px 25px rgba(0,0,0,0.5);">
                    <div style="width: 60px; height: 60px; background-color: rgba(59, 130, 246, 0.2); border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 20px;">
                        <span style="color: #3b82f6; font-size: 30px; font-weight: bold;">&#x1F6E1;</span>
                    </div>
                    <h2 style="color: #f8fafc; font-size: 24px; margin-bottom: 10px;">Vítejte v InLoopID</h2>
                    <p style="color: #94a3b8; font-size: 16px; line-height: 1.6; margin-bottom: 30px;">
                        Společnost <strong style="color: #ffffff;">{company_name}</strong> Vám zaslala pozvánku do bezpečného HR portálu.
                    </p>
                    <a href="{link}" style="display: inline-block; background-color: #2563eb; color: #ffffff; padding: 16px 32px; text-decoration: none; border-radius: 12px; font-weight: bold; font-size: 16px; transition: background-color 0.3s;">
                        Odemknout Trezor přes MojeID
                    </a>
                    <hr style="border: none; border-top: 1px solid #1e293b; margin: 40px 0 20px 0;">
                    <p style="color: #64748b; font-size: 12px; line-height: 1.5;">
                        Tento odkaz je jednorázový a kryptograficky chráněný architekturou Zero-Knowledge.<br>Nikomu jej nepřeposílejte.
                    </p>
                </div>
            </body>
            </html>
            '''
            msg.set_content(f"Dobrý den,\\nSpolečnost {company_name} Vás zve do HR portálu.\\nOdkaz: {link}")
            msg.add_alternative(html_content, subtype='html')
            server.send_message(msg)
            
        server.quit()
        return f"[SMTP] Odesláno {len(invitations)} pozvánek."
    except Exception as exc:
        print(f"[SMTP CHYBA] {exc}")
        raise self.retry(exc=exc)

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_contract_notice_task(self, email, company_name, smtp_server, smtp_port, smtp_user, smtp_pass):
    try:
        server = smtplib.SMTP_SSL(smtp_server, int(smtp_port)) if int(smtp_port) == 465 else smtplib.SMTP(smtp_server, int(smtp_port))
        if int(smtp_port) != 465: server.starttls()
        server.login(smtp_user, smtp_pass)

        msg = EmailMessage()
        msg['Subject'] = f'Nová smlouva k podpisu: {company_name}'
        msg['From'] = smtp_user
        msg['To'] = email

        html = f'''
        <div style="font-family: sans-serif; background: #0f172a; padding: 40px; color: white; text-align: center; border-radius: 16px;">
            <h2 style="color: #3b82f6;">Máte nový dokument v InLoopID</h2>
            <p style="color: #94a3b8;">Společnost <b>{company_name}</b> Vám zaslala smlouvu k elektronickému podpisu.</p>
            <a href="http://localhost:5173/employee" style="display: inline-block; padding: 15px 30px; background: #2563eb; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; margin-top: 20px;">Vstoupit do Trezoru</a>
        </div>
        '''
        msg.set_content(f"Nová smlouva k podpisu od {company_name}. Přihlaste se zde: http://localhost:5173/employee")
        msg.add_alternative(html, subtype='html')

        server.send_message(msg)
        server.quit()
        return f"[SMTP] Upozornění odesláno na {email}."
    except Exception as exc:
        print(f"[SMTP CHYBA] {exc}")
        raise self.retry(exc=exc)
"""
with open(tasks_path, "w") as f: f.write(tasks_code)
print("[+] Modul úloh (tasks.py) vygenerován.")

# 3. Patchování routes.py (Odstranění vláken a implementace tasků)
routes_path = os.path.join(backend_dir, "routes.py")
with open(routes_path, "r") as f: routes_content = f.read()

# Import tasků
if "from tasks import" not in routes_content:
    routes_content = routes_content.replace(
        "from flask import Blueprint", 
        "from tasks import send_invitations_task, send_contract_notice_task\nfrom flask import Blueprint"
    )

# Nahrazení logiky pro hromadný import (bulk-import)
old_bulk = """        if smtp_user and smtp_pass:
            threading.Thread(
                target=send_invitation_emails_async, 
                args=(emails_to_dispatch, comp.company_name, smtp_server, smtp_port, smtp_user, smtp_pass)
            ).start()"""
new_bulk = """        if smtp_user and smtp_pass:
            send_invitations_task.delay(emails_to_dispatch, comp.company_name, smtp_server, smtp_port, smtp_user, smtp_pass)"""
routes_content = routes_content.replace(old_bulk, new_bulk)

# Nahrazení logiky pro novou smlouvu (hr/contracts)
old_contract = """        if smtp_user and smtp_pass and comp:
            def send_notice():
                try:
                    server = smtplib.SMTP_SSL(smtp_server, smtp_port) if smtp_port == 465 else smtplib.SMTP(smtp_server, smtp_port)
                    if smtp_port != 465: server.starttls()
                    server.login(smtp_user, smtp_pass)

                    msg = EmailMessage()
                    msg['Subject'] = f'Nová smlouva k podpisu: {comp.company_name}'
                    msg['From'] = smtp_user
                    msg['To'] = email

                    html = f\"\"\"
                    <div style="font-family: sans-serif; background: #0f172a; padding: 40px; color: white; text-align: center; border-radius: 16px;">
                        <h2 style="color: #3b82f6;">Máte nový dokument v InLoopID</h2>
                        <p style="color: #94a3b8;">Společnost <b>{comp.company_name}</b> Vám zaslala smlouvu k elektronickému podpisu.</p>
                        <a href="http://localhost:5173/employee" style="display: inline-block; padding: 15px 30px; background: #2563eb; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; margin-top: 20px;">Vstoupit do Trezoru</a>
                    </div>
                    \"\"\"
                    msg.set_content(f"Nová smlouva k podpisu od {comp.company_name}. Přihlaste se zde: http://localhost:5173/employee")
                    msg.add_alternative(html, subtype='html')

                    server.send_message(msg)
                    server.quit()
                except Exception as e:
                    print(f"[SMTP CHYBA] {e}")

            threading.Thread(target=send_notice).start()"""
new_contract = """        if smtp_user and smtp_pass and comp:
            send_contract_notice_task.delay(email, comp.company_name, smtp_server, smtp_port, smtp_user, smtp_pass)"""
routes_content = routes_content.replace(old_contract, new_contract)

with open(routes_path, "w") as f: f.write(routes_content)
print("[+] Soubor routes.py aktualizován: Kritická vlákna přepsána na Celery úlohy.")
