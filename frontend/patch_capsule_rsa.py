import os, re

file_path = "/data/data/com.termux/files/home/InloopID/frontend/src/components/HRDashboard.jsx"
if os.path.exists(file_path):
    with open(file_path, "r") as f:
        content = f.read()

    # 1. Úprava RSA bloku - bezpečné pročištění struktury JWK pro mobilní prohlížeče
    pattern1 = r"let rsaPriv = null;\s*try \{[\s\S]*?console\.warn\([^)]+\);\s*\}"
    replacement1 = """let rsaPriv = null;
                    let rsaErrorMsg = "";
                    try {
                        if (vaultData.encrypted_private_key && vaultData.private_key_iv) {
                            const hrKey = await deriveAESKey(vaultData.masterKey, "HR_SALT", 100000);
                            const rsaDec = await crypto.subtle.decrypt({name: "AES-GCM", iv: new Uint8Array(b64ToBuf(vaultData.private_key_iv))}, hrKey, new Uint8Array(b64ToBuf(vaultData.encrypted_private_key)));
                            let rsaJwk = JSON.parse(new TextDecoder().decode(rsaDec));
                            
                            // Bezpečná normalizace struktury JWK 
                            if (rsaJwk.privateKey) rsaJwk = rsaJwk.privateKey;
                            else if (rsaJwk.jwk) rsaJwk = rsaJwk.jwk;
                            
                            // Smazání problematických parametrů, které mobilní Chrome/WebView odmítá
                            delete rsaJwk.key_ops;
                            delete rsaJwk.ext;
                            
                            rsaPriv = await crypto.subtle.importKey("jwk", rsaJwk, {name: "RSA-OAEP", hash: "SHA-256"}, true, ["decrypt"]);
                        }
                    } catch(rsaErr) {
                        rsaErrorMsg = rsaErr.message || "Chyba struktury klíče JWK";
                        console.warn("RSA ERR:", rsaErr);
                    }"""
    
    # 2. Úprava varovné hlášky, aby tiskla reálný důvod chyby
    pattern2 = r"if\(\!rsaPriv\) \{\s*html \+= '<div class=\"error\"[^>]+>Upozornění: Firemní RSA klíč se nepodařilo inicializovat[^<]+</div>';\s*\}"
    replacement2 = """if(!rsaPriv) {
                        html += '<div class="error" style="font-size: 0.8em; background: rgba(245, 158, 11, 0.1); border-color: #f59e0b; color: #f59e0b;">Upozornění: Firemní RSA klíč se nepodařilo inicializovat (' + rsaErrorMsg + '). Plně zašifrované smlouvy ze systému nepůjde otevřít. Zobrazuji pouze záchranná data.</div>';
                    }"""

    content = re.sub(pattern1, replacement1, content)
    content = re.sub(pattern2, replacement2, content)
    
    with open(file_path, "w") as f:
        f.write(content)
    print("[+] Kapsle byla naučena ignorovat striktní parametry klíčů. Červený banner by měl zmizet.")
