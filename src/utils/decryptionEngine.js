import { getIdentity } from './idbStorage';

const base64ToBuffer = (base64) => {
  const binary_string = window.atob(base64);
  const len = binary_string.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binary_string.charCodeAt(i);
  }
  return bytes.buffer;
};

// Funkce simulující parsování PDF dat z bufferu
const parseDecryptedPDF = async (arrayBuffer) => {
    // V této MVP fázi vrátíme Blob URL, kterou lze otevřít v prohlížeči
    const blob = new Blob([arrayBuffer], { type: 'application/pdf' });
    return URL.createObjectURL(blob);
};

export const decryptAndVerifyCredential = async (credential) => {
  try {
    // 1. Zajištění asymetrického klíče klienta z bezpečné zóny (IndexedDB)
    const identity = await getIdentity(credential.subject_did);
    if (!identity) throw new Error("Chybí privátní klíč (DID) pro tuto smlouvu.");

    // 2. Extrakce a dekódování Base64 payloadů
    const encryptedPayloadBuffer = base64ToBuffer(credential.encrypted_payload);
    const ivBuffer = base64ToBuffer(credential.iv);
    const wrappedKeyBuffer = base64ToBuffer(credential.wrapped_key);

    // 3. Rozbalení symetrického klíče pomocí RSA-OAEP (vyžaduje privátní klíč!)
    const aesRawKey = await window.crypto.subtle.decrypt(
      { name: "RSA-OAEP" },
      identity.encPrivateKey,
      wrappedKeyBuffer
    );

    // Znovuvytvoření objektu CryptoKey pro AES-GCM
    const aesKey = await window.crypto.subtle.importKey(
      "raw",
      aesRawKey,
      { name: "AES-GCM", length: 256 },
      true,
      ["decrypt"]
    );

    // 4. AEAD DEŠIFROVÁNÍ (Základní kámen neprůstřelnosti)
    // Pokud hacker upravil payload v tranzitu, AES-GCM Auth Tag nesedne a tato funkce okamžitě spadne.
    const decryptedBuffer = await window.crypto.subtle.decrypt(
      { name: "AES-GCM", iv: ivBuffer },
      aesKey,
      encryptedPayloadBuffer
    );

    // 5. Znovuvytvoření hashe a porovnání s nezměnitelným originálem (Double check)
    const hashBuffer = await window.crypto.subtle.digest('SHA-256', decryptedBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const calculatedHash = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');

    if (calculatedHash !== credential.content_hash) {
      throw new Error("KRYPTOGRAFICKÝ POPLACH: Integrita dokumentu byla narušena!");
    }

    // 6. Vrácení bezpečného URL pro zobrazení PDF
    const pdfUrl = await parseDecryptedPDF(decryptedBuffer);
    return { success: true, url: pdfUrl, hash: calculatedHash };

  } catch (error) {
    console.error("Bezpečnostní selhání:", error);
    return { success: false, error: error.message };
  }
};
