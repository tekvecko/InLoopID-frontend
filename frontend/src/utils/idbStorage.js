import { openDB } from 'idb';

const DB_NAME = 'InloopID_Wallet_V3'; 
const STORE_NAME = 'identities';
const CREDENTIALS_STORE = 'verified_credentials';

export const initDB = async () => {
  return openDB(DB_NAME, 1, {
    upgrade(db) {
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: 'did' });
      }
      if (!db.objectStoreNames.contains(CREDENTIALS_STORE)) {
        db.createObjectStore(CREDENTIALS_STORE, { keyPath: 'id' });
      }
    },
  });
};

export const saveIdentity = async (did, encKeyPair, signKeyPair, jwk, eidasCredential = null) => {
  const db = await initDB();
  await db.put(STORE_NAME, {
    did,
    encPrivateKey: encKeyPair.privateKey,
    encPublicKey: encKeyPair.publicKey,
    signPrivateKey: signKeyPair.privateKey,
    signPublicKey: signKeyPair.publicKey,
    jwk: JSON.stringify(jwk),
    createdAt: new Date().toISOString()
  });
  
  if (eidasCredential) {
    await db.put(CREDENTIALS_STORE, {
        id: 'primary_eidas',
        did: did,
        data: eidasCredential
    });
  }
};

export const getIdentity = async (did) => {
  const db = await initDB();
  return await db.get(STORE_NAME, did);
};

export const getAllIdentities = async () => {
  const db = await initDB();
  return await db.getAll(STORE_NAME);
};

export const getEidasCredential = async () => {
  const db = await initDB();
  return await db.get(CREDENTIALS_STORE, 'primary_eidas');
};
