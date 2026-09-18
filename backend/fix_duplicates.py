import os

file_path = os.path.expanduser('~/InloopID/backend/routes.py')
with open(file_path, 'r') as f:
    content = f.read()

marker = '# --- AUDITNÍ EXPORT ---'
if content.count(marker) > 1:
    # Zachování původního kódu a pouze jedné instance přidaného bloku
    clean_base = content.split(marker)[0]
    single_block = marker + content.split(marker)[1]
    
    # Vytvoření zálohy
    os.rename(file_path, file_path + '.dup.bak')
    
    # Zápis opraveného obsahu
    with open(file_path, 'w') as f:
        f.write(clean_base + single_block)
    print("[Systém] Identifikováno a odstraněno vícenásobné vložení auditního bloku.")
else:
    print("[Systém] Duplicity v souboru nebyly detekovány.")
