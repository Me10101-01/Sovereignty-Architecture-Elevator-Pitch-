// 36 Classical Pieces with Hz mappings and mood entanglement
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ClassicalPiece {
    pub id: u8,
    pub name: String,
    pub composer: String,
    pub key_note: String,
    pub fundamental_hz: f64,
    pub mood_band: String, // delta, theta, alpha, beta, gamma
    pub midi_file: String,
}

pub const CLASSICAL_PIECES: [ClassicalPiece; 36] = [
    ClassicalPiece { id: 1, name: "Symphony No.5".to_string(), composer: "Beethoven".to_string(), key_note: "C".to_string(), fundamental_hz: 261.0, mood_band: "beta".to_string(), midi_file: "assets/classical/beethoven_sym5.mid".to_string() },
    ClassicalPiece { id: 2, name: "Symphony No.9".to_string(), composer: "Beethoven".to_string(), key_note: "D".to_string(), fundamental_hz: 294.0, mood_band: "gamma".to_string(), midi_file: "assets/classical/beethoven_sym9.mid".to_string() },
    ClassicalPiece { id: 3, name: "Brandenburg No.3".to_string(), composer: "Bach".to_string(), key_note: "A".to_string(), fundamental_hz: 440.0, mood_band: "alpha".to_string(), midi_file: "assets/classical/bach_brandenburg3.mid".to_string() },
    ClassicalPiece { id: 4, name: "Four Seasons Spring".to_string(), composer: "Vivaldi".to_string(), key_note: "F".to_string(), fundamental_hz: 349.0, mood_band: "theta".to_string(), midi_file: "assets/classical/vivaldi_spring.mid".to_string() },
    ClassicalPiece { id: 5, name: "Requiem".to_string(), composer: "Mozart".to_string(), key_note: "G".to_string(), fundamental_hz: 392.0, mood_band: "delta".to_string(), midi_file: "assets/classical/mozart_requiem.mid".to_string() },
    ClassicalPiece { id: 6, name: "1812 Overture".to_string(), composer: "Tchaikovsky".to_string(), key_note: "C".to_string(), fundamental_hz: 523.0, mood_band: "beta".to_string(), midi_file: "assets/classical/tchaikovsky_1812.mid".to_string() },
    ClassicalPiece { id: 7, name: "Clair de Lune".to_string(), composer: "Debussy".to_string(), key_note: "E".to_string(), fundamental_hz: 330.0, mood_band: "theta".to_string(), midi_file: "assets/classical/debussy_clair.mid".to_string() },
    ClassicalPiece { id: 8, name: "Adagio for Strings".to_string(), composer: "Barber".to_string(), key_note: "B".to_string(), fundamental_hz: 247.0, mood_band: "delta".to_string(), midi_file: "assets/classical/barber_adagio.mid".to_string() },
    ClassicalPiece { id: 9, name: "Ride of the Valkyries".to_string(), composer: "Wagner".to_string(), key_note: "Bb".to_string(), fundamental_hz: 466.0, mood_band: "gamma".to_string(), midi_file: "assets/classical/wagner_valkyries.mid".to_string() },
    ClassicalPiece { id: 10, name: "Peer Gynt Morning".to_string(), composer: "Grieg".to_string(), key_note: "E".to_string(), fundamental_hz: 659.0, mood_band: "alpha".to_string(), midi_file: "assets/classical/grieg_morning.mid".to_string() },
    ClassicalPiece { id: 11, name: "Air on G String".to_string(), composer: "Bach".to_string(), key_note: "G".to_string(), fundamental_hz: 196.0, mood_band: "theta".to_string(), midi_file: "assets/classical/bach_air.mid".to_string() },
    ClassicalPiece { id: 12, name: "Canon in D".to_string(), composer: "Pachelbel".to_string(), key_note: "D".to_string(), fundamental_hz: 294.0, mood_band: "alpha".to_string(), midi_file: "assets/classical/pachelbel_canon.mid".to_string() },
    ClassicalPiece { id: 13, name: "Nocturne Op.9 No.2".to_string(), composer: "Chopin".to_string(), key_note: "Eb".to_string(), fundamental_hz: 311.0, mood_band: "delta".to_string(), midi_file: "assets/classical/chopin_nocturne.mid".to_string() },
    ClassicalPiece { id: 14, name: "Messiah Hallelujah".to_string(), composer: "Handel".to_string(), key_note: "C".to_string(), fundamental_hz: 523.0, mood_band: "beta".to_string(), midi_file: "assets/classical/handel_hallelujah.mid".to_string() },
    ClassicalPiece { id: 15, name: "Flight of Bumblebee".to_string(), composer: "Rimsky-Korsakov".to_string(), key_note: "A".to_string(), fundamental_hz: 880.0, mood_band: "gamma".to_string(), midi_file: "assets/classical/rimsky_bumblebee.mid".to_string() },
    ClassicalPiece { id: 16, name: "Blue Danube".to_string(), composer: "Strauss".to_string(), key_note: "F".to_string(), fundamental_hz: 349.0, mood_band: "theta".to_string(), midi_file: "assets/classical/strauss_danube.mid".to_string() },
    ClassicalPiece { id: 17, name: "Wedding March".to_string(), composer: "Mendelssohn".to_string(), key_note: "C".to_string(), fundamental_hz: 523.0, mood_band: "beta".to_string(), midi_file: "assets/classical/mendelssohn_wedding.mid".to_string() },
    ClassicalPiece { id: 18, name: "Pomp and Circumstance".to_string(), composer: "Elgar".to_string(), key_note: "G".to_string(), fundamental_hz: 392.0, mood_band: "alpha".to_string(), midi_file: "assets/classical/elgar_pomp.mid".to_string() },
    ClassicalPiece { id: 19, name: "Planets Mars".to_string(), composer: "Holst".to_string(), key_note: "C".to_string(), fundamental_hz: 261.0, mood_band: "beta".to_string(), midi_file: "assets/classical/holst_mars.mid".to_string() },
    ClassicalPiece { id: 20, name: "Bolero".to_string(), composer: "Ravel".to_string(), key_note: "E".to_string(), fundamental_hz: 330.0, mood_band: "theta".to_string(), midi_file: "assets/classical/ravel_bolero.mid".to_string() },
    ClassicalPiece { id: 21, name: "Danse Macabre".to_string(), composer: "Saint-Saens".to_string(), key_note: "B".to_string(), fundamental_hz: 247.0, mood_band: "delta".to_string(), midi_file: "assets/classical/saintsaens_danse.mid".to_string() },
    ClassicalPiece { id: 22, name: "Carmen Habanera".to_string(), composer: "Bizet".to_string(), key_note: "Bb".to_string(), fundamental_hz: 466.0, mood_band: "gamma".to_string(), midi_file: "assets/classical/bizet_carmen.mid".to_string() },
    ClassicalPiece { id: 23, name: "La Traviata Brindisi".to_string(), composer: "Verdi".to_string(), key_note: "E".to_string(), fundamental_hz: 659.0, mood_band: "alpha".to_string(), midi_file: "assets/classical/verdi_traviata.mid".to_string() },
    ClassicalPiece { id: 24, name: "Symphony No.9 New World".to_string(), composer: "Dvorak".to_string(), key_note: "G".to_string(), fundamental_hz: 196.0, mood_band: "theta".to_string(), midi_file: "assets/classical/dvorak_newworld.mid".to_string() },
    ClassicalPiece { id: 25, name: "Hungarian Dance No.5".to_string(), composer: "Brahms".to_string(), key_note: "D".to_string(), fundamental_hz: 294.0, mood_band: "beta".to_string(), midi_file: "assets/classical/brahms_hungarian5.mid".to_string() },
    ClassicalPiece { id: 26, name: "Hungarian Rhapsody No.2".to_string(), composer: "Liszt".to_string(), key_note: "Eb".to_string(), fundamental_hz: 311.0, mood_band: "gamma".to_string(), midi_file: "assets/classical/liszt_rhapsody2.mid".to_string() },
    ClassicalPiece { id: 27, name: "Toccata and Fugue".to_string(), composer: "Bach".to_string(), key_note: "G".to_string(), fundamental_hz: 392.0, mood_band: "delta".to_string(), midi_file: "assets/classical/bach_toccata.mid".to_string() },
    ClassicalPiece { id: 28, name: "Eine Kleine Nachtmusik".to_string(), composer: "Mozart".to_string(), key_note: "C".to_string(), fundamental_hz: 523.0, mood_band: "alpha".to_string(), midi_file: "assets/classical/mozart_nachtmusik.mid".to_string() },
    ClassicalPiece { id: 29, name: "Moonlight Sonata".to_string(), composer: "Beethoven".to_string(), key_note: "C".to_string(), fundamental_hz: 261.0, mood_band: "theta".to_string(), midi_file: "assets/classical/beethoven_moonlight.mid".to_string() },
    ClassicalPiece { id: 30, name: "Ave Maria".to_string(), composer: "Schubert".to_string(), key_note: "F".to_string(), fundamental_hz: 349.0, mood_band: "delta".to_string(), midi_file: "assets/classical/schubert_avemaria.mid".to_string() },
    ClassicalPiece { id: 31, name: "Can-Can".to_string(), composer: "Offenbach".to_string(), key_note: "C".to_string(), fundamental_hz: 523.0, mood_band: "beta".to_string(), midi_file: "assets/classical/offenbach_cancan.mid".to_string() },
    ClassicalPiece { id: 32, name: "William Tell Overture".to_string(), composer: "Rossini".to_string(), key_note: "A".to_string(), fundamental_hz: 880.0, mood_band: "gamma".to_string(), midi_file: "assets/classical/rossini_williamtell.mid".to_string() },
    ClassicalPiece { id: 33, name: "Sabre Dance".to_string(), composer: "Khachaturian".to_string(), key_note: "Bb".to_string(), fundamental_hz: 466.0, mood_band: "beta".to_string(), midi_file: "assets/classical/khachaturian_sabre.mid".to_string() },
    ClassicalPiece { id: 34, name: "Gymnopedie No.1".to_string(), composer: "Satie".to_string(), key_note: "E".to_string(), fundamental_hz: 330.0, mood_band: "theta".to_string(), midi_file: "assets/classical/satie_gymnopedie.mid".to_string() },
    ClassicalPiece { id: 35, name: "Adagio".to_string(), composer: "Albinoni".to_string(), key_note: "B".to_string(), fundamental_hz: 247.0, mood_band: "delta".to_string(), midi_file: "assets/classical/albinoni_adagio.mid".to_string() },
    ClassicalPiece { id: 36, name: "Jesu Joy of Man's Desiring".to_string(), composer: "Bach".to_string(), key_note: "G".to_string(), fundamental_hz: 196.0, mood_band: "alpha".to_string(), midi_file: "assets/classical/bach_jesu.mid".to_string() },
];

pub fn get_piece_by_id(id: u8) -> Option<&'static ClassicalPiece> {
    CLASSICAL_PIECES.iter().find(|p| p.id == id)
}

pub fn get_pieces_by_mood(mood: &str) -> Vec<&'static ClassicalPiece> {
    CLASSICAL_PIECES.iter().filter(|p| p.mood_band == mood).collect()
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_all_pieces_have_unique_ids() {
        let mut ids: Vec<u8> = CLASSICAL_PIECES.iter().map(|p| p.id).collect();
        ids.sort();
        let unique_count = ids.iter().collect::<std::collections::HashSet<_>>().len();
        assert_eq!(unique_count, 36);
    }
    
    #[test]
    fn test_get_piece_by_id() {
        let piece = get_piece_by_id(1).unwrap();
        assert_eq!(piece.composer, "Beethoven");
    }
}
