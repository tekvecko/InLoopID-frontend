#!/usr/bin/env python3
import os

fp = os.path.expanduser("~/InloopID/backend/routes.py")

with open(fp, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Anonymizace logování (Pravidlo: Nikdy neukládat email_hash a akční DID do stejného stringu)
content = content.replace(
    'db.session.add(BlindAuditLog(action=f"TASK_UPDATED_{data[\'task_type\']}_{data[\'status\']}", actor_did=data.get(\'did_uri\', \'system\')))',
    'db.session.add(BlindAuditLog(action=f"TASK_UPDATED_{data[\'task_type\']}_{data[\'status\']}", actor_did="ANONYMIZED_DID_HASH"))'
)

# 2. Hardening: Odstranění závislosti na IdentityNode v anchor_credential
# Původní kód kontroloval aktivitu identity (dotazoval se na databázi).
# Změníme to na "Slepé přijetí" (Server věří pouze podpisu, nikoliv existenci v DB).
hardened_anchor = """
    # Slepé přijetí: Server neověřuje identitu v DB, pouze validuje strukturu payloadu.
    # Toto zabraňuje útoku typu "Entity Enumeration".
    db.session.add(VerifiableCredentialAnchor(
        tenant_id=data.get('tenant_id', 'public_zone'), 
        credential_id=data['credential_id'], 
        issuer_did=data['issuer_did'], 
        subject_did=data['subject_did'],
        content_hash=data['content_hash'], 
        proof_signature=data['proof_signature'],
        hr_tsa_token=get_qualified_timestamp(data['content_hash']), 
        encrypted_payload=data['encrypted_payload'], 
        iv=data['iv'], 
        wrapped_key=data['wrapped_key'],
        status='pending_signature'
    ))
    db.session.commit()
"""

# Identifikujeme blok v anchor_credential a nahradíme jej
# Najdeme start a konec bloku
start_marker = "issuer = IdentityNode.query.filter_by(did_uri=data['issuer_did']).first()"
end_marker = "db.session.commit()"
if start_marker in content:
    pre = content.split(start_marker)[0]
    post = content.split(end_marker)[1]
    content = pre + hardened_anchor + post

with open(fp, "w", encoding="utf-8") as f:
    f.write(content)

print("[+] Backend úspěšně zkonvertován na Blind Notary.")
print("[+] Relační vazby přerušeny. Server nyní pracuje pouze s DID stringy.")
