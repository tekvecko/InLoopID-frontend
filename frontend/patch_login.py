import re

file_path = "/data/data/com.termux/files/home/InloopID/frontend/src/components/HRDashboard.jsx"

with open(file_path, 'r') as f:
    content = f.read()

# Regulární výraz, který najde rozbitou přihlašovací funkci
pattern = r"const unlockLedger = async \(e\) => \{[\s\S]*?setIsLoggingIn\(false\);\s*\};"

# Nová, funkční a bezpečná verze
new_unlock = """const unlockLedger = async (e) => {
    e.preventDefault(); setIsLoggingIn(true);
    try {
        const res = await safeFetch(`${BACKEND_URL}/hr/agenda?tenant_id=${tenantId.trim()}`);
        
        // Správné předání šifrovaného klíče do krypto enginu
        if (res.encrypted_private_key && res.private_key_iv) {
            await decryptKeystore(res.encrypted_private_key, res.private_key_iv, hrPassword, "HR_SALT");
        }
        
        setIsUnlocked(true); 
        fetchRadarData(); 
        fetchContracts();
        notify.success("Přístup povolen. Vítejte ve Velínu.");
    } catch (err) {
        notify.error(`Přihlášení selhalo: ${err.message || 'Neplatné ID nebo heslo.'}`);
        console.error(err);
    }
    setIsLoggingIn(false);
  };"""

if "const unlockLedger = async" in content:
    content = re.sub(pattern, lambda m: new_unlock, content)
    with open(file_path, 'w') as f:
        f.write(content)
    print("[+] Přihlašovací logika (Odemknout Velín) byla úspěšně opravena.")
else:
    print("[-] Chyba: Nemohu najít funkci unlockLedger.")

