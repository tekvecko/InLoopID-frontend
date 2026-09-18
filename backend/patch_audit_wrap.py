import os

file_path = "/data/data/com.termux/files/home/InloopID/backend/routes.py"

with open(file_path, 'r') as f:
    content = f.read()

# Kód z předchozí iterace, který způsobil pád
old_loop = """    for cred in credentials:
        hash_val = cred.content_hash if cred.content_hash else "HASH_PENDING"
        pdf.set_font("Roboto", "B", 8)
        pdf.cell(0, 5, f"ID: {cred.credential_id} | STATUS: {cred.status.upper()}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Roboto", "", 8)
        pdf.multi_cell(0, 5, f"DID: {cred.subject_did}")
        pdf.multi_cell(0, 5, f"HASH: {hash_val}")
        pdf.ln(3)"""

# Nový kód s vynuceným textwrapem
new_loop = """    for cred in credentials:
        import textwrap
        did_val = cred.subject_did if cred.subject_did else "DID_PENDING"
        hash_val = cred.content_hash if cred.content_hash else "HASH_PENDING"
        
        # Bezpečné zalomení dlouhých řetězců (vynucené natvrdo po 60 znacích)
        did_wrapped = "\\n".join(textwrap.wrap(did_val, width=60, break_long_words=True))
        hash_wrapped = "\\n".join(textwrap.wrap(hash_val, width=60, break_long_words=True))
        
        pdf.set_font("Roboto", "B", 8)
        pdf.cell(0, 5, f"ID: {cred.credential_id} | STATUS: {cred.status.upper()}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Roboto", "", 8)
        # Použijeme multi_cell s menším řádkováním (4) pro kompaktnější vzhled
        pdf.multi_cell(0, 4, f"DID: {did_wrapped}")
        pdf.multi_cell(0, 4, f"HASH: {hash_wrapped}")
        pdf.ln(3)"""

if old_loop in content:
    content = content.replace(old_loop, new_loop)
    with open(file_path, 'w') as f:
        f.write(content)
    print("[+] Oprava zalamování textu úspěšně aplikována.")
else:
    print("[-] Nepodařilo se najít starý kód. Je možné, že už byl upraven.")

