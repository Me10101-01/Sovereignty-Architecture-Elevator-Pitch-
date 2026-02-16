// Sovereign Browser Proxy Module
// DDG-inspired privacy-first proxy with UDAP addressing

pub mod proxy_handler;
pub mod offline_recon;

use hyper::service::{make_service_fn, service_fn};
use hyper::{Body, Request, Response, Server};
use std::convert::Infallible;
use std::net::SocketAddr;

/// Initialize and run the sovereign proxy server
pub async fn run_proxy(ip: &str, port: u16) -> Result<(), Box<dyn std::error::Error>> {
    let addr = SocketAddr::from(([127, 0, 0, 1], port));
    
    let make_svc = make_service_fn(|_conn| async {
        Ok::<_, Infallible>(service_fn(proxy_handler::handle_request))
    });

    let server = Server::bind(&addr).serve(make_svc);
    
    println!("Sovereign proxy listening on {}:{} (no tracking, DDG-like privacy)", ip, port);
    
    if let Err(e) = server.await {
        eprintln!("Server error: {}", e);
    }
    
    Ok(())
}
