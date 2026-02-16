// Domain mapper for music to recon waves
pub fn map_music_to_recon(piece_id: u8, hz: f64) -> String {
    format!("Mapping piece {} ({}Hz) to recon domain", piece_id, hz)
}
