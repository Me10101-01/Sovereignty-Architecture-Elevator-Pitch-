# Classical MIDI Files

This directory contains MIDI files for the 36 curated classical pieces.

## File List

1. `beethoven_sym5.mid` - Symphony No.5 in C minor (261Hz)
2. `beethoven_sym9.mid` - Symphony No.9 in D minor (294Hz)
3. `bach_brandenburg3.mid` - Brandenburg Concerto No.3 (440Hz)
4. `vivaldi_spring.mid` - Four Seasons: Spring (349Hz)
5. `mozart_requiem.mid` - Requiem (392Hz)
6. `tchaikovsky_1812.mid` - 1812 Overture (523Hz)
7. `debussy_clair.mid` - Clair de Lune (330Hz)
8. `barber_adagio.mid` - Adagio for Strings (247Hz)
9. `wagner_valkyries.mid` - Ride of the Valkyries (466Hz)
10. `grieg_morning.mid` - Peer Gynt: Morning (659Hz)
11. `bach_air.mid` - Air on G String (196Hz)
12. `pachelbel_canon.mid` - Canon in D (294Hz)
13. `chopin_nocturne.mid` - Nocturne Op.9 No.2 (311Hz)
14. `handel_hallelujah.mid` - Messiah: Hallelujah (523Hz)
15. `rimsky_bumblebee.mid` - Flight of the Bumblebee (880Hz)
16. `strauss_danube.mid` - Blue Danube (349Hz)
17. `mendelssohn_wedding.mid` - Wedding March (523Hz)
18. `elgar_pomp.mid` - Pomp and Circumstance (392Hz)
19. `holst_mars.mid` - The Planets: Mars (261Hz)
20. `ravel_bolero.mid` - Bolero (330Hz)
21. `saintsaens_danse.mid` - Danse Macabre (247Hz)
22. `bizet_carmen.mid` - Carmen: Habanera (466Hz)
23. `verdi_traviata.mid` - La Traviata: Brindisi (659Hz)
24. `dvorak_newworld.mid` - Symphony No.9 "New World" (196Hz)
25. `brahms_hungarian5.mid` - Hungarian Dance No.5 (294Hz)
26. `liszt_rhapsody2.mid` - Hungarian Rhapsody No.2 (311Hz)
27. `bach_toccata.mid` - Toccata and Fugue (392Hz)
28. `mozart_nachtmusik.mid` - Eine Kleine Nachtmusik (523Hz)
29. `beethoven_moonlight.mid` - Moonlight Sonata (261Hz)
30. `schubert_avemaria.mid` - Ave Maria (349Hz)
31. `offenbach_cancan.mid` - Can-Can (523Hz)
32. `rossini_williamtell.mid` - William Tell Overture (880Hz)
33. `khachaturian_sabre.mid` - Sabre Dance (466Hz)
34. `satie_gymnopedie.mid` - Gymnopedie No.1 (330Hz)
35. `albinoni_adagio.mid` - Adagio (247Hz)
36. `bach_jesu.mid` - Jesu, Joy of Man's Desiring (196Hz)

## Usage

MIDI files are parsed using the `midly` crate in Rust. Each file contains:
- Note sequences mapped to frequencies
- Tempo and timing information
- Instrument assignments

## MuseScore

These pieces can be generated/edited using MuseScore, an open-source music notation software.

**Note**: Actual MIDI files not included in repository to keep size minimal. 
In production, obtain from public domain sources or generate via MuseScore.
