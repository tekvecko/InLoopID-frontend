// Nativní integrace FIDO2 / Passkeys (WebAuthn)
// Zcela nahrazuje závislost na Termux:API

export const promptBiometrics = async () => {
  // 1. Zkontrolujeme, zda zařízení a prohlížeč podporují hardwarovou biometrii
  if (!window.PublicKeyCredential) {
    return window.confirm("Váš prohlížeč nepodporuje hardwarovou biometrii. Potvrzujete tuto akci?");
  }

  try {
    // Zjistíme, zda už jsme si na tomto zařízení Passkey vytvořili
    const credentialIdBase64 = localStorage.getItem('inloopid_passkey');

    // Generujeme kryptografickou výzvu
    const challenge = new Uint8Array(32);
    window.crypto.getRandomValues(challenge);

    if (!credentialIdBase64) {
        // SCÉNÁŘ A: První spuštění (Vytváření Trezoru)
        // Prohlížeč vyvolá nativní dialog Androidu pro vytvoření Passkey
        const cred = await navigator.credentials.create({
            publicKey: {
                challenge: challenge,
                rp: { name: "InLoopID Trezor" },
                user: { 
                    id: new Uint8Array(16), 
                    name: "zamestnanec@inloopid", 
                    displayName: "Můj Bezpečný Trezor" 
                },
                pubKeyCredParams: [
                    { type: "public-key", alg: -7 }, // ES256
                    { type: "public-key", alg: -257 } // RS256
                ],
                authenticatorSelection: { 
                    authenticatorAttachment: "platform", // Vynutí biometrii přímo na telefonu
                    userVerification: "required" 
                },
                timeout: 60000
            }
        });
        
        // Uložíme ID vygenerovaného otisku do paměti pro budoucí podepisování
        const rawId = new Uint8Array(cred.rawId);
        localStorage.setItem('inloopid_passkey', btoa(String.fromCharCode.apply(null, rawId)));
        return true;
        
    } else {
        // SCÉNÁŘ B: Další spuštění (Podepisování smlouvy, Odemčení)
        // Prohlížeč vyvolá nativní dialog pro ověření existujícího Passkey
        const binaryString = window.atob(credentialIdBase64);
        const credentialId = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
            credentialId[i] = binaryString.charCodeAt(i);
        }

        await navigator.credentials.get({
            publicKey: {
                challenge: challenge,
                allowCredentials: [{ type: "public-key", id: credentialId }],
                userVerification: "required",
                timeout: 60000
            }
        });
        return true;
    }
  } catch (err) {
    console.warn("Biometrické ověření bylo zrušeno nebo selhalo:", err);
    return false;
  }
};
