

use color_eyre::Result;
use tracing::{info, error};
use reqwest::Client;
use serde::Deserialize;

#[derive(Clone, Debug)]
pub struct StacksRelayer {
    pub node_url: String,
    pub client: Client,
}

#[derive(Deserialize)]
struct StacksTxResponse {
    #[allow(dead_code)] 
    txid: String,
}

impl StacksRelayer {
    pub fn new(node_url: String) -> Self {
        Self { 
            node_url,
            client: Client::new()
        }
    }

    pub async fn broadcast_transaction(&self, tx_hex: &str) -> Result<String> {
        info!("Broadcasting Stacks transaction to {}", self.node_url);
        
        // Remove 0x prefix if present
        let clean_hex = tx_hex.trim_start_matches("0x");
        let tx_bytes = hex::decode(clean_hex)?;
        
        let url = format!("{}/v2/transactions", self.node_url);
        
        let res = self.client.post(&url)
            .header("Content-Type", "application/octet-stream")
            .body(tx_bytes)
            .send()
            .await?;
            
        if !res.status().is_success() {
            let error_text = res.text().await.unwrap_or_else(|_| "Unknown error".to_string());
            error!("Stacks Node Error: {}", error_text);
            return Err(color_eyre::eyre::eyre!("Stacks Node Error: {}", error_text));
        }
        
        // Response string is typically just the quoted TXID string like "0x..."
        let tx_id = res.text().await?.trim_matches('"').to_string();
        info!("Transaction broadcasted successfully. ID: {}", tx_id);
        
        Ok(tx_id)
    }
    
    pub async fn validate_transaction(&self, _tx_hex: &str) -> Result<bool> {
        // Validation logic would require parsing the Stacks transaction format
        // which is complex without stacks-rs. Keeping as mock for now or until stacks-rs is fixed.
        Ok(true)
    }
}
