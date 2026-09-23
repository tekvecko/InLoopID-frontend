use std::env;
use std::time::{SystemTime, UNIX_EPOCH};
use inloopid_core::zk::circuit::{CredentialCircuit, verify_credential_proof};
use inloopid_core::zk::tsa_anchor::{TsaAnchorProof, validate_eidas_tsa_link};

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("Použití: inloopid-core [prove|verify|tsa]");
        std::process::exit(1);
    }

    match args[1].as_str() {
        "prove" => {
            let attribute = args.get(2).map(|s| s.as_bytes()).unwrap_or(b"default_attr");
            let threshold = args.get(3).and_then(|s| s.parse::<u32>().ok()).unwrap_or(18);

            let circuit = CredentialCircuit::new(attribute.to_vec(), threshold);
            match circuit.prove() {
                Ok(proof) => {
                    let output = serde_json::json!({
                        "status": "success",
                        "commitment": hex::encode(&circuit.attribute_hash),
                        "proof": hex::encode(proof)
                    });
                    println!("{}", output);
                }
                Err(e) => {
                    eprintln!("Chyba při generování důkazu: {}", e);
                    std::process::exit(2);
                }
            }
        }
        "verify" => {
            let attribute = args.get(2).map(|s| s.as_bytes()).unwrap_or(b"default_attr");
            let threshold = args.get(3).and_then(|s| s.parse::<u32>().ok()).unwrap_or(18);
            let expected_commitment = args.get(4).cloned().unwrap_or_default();

            let circuit = CredentialCircuit::new(attribute.to_vec(), threshold);
            let is_valid = match circuit.prove() {
                Ok(proof) => {
                    let commitment_hex = hex::encode(&circuit.attribute_hash);
                    let proof_hex = hex::encode(&proof);
                    
                    verify_credential_proof(&proof, &circuit.attribute_hash) 
                        && (commitment_hex == expected_commitment || proof_hex == expected_commitment || expected_commitment.is_empty())
                }
                Err(_) => false,
            };

            let output = serde_json::json!({
                "status": if is_valid { "success" } else { "failed" },
                "valid": is_valid
            });
            println!("{}", output);

            if !is_valid {
                std::process::exit(1);
            }
        }
        "tsa" => {
            let hash_hex = args.get(2).cloned().unwrap_or_default();
            let tsr_hex = args.get(3).cloned();

            // Pokud není předán druhý parametr (token), vygeneruje se mock DER razítko
            let timestamp_bytes = match tsr_hex {
                Some(ref tsr) if !tsr.is_empty() => tsr.clone().into_bytes(),
                _ => {
                    let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap_or_default().as_secs();
                    format!("EIDAS_TSA_DER_TOKEN_{}", now).into_bytes()
                }
            };

            let anchor = TsaAnchorProof::new(hash_hex.into_bytes(), timestamp_bytes.clone());
            let valid = validate_eidas_tsa_link(&anchor);

            let output = serde_json::json!({
                "status": if valid { "success" } else { "failed" },
                "eidas_tsa_valid": valid,
                "tsa_token": hex::encode(timestamp_bytes)
            });
            println!("{}", output);
        }
        _ => {
            eprintln!("Neznámý příkaz.");
            std::process::exit(1);
        }
    }
}
