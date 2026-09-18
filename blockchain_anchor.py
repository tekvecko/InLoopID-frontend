#!/usr/bin/env python3
import sqlite3
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone

# Konfigurace cest
DB_PATH = os.path.expanduser("~/InLoopID/inloopid.db")
LEDGER_FILE = os.path.expanduser("~/InLoopID/backend/static/public_ledger.json")
OTS_DIR = os.path.expanduser("~/InLoopID/ots_proofs")

os.makedirs(os.path.dirname(LEDGER_FILE), exist_ok=True)
os.makedirs(OTS_DIR, exist_ok=True)

def generate_daily_block():
    print("[System] Zahajuji proces ukotveni do blockchainu...")
    
    # 1. Nacteni predchoziho stavu (zajisteni kontinuity)
    if os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE, 'r', encoding='utf-8') as f:
            try:
                chain = json.load(f)
                prev_hash = chain[-1]['block_hash']
            except json.JSONDecodeError:
                chain = []
                prev_hash = "GENESIS_00000000000000000000000000000000000000000000000000000000"
    else:
        chain = []
        prev_hash = "GENESIS_00000000000000000000000000000000000000000000000000000000"

    # 2. Ziskani vsech platnych hashu z lokalni databaze
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT content_hash FROM verifiable_credential_anchor WHERE content_hash IS NOT NULL")
        rows = cursor.fetchall()
        conn.close()
        
        current_hashes = sorted([r[0] for r in rows])
    except Exception as e:
        print(f"[Chyba] Nelze precist databazi: {e}")
        return

    if not current_hashes:
        print("[Info] Zadne hashe k ukotveni.")
        return

    # 3. Vytvoreni Root hashe (agregace databaze a predchoziho bloku)
    block_content = prev_hash + "".join(current_hashes)
    block_hash = hashlib.sha256(block_content.encode('utf-8')).hexdigest()

    # Pokud se stav nezmenil (zadne nove smlouvy), nekotvime zbytecne
    if chain and chain[-1]['block_hash'] == block_hash:
        print("[Info] Stav se nezmenil. Neni nutne vytvaret novy blok.")
        return

    # 4. Priprava souboru pro OpenTimestamps
    stamp_file = os.path.join(OTS_DIR, f"block_{block_hash}.txt")
    with open(stamp_file, 'w', encoding='utf-8') as f:
        f.write(block_hash)

    # 5. Odeslani do site Bitcoin (OpenTimestamps)
    ots_proof_file = f"{stamp_file}.ots"
    try:
        print(f"[Sít] Odesilam hash {block_hash[:16]}... do site Bitcoin (OTS)")
        # Volame binarku ots z opentimestamps-client
        subprocess.run(["ots", "stamp", stamp_file], check=True, capture_output=True)
        ots_success = True
        print("[Uspesno] Blockchain ukotveni potvrzeno kalendarnim serverem.")
    except subprocess.CalledProcessError as e:
        print(f"[Kriticka chyba] Selhalo ukotveni do OTS. Zkontrolujte pripojeni k internetu. Detail: {e.stderr.decode() if e.stderr else e}")
        ots_success = False

    # 6. Zapis do verejne knihy
    new_block = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "previous_block_hash": prev_hash,
        "included_documents_count": len(current_hashes),
        "block_hash": block_hash,
        "bitcoin_anchored": ots_success,
        "proof_file": os.path.basename(ots_proof_file) if ots_success else None
    }
    
    chain.append(new_block)
    
    # Atomicky zapis verejne uctovni knihy
    temp_ledger = f"{LEDGER_FILE}.tmp"
    with open(temp_ledger, 'w', encoding='utf-8') as f:
        json.dump(chain, f, indent=4)
    os.replace(temp_ledger, LEDGER_FILE)
        
    print(f"[Hotovo] Verejna casova osa byla aktualizovana a ulozena do: {LEDGER_FILE}")

if __name__ == "__main__":
    generate_daily_block()
