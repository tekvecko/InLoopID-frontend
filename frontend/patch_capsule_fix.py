import os

file_path = "/data/data/com.termux/files/home/InloopID/frontend/src/components/HRDashboard.jsx"

with open(file_path, "r") as f:
    content = f.read()

start_idx = content.find("async function unlockVault() {")
end_idx = content.find("</script>", start_idx)

if start_idx != -1 and end_idx != -1:
    new_code = r"""async function unlockVault() {
            const words = document.getElementById('seed').value.trim().toLowerCase().replace(/\s+/g, ' ');
            const status = document.getElementById('status');
            const btn = document.getElementById('btn');
            
            if(!words) return;
            btn.disabled = true;
            status.innerHTML = '<span class="success">Odemykám... Provádím PBKDF2 výpočet s 1 000 000 iteracemi (ochrana proti kvantovému útoku). To může chvíli trvat...</span>';
            
            setTimeout(async () => {
                try {
                    const vaultKey = await deriveAESKey(words, "INLOOP_COLD_VAULT_SALT", 1000000);
                    const decrypted = await crypto.subtle.decrypt({name: "AES-GCM", iv: b64ToBuf(IV)}, vaultKey, b64ToBuf(CIPHERTEXT));
                    const vaultData = JSON.parse(new TextDecoder().decode(decrypted));
                    
                    status.innerHTML = '<span class="success">Kapsle odemčena. Rekonstruuji asymetrické vazby z databáze...</span>';
                    
                    const hrKey = await deriveAESKey(vaultData.masterKey, "HR_SALT", 100000);
                    const rsaDec = await crypto.subtle.decrypt({name: "AES-GCM", iv: b64ToBuf(vaultData.private_key_iv)}, hrKey, b64ToBuf(vaultData.encrypted_private_key));
                    const rsaJwk = JSON.parse(new TextDecoder().decode(rsaDec));
                    
                    // OPRAVA 1: Povolujeme pouze "decrypt", jelikož JWK klíč nemá atribut "unwrapKey"
                    const rsaPriv = await crypto.subtle.importKey("jwk", rsaJwk, {name: "RSA-OAEP", hash: "SHA-256"}, true, ["decrypt"]);
                    
                    let html = '<h2 style="margin-top: 40px; border-bottom: 1px solid #1e293b; padding-bottom: 10px;">Archiv smluv (' + vaultData.contracts.length + ')</h2>';
                    
                    for (const c of vaultData.contracts) {
                        try {
                            let payload;
                            // OPRAVA 2: Fallback dekódování pro smlouvy z HRDashboard
                            if (c.iv === 'IV_PENDING' || c.wrapped_key === 'WRAPPED_KEY_PENDING') {
                                const decoded = window.atob(c.encrypted_payload);
                                payload = JSON.parse(decodeURIComponent(escape(decoded)));
                            } else {
                                const aesRaw = await crypto.subtle.decrypt({name: "RSA-OAEP"}, rsaPriv, b64ToBuf(c.wrapped_key));
                                const aesKey = await crypto.subtle.importKey("raw", aesRaw, {name: "AES-GCM", length: 256}, true, ["decrypt"]);
                                const payloadDec = await crypto.subtle.decrypt({name: "AES-GCM", iv: b64ToBuf(c.iv)}, aesKey, b64ToBuf(c.encrypted_payload));
                                const payloadBase64 = new TextDecoder().decode(payloadDec);
                                payload = JSON.parse(decodeURIComponent(escape(window.atob(payloadBase64))));
                            }
                            
                            html += '<div class="contract">';
                            html += '<h3>ID Smlouvy: ' + c.id + ' <span style="font-size: 0.6em; color: #64748b;">(Status: ' + c.status.toUpperCase() + ')</span></h3>';
                            html += '<p><strong>DID Zaměstnance:</strong> ' + c.subject_did + '</p>';
                            html += '<p><strong>Hash (Důkaz z blockchainu):</strong> ' + c.content_hash + '</p>';
                            html += '<div style="background: #0f172a; padding: 15px; border-radius: 8px; margin: 15px 0;">';
                            if(payload.firstName) html += 'Jméno: ' + payload.firstName + ' ' + (payload.lastName || '') + '<br>';
                            if(payload.position) html += 'Pozice: ' + payload.position + '<br>';
                            if(payload.salary) html += 'Odměna: ' + payload.salary + ' CZK<br>';
                            if(payload.startDate) html += 'Nástup: ' + payload.startDate + '<br>';
                            if(payload.validUntil) html += 'Konec platnosti: ' + payload.validUntil + '<br>';
                            html += '</div>';
                            
                            if (payload.fileData) html += '<a class="download-btn" href="' + payload.fileData + '" download="' + (payload.fileName || 'smlouva.pdf') + '">📄 Stáhnout původní fyzický soubor</a>';
                            else if (payload.url) html += '<a class="download-btn" href="' + payload.url + '" target="_blank">🔗 Otevřít na cloudu</a>';
                            html += '</div>';
                        } catch (err) {
                            html += '<div class="contract"><p class="error">Kryptografická chyba: Záznam ' + c.id + ' nelze dešifrovat.</p></div>';
                        }
                    }
                    document.getElementById('content').innerHTML = html;
                    status.innerHTML = '';
                    document.getElementById('seed').style.display = 'none';
                    btn.style.display = 'none';
                } catch (e) {
                    console.error(e);
                    status.innerHTML = '<div class="error">Kritická chyba: Nesprávný Master Seed nebo porušená integrita kapsle! Zkontrolujte zadání slov.</div>';
                    btn.disabled = false;
                }
            }, 100);
        }
"""
    new_content = content[:start_idx] + new_code + "\n    " + content[end_idx:]
    with open(file_path, "w") as f:
        f.write(new_content)
    print("[+] Kapsle byla úspěšně opravena.")
else:
    print("[-] Selhalo vyhledání funkce v souboru.")
