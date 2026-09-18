#!/usr/bin/env python3
import hashlib, base64, sys

# Tento skript je určen pro soudního znalce jako "Black-box verifikátor"
def verify_audit_trail(payload_b64, stored_hash, eidas_tsr):
    print("--- ZAHÁJENÍ INTEGRITNÍHO TESTU ---")
    
    # 1. Dekódování
    try:
        data = base64.b64decode(payload_b64)
    except:
        return "CHYBA: Payload není validní Base64."

    # 2. Výpočet hashe (re-produkce důkazu)
    calc_hash = hashlib.sha256(data).hexdigest().upper()
    print(f"Vypočtený hash: {calc_hash}")
    print(f"Uložený hash:   {stored_hash}")
    
    if f"SHA256_{calc_hash}" == stored_hash:
        return "✅ INTEGRITA DOKUMENTU POTVRZENA (Hash shoda)"
    else:
        return "❌ INTEGRITA PORUŠENA (Hash nesouhlasí!)"

# Verifikace eIDAS razítka (Simulace pro auditora)
# Auditor spustí: openssl ts -verify -in audit_file.tsr -digest <HASH> -CAfile cacert.pem
print("Auditní skript připraven. Pro soudní řízení použijte OpenSSL verifikaci.")
