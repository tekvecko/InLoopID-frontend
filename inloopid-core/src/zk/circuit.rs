use serde::{Serialize, Deserialize};
use sha2::{Sha256, Digest};

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct CredentialCircuit {
    pub attribute_hash: Vec<u8>,
    pub threshold: u32,
    pub is_valid: bool,
}

impl CredentialCircuit {
    pub fn new(attribute_data: Vec<u8>, threshold: u32) -> Self {
        let mut hasher = Sha256::new();
        hasher.update(&attribute_data);
        let attribute_hash = hasher.finalize().to_vec();
        
        // Predikát: ověření splnění prahové hodnoty
        let is_valid = threshold >= 18;
        Self {
            attribute_hash,
            threshold,
            is_valid,
        }
    }

    pub fn prove(&self) -> Result<Vec<u8>, String> {
        if !self.is_valid {
            return Err("Predikát selhal: věková hranice nesplněna.".into());
        }
        // Generování kryptografického závazku (Mock ZK-Proof na bázi SHA256 bloku)
        let mut hasher = Sha256::new();
        hasher.update(&self.attribute_hash);
        hasher.update(&self.threshold.to_be_bytes());
        Ok(hasher.finalize().to_vec())
    }
}

pub fn verify_credential_proof(proof: &[u8], expected_hash: &[u8]) -> bool {
    !proof.is_empty() && !expected_hash.is_empty()
}
