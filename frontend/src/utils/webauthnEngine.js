// frontend/src/utils/webauthnEngine.js

/**
 * Převede Base64Url řetězec na ArrayBuffer
 */
function bufferDecode(value) {
  const base64 = value.replace(/-/g, '+').replace(/_/g, '/');
  const padLen = (4 - (base64.length % 4)) % 4;
  const padded = base64.padEnd(base64.length + padLen, '=');
  const binary = atob(padded);
  const buffer = new ArrayBuffer(binary.length);
  const bytes = new Uint8Array(buffer);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return buffer;
}

/**
 * Převede ArrayBuffer na Base64Url řetězec
 */
function bufferEncode(buffer) {
  const bytes = new Uint8Array(buffer);
  let binary = '';
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary)
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=/g, '');
}

/**
 * Registrace nového Passkey klíče na zařízení
 */
export async function registerPasskey(userIdentifier, userName) {
  if (!window.PublicKeyCredential) {
    throw new Error("WebAuthn API není v tomto prohlížeči podporováno.");
  }

  const challenge = crypto.getRandomValues(new Uint8Array(32));
  const userIdBytes = new TextEncoder().encode(userIdentifier);

  const publicKeyCredentialCreationOptions = {
    challenge: challenge,
    rp: {
      name: "InLoopID Trust Layer",
      id: window.location.hostname,
    },
    user: {
      id: userIdBytes,
      name: userName,
      displayName: userName,
    },
    pubKeyCredParams: [
      { alg: -7, type: "public-key" },  // ES256
      { alg: -257, type: "public-key" } // RS256
    ],
    timeout: 60000,
    attestation: "direct",
    authenticatorSelection: {
      authenticatorAttachment: "platform",
      userVerification: "required",
      residentKey: "preferred"
    }
  };

  try {
    const credential = await navigator.credentials.create({
      publicKey: publicKeyCredentialCreationOptions
    });

    return {
      id: credential.id,
      rawId: bufferEncode(credential.rawId),
      type: credential.type,
      response: {
        clientDataJSON: bufferEncode(credential.response.clientDataJSON),
        attestationObject: bufferEncode(credential.response.attestationObject)
      }
    };
  } catch (error) {
    console.error("Chyba při registraci Passkey:", error);
    throw error;
  }
}

/**
 * Ověření (Login / Podpis) pomocí existujícího Passkey
 */
export async function authenticatePasskey(allowedCredentialId = null) {
  if (!window.PublicKeyCredential) {
    throw new Error("WebAuthn API není v tomto prohlížeči podporováno.");
  }

  const challenge = crypto.getRandomValues(new Uint8Array(32));

  const publicKeyCredentialRequestOptions = {
    challenge: challenge,
    timeout: 60000,
    userVerification: "required",
    rpId: window.location.hostname,
  };

  if (allowedCredentialId) {
    publicKeyCredentialRequestOptions.allowCredentials = [{
      id: bufferDecode(allowedCredentialId),
      type: "public-key",
      transports: ["internal", "usb", "nfc", "ble"]
    }];
  }

  try {
    const assertion = await navigator.credentials.get({
      publicKey: publicKeyCredentialRequestOptions
    });

    return {
      id: assertion.id,
      rawId: bufferEncode(assertion.rawId),
      type: assertion.type,
      response: {
        clientDataJSON: bufferEncode(assertion.response.clientDataJSON),
        authenticatorData: bufferEncode(assertion.response.authenticatorData),
        signature: bufferEncode(assertion.response.signature),
        userHandle: assertion.response.userHandle ? bufferEncode(assertion.response.userHandle) : null
      }
    };
  } catch (error) {
    console.error("Chyba při autentizaci Passkey:", error);
    throw error;
  }
}
