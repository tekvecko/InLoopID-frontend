export const generateRSAKeyPair = async () => {
  return await window.crypto.subtle.generateKey(
    { name: "RSA-OAEP", modulusLength: 2048, publicExponent: new Uint8Array([1, 0, 1]), hash: "SHA-256" },
    true, ["encrypt", "decrypt"]
  );
};

export const generateSigningKeyPair = async () => {
  return await window.crypto.subtle.generateKey(
    { name: "ECDSA", namedCurve: "P-256" },
    true, ["sign", "verify"]
  );
};

export const exportPublicKeyJWK = async (publicKey) => {
  return await window.crypto.subtle.exportKey("jwk", publicKey);
};

export const exportPrivateKeyJWK = async (privateKey) => {
  return await window.crypto.subtle.exportKey("jwk", privateKey);
};

export const importPrivateKeyJWK = async (jwk, type) => {
  if (type === 'RSA') {
    return await window.crypto.subtle.importKey("jwk", jwk, { name: "RSA-OAEP", hash: "SHA-256" }, true, ["decrypt"]);
  } else {
    return await window.crypto.subtle.importKey("jwk", jwk, { name: "ECDSA", namedCurve: "P-256" }, true, ["sign"]);
  }
};

export const importPublicKeyJWK = async (jwkStr) => {
  const jwk = typeof jwkStr === 'string' ? JSON.parse(jwkStr) : jwkStr;
  return await window.crypto.subtle.importKey(
    "jwk",
    jwk,
    { name: "RSA-OAEP", hash: "SHA-256" },
    true,
    ["encrypt"]
  );
};

export const generateAESKey = async () => {
  return await window.crypto.subtle.generateKey({ name: "AES-GCM", length: 256 }, true, ["encrypt", "decrypt"]);
};

export const hashDocument = async (arrayBuffer) => {
  const hashBuffer = await window.crypto.subtle.digest('SHA-256', arrayBuffer);
  return Array.from(new Uint8Array(hashBuffer)).map(b => b.toString(16).padStart(2, '0')).join('');
};

export const hashEmail = async (email) => {
  const buffer = await window.crypto.subtle.digest('SHA-256', new TextEncoder().encode(email.toLowerCase().trim()));
  return Array.from(new Uint8Array(buffer)).map(b => b.toString(16).padStart(2, '0')).join('');
};

export const encryptDocument = async (arrayBuffer, aesKey) => {
  const iv = window.crypto.getRandomValues(new Uint8Array(12));
  const encryptedBuffer = await window.crypto.subtle.encrypt({ name: "AES-GCM", iv }, aesKey, arrayBuffer);
  return { iv, encryptedBuffer };
};

export const decryptDocument = async (encryptedBuffer, aesKey, ivBuffer) => {
    return await window.crypto.subtle.decrypt({ name: "AES-GCM", iv: ivBuffer }, aesKey, encryptedBuffer);
};

export const wrapKey = async (aesKey, rsaPublicKey) => {
  const rawKey = await window.crypto.subtle.exportKey("raw", aesKey);
  return await window.crypto.subtle.encrypt({ name: "RSA-OAEP" }, rsaPublicKey, rawKey);
};

export const unwrapKey = async (wrappedKeyBuffer, privateKey) => {
    return await window.crypto.subtle.unwrapKey(
        "raw", wrappedKeyBuffer, privateKey,
        { name: "RSA-OAEP" }, { name: "AES-GCM", length: 256 },
        true, ["encrypt", "decrypt"]
    );
};

export const signData = async (privateSigningKey, dataString) => {
  const encoder = new TextEncoder();
  const signatureBuffer = await window.crypto.subtle.sign(
    { name: "ECDSA", hash: { name: "SHA-256" } },
    privateSigningKey,
    encoder.encode(dataString)
  );
  return bufferToBase64(signatureBuffer);
};

export const bufferToBase64 = (buffer) => {
  const bytes = new Uint8Array(buffer);
  let binary = '';
  for (let i = 0; i < bytes.byteLength; i++) binary += String.fromCharCode(bytes[i]);
  return window.btoa(binary);
};

export const base64ToBuffer = (base64) => {
  const binary_string = window.atob(base64);
  const len = binary_string.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binary_string.charCodeAt(i);
  }
  return bytes.buffer;
};

const deriveKeyFromPassword = async (password, salt) => {
  const enc = new TextEncoder();
  const keyMaterial = await window.crypto.subtle.importKey("raw", enc.encode(password), { name: "PBKDF2" }, false, ["deriveBits", "deriveKey"]);
  return window.crypto.subtle.deriveKey(
    { name: "PBKDF2", salt: enc.encode(salt), iterations: 100000, hash: "SHA-256" },
    keyMaterial, { name: "AES-GCM", length: 256 }, true, ["encrypt", "decrypt"]
  );
};

export const encryptKeystore = async (payloadObj, password, emailHash) => {
  const aesKey = await deriveKeyFromPassword(password, emailHash);
  const iv = window.crypto.getRandomValues(new Uint8Array(12));
  const encrypted = await window.crypto.subtle.encrypt({ name: "AES-GCM", iv }, aesKey, new TextEncoder().encode(JSON.stringify(payloadObj)));
  return { iv: bufferToBase64(iv), encryptedBlob: bufferToBase64(encrypted) };
};

export const decryptKeystore = async (encryptedBlobBase64, ivBase64, password, emailHash) => {
  const aesKey = await deriveKeyFromPassword(password, emailHash);
  const encryptedBuffer = base64ToBuffer(encryptedBlobBase64);
  const ivBuffer = base64ToBuffer(ivBase64);
  const decrypted = await window.crypto.subtle.decrypt({ name: "AES-GCM", iv: ivBuffer }, aesKey, encryptedBuffer);
  return JSON.parse(new TextDecoder().decode(decrypted));
};
