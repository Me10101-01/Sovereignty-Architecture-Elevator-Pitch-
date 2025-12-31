// IO Unit - Bridge to proxy port for localhost simulation
use std::net::TcpListener;

pub fn bind_proxy_port(ip: &str, port: u16) -> Result<TcpListener, std::io::Error> {
    let addr = format!("{}:{}", ip, port);
    TcpListener::bind(&addr)
}

pub fn simulate_connection(uri: &str) -> String {
    format!("Simulated connection to {}", uri)
}
