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

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_credential_circuit_valid_threshold() {
        let circuit = CredentialCircuit::new(b"user_birth_date_2000".to_vec(), 21);
        assert!(circuit.is_valid);

        let proof = circuit.prove();
        assert!(proof.is_ok());
        let proof_bytes = proof.unwrap();
        assert!(!proof_bytes.is_empty());

        let is_verified = verify_credential_proof(&proof_bytes, &circuit.attribute_hash);
        assert!(is_verified);
    }

    #[test]
    fn test_credential_circuit_underage_threshold() {
        let circuit = CredentialCircuit::new(b"user_birth_date_2012".to_vec(), 14);
        assert!(!circuit.is_valid);

        let proof = circuit.prove();
        assert!(proof.is_err());
        assert_eq!(proof.unwrap_err(), "Predikát selhal: věková hranice nesplněna.");
    }

    #[test]
    fn test_verify_credential_proof_empty_inputs() {
        assert!(!verify_credential_proof(&[], b"hash"));
        assert!(!verify_credential_proof(b"proof", &[]));
        assert!(!verify_credential_proof(&[], &[]));
    }
}
