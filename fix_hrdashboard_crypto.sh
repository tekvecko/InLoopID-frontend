#!/bin/bash
set -e

echo "=========================================================="
echo " INLOOPID - OPRAVA HRDASHBOARD KRYPTOGRAFIE"
echo "=========================================================="

# 1. Vytvoření šifrovacího enginu pro HR
cat << 'JS_EOF' > ~/InloopID/frontend/src/utils/hrCryptoEngine.js
// Nativní WebCrypto implementace pro HR operace
export const encryptForHR = async (payloadString, masterPassword = "inloop-master-key-demo") => {
    const enc = new TextEncoder();
    
    // 1. Derivace klíče (musí odpovídat dešifrování ve Vaultu)
    const keyMaterial = await window.crypto.subtle.digest('SHA-256', enc.encode(masterPassword));
    const cryptoKey = await window.crypto.subtle.importKey(
        'raw', 
        keyMaterial, 
        { name: 'AES-GCM' }, 
        false, 
        ['encrypt']
    );

    // 2. Generování IV a šifrování
    const iv = window.crypto.getRandomValues(new Uint8Array(12));
    const encryptedBuffer = await window.crypto.subtle.encrypt(
        { name: 'AES-GCM', iv: iv },
        cryptoKey,
        enc.encode(payloadString)
    );

    // 3. Konverze do Base64 pro přenos
    const bufferToBase64 = (buffer) => btoa(String.fromCharCode(...new Uint8Array(buffer)));
    
    return {
        encrypted_payload: bufferToBase64(encryptedBuffer),
        iv: bufferToBase64(iv),
        wrapped_key: "hr-symmetric-direct" // Značka pro HR Vault, že nejde o asymetrické balení
    };
};
JS_EOF

# 2. Precizní integrace do HRDashboard.jsx
python3 << 'PY_EOF'
import os
import re

fp = os.path.expanduser("~/InloopID/frontend/src/components/HRDashboard.jsx")

# Záloha
os.system(f"cp {fp} {fp}.bak_crypto")

with open(fp, "r", encoding="utf-8") as f:
    content = f.read()

# Zajištění importu nového enginu
if "encryptForHR" not in content:
    content = "import { encryptForHR } from '../utils/hrCryptoEngine';\n" + content

# Oprava bloku pro standardní odeslání smlouvy (kolem řádku 256)
old_submit_logic = r"const mockEncryptedPayload = btoa\(unescape\(encodeURIComponent\(payloadString\)\)\);\s*const mockHash = await generateRealHash\(payloadString, \"SHA256_\"\);\s*await safeFetch\(`\$\{BACKEND_URL\}/hr/contracts`, \{ method: 'POST', headers: \{'Content-Type': 'application/json'\}, body: JSON\.stringify\(\{ tenant_id: tenantId\.trim\(\), email: contractForm\.email, content_hash: mockHash, encrypted_payload: mockEncryptedPayload, valid_until: .*? \}\) \}\);"

new_submit_logic = """
          const cryptoPackage = await encryptForHR(payloadString);
          const mockHash = await generateRealHash(payloadString, "SHA256_");

          await safeFetch(`${BACKEND_URL}/hr/contracts`, { 
              method: 'POST', 
              headers: {'Content-Type': 'application/json'}, 
              body: JSON.stringify({ 
                  tenant_id: tenantId.trim(), 
                  email: contractForm.email, 
                  content_hash: mockHash, 
                  encrypted_payload: cryptoPackage.encrypted_payload,
                  iv: cryptoPackage.iv,
                  wrapped_key: cryptoPackage.wrapped_key,
                  valid_until: contractForm.duration === 'urcita' ? parseDateToISO(contractForm.validUntil) : null, 
                  clearance_level: contractForm.clearance_level 
              }) 
          });
"""
content = re.sub(old_submit_logic, new_submit_logic, content, flags=re.DOTALL)

with open(fp, "w", encoding="utf-8") as f:
    f.write(content)

print("[+] Šifrovací bypass v HRDashboard úspěšně nahrazen WebCrypto API.")
PY_EOF

echo "=========================================================="
echo " HOTOVO. HRDashboard nyní generuje platné AES-GCM balíčky."
echo "=========================================================="
