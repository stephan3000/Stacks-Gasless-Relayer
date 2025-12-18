
use actix_web::{web, HttpResponse};
use crate::models::DefaultAppState;
use serde::Deserialize;

#[derive(Deserialize)]
pub struct StacksRelayRequest {
    pub tx_hex: String,
}

pub async fn relay_stacks_tx(
    data: web::ThinData<DefaultAppState>,
    req: web::Json<StacksRelayRequest>,
) -> HttpResponse {
    match data.stacks_relayer.broadcast_transaction(&req.tx_hex).await {
        Ok(tx_id) => HttpResponse::Ok().json(serde_json::json!({ "status": "success", "tx_id": tx_id })),
        Err(e) => {
            let error_msg = e.to_string();
            tracing::error!("Failed to relay Stacks transaction: {}", error_msg);
            
            if error_msg.contains("Stacks Node Error") || error_msg.contains("hex") {
                 HttpResponse::BadRequest().json(serde_json::json!({ "status": "error", "message": error_msg }))
            } else {
                 HttpResponse::InternalServerError().json(serde_json::json!({ "status": "error", "message": error_msg }))
            }
        }
    }
}

pub fn init(cfg: &mut web::ServiceConfig) {
    cfg.service(
        web::resource("/stacks/relay")
            .route(web::post().to(relay_stacks_tx))
    );
}
