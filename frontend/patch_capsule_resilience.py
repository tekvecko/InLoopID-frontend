import os

file_path = "/data/data/com.termux/files/home/InloopID/frontend/src/components/HRDashboard.jsx"
if os.path.exists(file_path):
    with open(file_path, "r") as f:
        content = f.read()
    
    start_marker = "const coldVaultTemplate = (ciphertextBase64, ivBase64) => `"
    end_marker = "\nexport const HRDashboard = () => {"
    
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)
    
    if start_idx != -1 and end_idx != -1:
        new_template = """const coldVaultTemplate = (ciphertextBase64, ivBase64) => `<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <title>InLoopID Cold Vault</title>
    <style>
        body { font-family: monospace; background: #020617; color: #f8fafc; padding: 40px; margin: 0; line-height: 1.6; }
        .container { max-width: 900px; margin: 0 auto; background: #0f172a; padding: 50px; border-radius: 24px; border: 1px solid #1e293b; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5); }
        h1 { color: #3b82f6; text-align: center; font-size: 2.5em; margin-bottom: 10px; }
        .subtitle { text-align: center; color: #64748b; margin-bottom: 40px; }
        input { width: 100%; padding: 20px; background: #020617; border: 1px solid #1e293b; color: white; border-radius: 16px; margin-bottom: 20px; font-size: 18px; box-sizing: border-box; text-align: center; letter-spacing: 1px; }
        input:focus { outline: none; border-color: #3b82f6; }
        button { width: 100%; background: #2563eb; color: white; border: none; padding: 20px; border-radius: 16px; font-weight: bold; cursor: pointer; font-size: 18px; transition: background 0.3s; }
        button:hover { background: #1d4ed8; }
        .contract { background: #020617; border: 1px solid #1e293b; padding: 25px; border-radius: 16px; margin-top: 25px; }
        .contract h3 { margin-top: 0; color: #10b981; }
        .error { color: #ef4444; font-weight: bold; padding: 20px; background: rgba(239, 68, 68, 0.1); border-radius: 12px; text-align: center; margin-bottom: 20px; }
        .success { color: #10b981; font-weight: bold; text-align: center; display: block; margin-top: 20px; }
        .download-btn { display: inline-block; padding: 10px 20px; background: #1e293b; color: #3b82f6; text-decoration: none; border-radius: 8px; font-weight: bold; margin-top: 15px; }
        .download-btn:hover { background: #334155; }
    </style>
</head>
<body>
    <div class="container">
        <h1>InLoopID Cold Vault</h1>
        <p class="subtitle">Tento soubor je kvantově odolný off-grid archiv. Obsahuje všechny vaše smlouvy. Pro odemčení zadejte svůj 24slovný Master Seed.</p>
        <input type="text" id="seed" placeholder="Zadejte 24 slov oddělených mezerou..." autocomplete="off" />
        <button onclick="unlockVault()" id="btn">Dešifrovat Trezor a Zobrazit Dokumenty</button>
        <div id="status"></div>
        <div id="content"></div>
    </div>
    <script>
        const CIPHERTEXT = "${ciphertextBase64}";
        const IV = "${ivBase64}";

        const b64ToBuf = (b64) => {
            const s = window.atob(b64);
            const bytes = new Uint8Array(s.length);
            for (let i = 0; i < s.length; i++) bytes[i] = s.charCodeAt(i);
            return bytes.buffer;
        };

        const deriveAESKey = async (password, salt, iters) => {
            const enc = new TextEncoder();
            const keyMaterial = await crypto.subtle.importKey("raw", enc.encode(password), {name: "PBKDF2"}, false, ["deriveBits", "deriveKey"]);
            return crypto.subtle.deriveKey(
                { name: "PBKDF2", salt: enc.encode(salt), iterations: iters, hash: "SHA-256" },
                keyMaterial, { name: "AES-GCM", length: 256 }, true, ["encrypt", "decrypt"]
            );
        };

        async function unlockVault() {
            const words = document.getElementById('seed').value.trim().toLowerCase().replace(/\\s+/g, ' ');
            const status = document.getElementById('status');
            const btn = document.getElementById('btn');
            
            if(!words) return;
            btn.disabled = true;
            status.innerHTML = '<span class="success">Odemykám... Provádím PBKDF2 výpočet s 1 000 000 iteracemi (ochrana proti kvantovému útoku). To může chvíli trvat...</span>';
            
            setTimeout(async () => {
                try {
                    const vaultKey = await deriveAESKey(words, "INLOOP_COLD_VAULT_SALT", 1000000);
                    let decrypted;
                    try {
                        decrypted = await crypto.subtle.decrypt({name: "AES-GCM", iv: b64ToBuf(IV)}, vaultKey, b64ToBuf(CIPHERTEXT));
                    } catch (aesErr) {
                        throw new Error("Hlavní obálku kapsle nelze dešifrovat. Buď je Seed chybný, nebo byla data poškozena.");
                    }
                    
                    const vaultData = JSON.parse(new TextDecoder().decode(decrypted));
                    status.innerHTML = '<span class="success">Kapsle odemčena. Rekonstruuji vnitřní klíče a data...</span>';
                    
                    let rsaPriv = null;
                    try {
                        if (vaultData.encrypted_private_key && vaultData.private_key_iv) {
                            const hrKey = await deriveAESKey(vaultData.masterKey, "HR_SALT", 100000);
                            const rsaDec = await crypto.subtle.decrypt({name: "AES-GCM", iv: b64ToBuf(vaultData.private_key_iv)}, hrKey, b64ToBuf(vaultData.encrypted_private_key));
                            const rsaJwk = JSON.parse(new TextDecoder().decode(rsaDec));
                            // Opravené oprávnění (pouze decrypt)
                            rsaPriv = await crypto.subtle.importKey("jwk", rsaJwk, {name: "RSA-OAEP", hash: "SHA-256"}, true, ["decrypt"]);
                        }
                    } catch(rsaErr) {
                        console.warn("Firemní RSA klíč nelze načíst. Pokračuji v renderování nezávislých smluv.", rsaErr);
                    }
                    
                    let html = '<h2 style="margin-top: 40px; border-bottom: 1px solid #1e293b; padding-bottom: 10px;">Archiv smluv (' + vaultData.contracts.length + ')</h2>';
                    
                    if(!rsaPriv) {
                        html += '<div class="error" style="font-size: 0.8em;">Upozornění: Firemní RSA klíč se nepodařilo inicializovat. Vaše starší plně zašifrované záznamy mohou ohlásit chybu.</div>';
                    }

                    for (const c of vaultData.contracts) {
                        try {
                            let payload;
                            // Náš zachránce: Fallback pro nové/dočasně kódované smlouvy z HR Velínu
                            if (c.iv === 'IV_PENDING' || c.wrapped_key === 'WRAPPED_KEY_PENDING') {
                                const decoded = window.atob(c.encrypted_payload);
                                payload = JSON.parse(decodeURIComponent(escape(decoded)));
                            } else {
                                if (!rsaPriv) throw new Error("Chybí firemní RSA klíč pro rozšifrování payloadu.");
                                const aesRaw = await crypto.subtle.decrypt({name: "RSA-OAEP"}, rsaPriv, b64ToBuf(c.wrapped_key));
                                const aesKey = await crypto.subtle.importKey("raw", aesRaw, {name: "AES-GCM", length: 256}, true, ["decrypt"]);
                                const payloadDec = await crypto.subtle.decrypt({name: "AES-GCM", iv: b64ToBuf(c.iv)}, aesKey, b64ToBuf(c.encrypted_payload));
                                const payloadBase64 = new TextDecoder().decode(payloadDec);
                                payload = JSON.parse(decodeURIComponent(escape(window.atob(payloadBase64))));
                            }
                            
                            html += '<div class="contract">';
                            html += '<h3>ID Smlouvy: ' + c.id + ' <span style="font-size: 0.6em; color: #64748b;">(Status: ' + c.status.toUpperCase() + ')</span></h3>';
                            html += '<p><strong>DID Zaměstnance:</strong> ' + c.subject_did + '</p>';
                            html += '<p><strong>Hash (Důkaz):</strong> ' + c.content_hash + '</p>';
                            html += '<div style="background: #0f172a; padding: 15px; border-radius: 8px; margin: 15px 0;">';
                            if(payload.firstName) html += 'Jméno: ' + payload.firstName + ' ' + (payload.lastName || '') + '<br>';
                            if(payload.position) html += 'Pozice: ' + payload.position + '<br>';
                            if(payload.salary) html += 'Odměna: ' + payload.salary + ' CZK<br>';
                            if(payload.startDate) html += 'Nástup: ' + payload.startDate + '<br>';
                            if(payload.validUntil) html += 'Konec platnosti: ' + payload.validUntil + '<br>';
                            html += '</div>';
                            
                            if (payload.fileData) html += '<a class="download-btn" href="' + payload.fileData + '" download="' + (payload.fileName || 'smlouva.pdf') + '">📄 Stáhnout fyzický soubor</a>';
                            else if (payload.url) html += '<a class="download-btn" href="' + payload.url + '" target="_blank">🔗 Otevřít na cloudu</a>';
                            html += '</div>';
                        } catch (err) {
                            html += '<div class="contract"><p class="error" style="background: transparent; color: #ef4444; border: 1px solid #ef4444;">Chyba dešifrování u záznamu ' + c.id + ':<br>' + err.message + '</p></div>';
                        }
                    }
                    document.getElementById('content').innerHTML = html;
                    status.innerHTML = '';
                    document.getElementById('seed').style.display = 'none';
                    btn.style.display = 'none';
                } catch (e) {
                    console.error(e);
                    status.innerHTML = '<div class="error"><strong>Kritická chyba:</strong> ' + e.message + '</div>';
                    btn.disabled = false;
                }
            }, 100);
        }
    </script>
</body>
</html>`;\n"""
        
        with open(file_path, "w") as f:
            f.write(content[:start_idx] + new_template + content[end_idx:])
        print("[+] Kapsle byla prepsana na neprustrelnou a odolnou verzi.")
