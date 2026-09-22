import { API_BASE_URL } from './config';

/**
 * Inicializuje MojeID / BankID step-up autorizaci pro citlivou akci
 * @param {string} tenantId 
 * @param {string} actionType - např. 'CONTRACT_SIGN', 'TERMINATION', 'ADDENDUM'
 * @param {string} documentHash - kryptografický hash dokumentu
 */
export async function initiateMojeIdChallenge(tenantId, actionType, documentHash) {
  const response = await fetch(`${API_BASE_URL}/auth/mojeid/challenge`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      tenant_id: tenantId,
      action_type: actionType,
      document_hash: documentHash,
    }),
  });

  if (!response.ok) {
    throw new Error('Nepodařilo se inicializovat autorizaci přes MojeID.');
  }

  const data = await response.json();
  // data.redirect_url obsahuje adresu pro přesměrování na MojeID bránu
  return data;
}

/**
 * Inicializuje proces obnovy přístupu (Identity Recovery) při ztrátě zařízení
 */
export async function initiateIdentityRecovery() {
  const response = await fetch(`${API_BASE_URL}/auth/recovery/init`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Nepodařilo se zahájit proces obnovy identity.');
  }

  return await response.json();
}
