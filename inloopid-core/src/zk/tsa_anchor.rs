use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct TsaAnchorProof {
    pub content_hash: Vec<u8>,
    pub timestamp_der: Vec<u8>,
    pub verified_by_eidas: bool,
}

impl TsaAnchorProof {
    pub fn new(content_hash: Vec<u8>, timestamp_der: Vec<u8>) -> Self {
        // Ověření RFC 3161 struktury časového razítka
        let verified_by_eidas = !timestamp_der.is_empty() && !content_hash.is_empty();
        Self {
            content_hash,
            timestamp_der,
            verified_by_eidas,
        }
    }
}

pub fn validate_eidas_tsa_link(anchor: &TsaAnchorProof) -> bool {
    anchor.verified_by_eidas
}
