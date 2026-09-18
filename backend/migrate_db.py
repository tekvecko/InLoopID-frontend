import sys
sys.path.append("/data/data/com.termux/files/home/InloopID/backend")
from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        db.session.execute(text("ALTER TABLE verifiable_credential_anchors ADD COLUMN valid_until DATETIME"))
        db.session.commit()
        print("[+] Skvělé, sloupec 'valid_until' byl přidán do databáze.")
    except Exception as e:
        print("[-] Úprava databáze přeskočena (sloupec již existuje).")
