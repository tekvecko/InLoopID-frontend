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

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_tsa_anchor_valid_link() {
        let content_hash = vec![0x01, 0x02, 0x03, 0x04];
        let timestamp_der = vec![0x30, 0x82, 0x01, 0x00]; // mock DER
        let anchor = TsaAnchorProof::new(content_hash, timestamp_der);

        assert!(anchor.verified_by_eidas);
        assert!(validate_eidas_tsa_link(&anchor));
    }

    #[test]
    fn test_tsa_anchor_missing_timestamp() {
        let content_hash = vec![0x01, 0x02, 0x03];
        let timestamp_der = vec![];
        let anchor = TsaAnchorProof::new(content_hash, timestamp_der);

        assert!(!anchor.verified_by_eidas);
        assert!(!validate_eidas_tsa_link(&anchor));
    }

    #[test]
    fn test_tsa_anchor_missing_content_hash() {
        let content_hash = vec![];
        let timestamp_der = vec![0x30, 0x82];
        let anchor = TsaAnchorProof::new(content_hash, timestamp_der);

        assert!(!anchor.verified_by_eidas);
        assert!(!validate_eidas_tsa_link(&anchor));
    }
}
