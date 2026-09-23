pub mod zk;

pub use zk::circuit::{CredentialCircuit, verify_credential_proof};
pub use zk::tsa_anchor::{TsaAnchorProof, validate_eidas_tsa_link};

pub fn version() -> &'static str {
    "inloopid-core-zk-0.1.0"
}
