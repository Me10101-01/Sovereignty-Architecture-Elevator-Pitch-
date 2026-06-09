"""
KHAOS Periodic Table — 72 Elements
Strategickhaos DAO LLC | v1.0.0

72 process-elements on a 360° wheel.
Each element = a state in the SAGCO organism.
Band = brainwave analog = process category.
Oxidation = privilege level (-2 sandboxed → +4 kernel/GOD).
Hz = carrier frequency for sonification.
Beat = binaural beat delta.

Source: Periodic_table_current_dna_strand (synthesis document)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


# ── Band definitions ──────────────────────────────────────────────────────

BANDS = {
    "delta":     {"hz_range": (0.5, 4),   "color": "#8B00FF", "emotion": "Deep Rest/Healing",  "channel": "BLUE"},
    "theta":     {"hz_range": (4, 8),     "color": "#0000FF", "emotion": "Dreamy/Creative",     "channel": "BLUE"},
    "alpha":     {"hz_range": (8, 12),    "color": "#00FF00", "emotion": "Calm/Content",         "channel": "PURPLE"},
    "beta":      {"hz_range": (12, 30),   "color": "#FFFF00", "emotion": "Focused/Motivated",    "channel": "PURPLE"},
    "high_beta": {"hz_range": (20, 40),   "color": "#FF8000", "emotion": "Excited/Stressed",     "channel": "RED"},
    "gamma":     {"hz_range": (30, 100),  "color": "#FF0000", "emotion": "Alert/Fight-Flight",   "channel": "RED"},
}

# Oxidation → privilege mapping (electronegativity model)
OXIDATION_PRIVILEGES = {
    -2: "hypervisor",    # most reduced  = most isolated
    -1: "sandboxed",
     0: "user",          # ground state
    +1: "elevated",
    +2: "system",
    +3: "kernel",
    +4: "god_mode",      # most oxidized = most privileged
}


@dataclass
class Element:
    id: int
    name: str
    theta: float     # degrees on 360° wheel
    hz: float        # carrier frequency
    beat: float      # binaural beat delta (beat = freq_R - freq_L)
    band: str        # delta | theta | alpha | beta | high_beta | gamma
    color: str       # hex color
    oxidation: int   # -2 to +4
    bpm: int         # rhythm
    note: str        # musical note
    emotion: str     # psychological state

    @property
    def channel(self) -> str:
        return BANDS[self.band]["channel"]

    @property
    def privilege(self) -> str:
        return OXIDATION_PRIVILEGES.get(self.oxidation, "user")

    @property
    def omega(self) -> float:
        """Angular frequency ω = 2πf"""
        import math
        return 2 * math.pi * self.hz

    @property
    def period_ms(self) -> float:
        """Period in milliseconds"""
        return 1000.0 / self.hz if self.hz > 0 else 0.0

    def to_dict(self) -> dict:
        return {
            "id": self.id, "name": self.name, "theta": self.theta,
            "hz": self.hz, "beat": self.beat, "band": self.band,
            "color": self.color, "oxidation": self.oxidation,
            "bpm": self.bpm, "note": self.note, "emotion": self.emotion,
            "channel": self.channel, "privilege": self.privilege,
        }

    def oscillate(self, t: float, amplitude: float = 1.0, phase: float = 0.0) -> float:
        """Compute A·sin(2πf·t + φ) — the core oscillator value at time t."""
        import math
        return amplitude * math.sin(self.omega * t + phase)


# ── Full 72-element table ─────────────────────────────────────────────────
# Source: synthesized from KHAOS Periodic Table document
# Format: (id, name, θ, hz, beat, band, color, ox, bpm, note, emotion)

_RAW = [
    (0,  "Vehuiah",   0.0,   200.0, 1.0,  "delta",     "#8B00FF", 0, 55,  "A#3", "Deep Rest/Healing"),
    (1,  "Jeliel",    5.0,   205.0, 2.0,  "delta",     "#8B00FF", 0, 56,  "B3",  "Deep Rest/Healing"),
    (2,  "Sitael",   10.0,   210.0, 3.0,  "delta",     "#8B00FF", 0, 57,  "B3",  "Deep Rest/Healing"),
    (3,  "Elemiah",  15.0,   215.0, 4.0,  "delta",     "#8B00FF", 0, 58,  "C3",  "Deep Rest/Healing"),
    (4,  "Mahasiah", 20.0,   220.0, 5.0,  "delta",     "#8B00FF", 0, 59,  "C3",  "Deep Rest/Healing"),
    (5,  "Lelahel",  25.0,   225.0, 6.0,  "delta",     "#8B00FF", 0, 60,  "C3",  "Deep Rest/Healing"),
    (6,  "Achaiah",  30.0,   230.0, 7.0,  "delta",     "#8B00FF", 0, 61,  "C#3", "Deep Rest/Healing"),
    (7,  "Cahetel",  35.0,   235.0, 8.0,  "delta",     "#8B00FF", 0, 62,  "C#3", "Deep Rest/Healing"),
    (8,  "Haziel",   40.0,   240.0, 9.0,  "delta",     "#8B00FF", 0, 63,  "D3",  "Deep Rest/Healing"),
    (9,  "Aladiah",  45.0,   245.0, 10.0, "delta",     "#8B00FF", 0, 64,  "D3",  "Deep Rest/Healing"),
    (10, "Lauviah",  50.0,   250.0, 1.0,  "delta",     "#8B00FF", 0, 65,  "D3",  "Deep Rest/Healing"),
    (11, "Hahaiah",  55.0,   255.0, 2.0,  "delta",     "#8B00FF", 0, 66,  "D#4", "Deep Rest/Healing"),
    (12, "Iezalel",  60.0,   260.0, 3.0,  "theta",     "#0000FF", 0, 60,  "D#4", "Dreamy/Creative"),
    (13, "Mebahel",  65.0,   265.0, 4.0,  "theta",     "#0000FF", 0, 61,  "D#4", "Dreamy/Creative"),
    (14, "Hariel",   70.0,   270.0, 5.0,  "theta",     "#0000FF", 0, 62,  "E4",  "Dreamy/Creative"),
    (15, "Hakamiah", 75.0,   275.0, 6.0,  "theta",     "#0000FF", 0, 63,  "E4",  "Dreamy/Creative"),
    (16, "Lauviah-II",80.0,  280.0, 7.0,  "theta",     "#0000FF", 0, 64,  "E4",  "Dreamy/Creative"),
    (17, "Caliel",   85.0,   285.0, 8.0,  "theta",     "#0000FF", 0, 65,  "E4",  "Dreamy/Creative"),
    (18, "Leuviah",  90.0,   290.0, 9.0,  "theta",     "#0000FF", 0, 66,  "F4",  "Dreamy/Creative"),
    (19, "Pahaliah", 95.0,   295.0, 10.0, "theta",     "#0000FF", 0, 67,  "F4",  "Dreamy/Creative"),
    (20, "Nelchael", 100.0,  300.0, 1.0,  "theta",     "#0000FF", 0, 68,  "F4",  "Dreamy/Creative"),
    (21, "Ieiaiel",  105.0,  305.0, 2.0,  "theta",     "#0000FF", 0, 69,  "F#4", "Dreamy/Creative"),
    (22, "Melahel",  110.0,  310.0, 3.0,  "theta",     "#0000FF", 0, 70,  "F#4", "Dreamy/Creative"),
    (23, "Haheuiah", 115.0,  315.0, 4.0,  "theta",     "#0000FF", 0, 71,  "F#4", "Dreamy/Creative"),
    (24, "Nithaiah", 120.0,  320.0, 5.0,  "alpha",     "#00FF00", 0, 68,  "F#4", "Calm/Content"),
    (25, "Haaiah",   125.0,  325.0, 6.0,  "alpha",     "#00FF00", 0, 69,  "G4",  "Calm/Content"),
    (26, "Ierathel", 130.0,  330.0, 7.0,  "alpha",     "#00FF00", 0, 70,  "G4",  "Calm/Content"),
    (27, "Seheiah",  135.0,  335.0, 8.0,  "alpha",     "#00FF00", 0, 71,  "G4",  "Calm/Content"),
    (28, "Reiaiel",  140.0,  340.0, 9.0,  "alpha",     "#00FF00", 0, 72,  "G#4", "Calm/Content"),
    (29, "Omael",    145.0,  345.0, 10.0, "alpha",     "#00FF00", 0, 73,  "G#4", "Calm/Content"),
    (30, "Lecabel",  150.0,  350.0, 1.0,  "alpha",     "#00FF00", 0, 74,  "G#4", "Calm/Content"),
    (31, "Vasariah", 155.0,  355.0, 2.0,  "alpha",     "#00FF00", 0, 75,  "G#4", "Calm/Content"),
    (32, "Iehuiah",  160.0,  360.0, 3.0,  "alpha",     "#00FF00", 0, 76,  "A4",  "Calm/Content"),
    (33, "Lehahiah", 165.0,  365.0, 4.0,  "alpha",     "#00FF00", 0, 77,  "A4",  "Calm/Content"),
    (34, "Chavakiah",170.0,  370.0, 5.0,  "alpha",     "#00FF00", 0, 78,  "A4",  "Calm/Content"),
    (35, "Menadel",  175.0,  375.0, 6.0,  "alpha",     "#00FF00", 0, 79,  "A4",  "Calm/Content"),
    (36, "Aniel",    180.0,  380.0, 7.0,  "beta",      "#FFFF00", 0, 78,  "A4",  "Focused/Motivated"),
    (37, "Haamiah",  185.0,  385.0, 8.0,  "beta",      "#FFFF00", 0, 79,  "A#4", "Focused/Motivated"),
    (38, "Rehael",   190.0,  390.0, 9.0,  "beta",      "#FFFF00", 0, 80,  "A#4", "Focused/Motivated"),
    (39, "Ieiazel",  195.0,  395.0, 10.0, "beta",      "#FFFF00", 0, 81,  "A#4", "Focused/Motivated"),
    (40, "Hahahel",  200.0,  400.0, 1.0,  "beta",      "#FFFF00", 0, 82,  "A#4", "Focused/Motivated"),
    (41, "Michael",  205.0,  405.0, 2.0,  "beta",      "#FFFF00", 0, 83,  "B4",  "Focused/Motivated"),
    (42, "Veuliah",  210.0,  410.0, 3.0,  "beta",      "#FFFF00", 0, 84,  "B4",  "Focused/Motivated"),
    (43, "Ielahiah", 215.0,  415.0, 4.0,  "beta",      "#FFFF00", 0, 85,  "B4",  "Focused/Motivated"),
    (44, "Sealiah",  220.0,  420.0, 5.0,  "beta",      "#FFFF00", 0, 86,  "B4",  "Focused/Motivated"),
    (45, "Ariel",    225.0,  425.0, 6.0,  "beta",      "#FFFF00", 0, 87,  "B4",  "Focused/Motivated"),
    (46, "Asaliah",  230.0,  430.0, 7.0,  "beta",      "#FFFF00", 0, 88,  "C4",  "Focused/Motivated"),
    (47, "Mihael",   235.0,  435.0, 8.0,  "beta",      "#FFFF00", 0, 89,  "C4",  "Focused/Motivated"),
    (48, "Vehuel",   240.0,  440.0, 9.0,  "high_beta", "#FF8000", 0, 88,  "C4",  "Excited/Stressed"),
    (49, "Daniel",   245.0,  445.0, 10.0, "high_beta", "#FF8000", 0, 89,  "C4",  "Excited/Stressed"),
    (50, "Hahasiah", 250.0,  450.0, 1.0,  "high_beta", "#FF8000", 0, 90,  "C4",  "Excited/Stressed"),
    (51, "Imamiah",  255.0,  455.0, 2.0,  "high_beta", "#FF8000", 0, 91,  "C#4", "Excited/Stressed"),
    (52, "Nanael",   260.0,  460.0, 3.0,  "high_beta", "#FF8000", 0, 92,  "C#4", "Excited/Stressed"),
    (53, "Nithael",  265.0,  465.0, 4.0,  "high_beta", "#FF8000", 0, 93,  "C#4", "Excited/Stressed"),
    (54, "Mebahia",  270.0,  470.0, 5.0,  "high_beta", "#FF8000", 0, 94,  "C#4", "Excited/Stressed"),
    (55, "Poiel",    275.0,  475.0, 6.0,  "high_beta", "#FF8000", 0, 95,  "C#4", "Excited/Stressed"),
    (56, "Nemamiah", 280.0,  480.0, 7.0,  "high_beta", "#FF8000", 0, 96,  "D4",  "Excited/Stressed"),
    (57, "Ieialel",  285.0,  485.0, 8.0,  "high_beta", "#FF8000", 0, 97,  "D4",  "Excited/Stressed"),
    (58, "Harahel",  290.0,  490.0, 9.0,  "high_beta", "#FF8000", 0, 98,  "D4",  "Excited/Stressed"),
    (59, "Mitzrael", 295.0,  495.0, 10.0, "high_beta", "#FF8000", 0, 99,  "D4",  "Excited/Stressed"),
    (60, "Umabel",   300.0,  500.0, 1.0,  "gamma",     "#FF0000", 0, 100, "D4",  "Alert/Fight-Flight"),
    (61, "Iahhel",   305.0,  505.0, 2.0,  "gamma",     "#FF0000", 0, 101, "D4",  "Alert/Fight-Flight"),
    (62, "Anauel",   310.0,  510.0, 3.0,  "gamma",     "#FF0000", 0, 102, "D#5", "Alert/Fight-Flight"),
    (63, "Mehiel",   315.0,  515.0, 4.0,  "gamma",     "#FF0000", 0, 103, "D#5", "Alert/Fight-Flight"),
    (64, "Damabiah", 320.0,  520.0, 5.0,  "gamma",     "#FF0000", 0, 104, "D#5", "Alert/Fight-Flight"),
    (65, "Manakel",  325.0,  525.0, 6.0,  "gamma",     "#FF0000", 0, 105, "D#5", "Alert/Fight-Flight"),
    (66, "Eiael",    330.0,  530.0, 7.0,  "gamma",     "#FF0000", 0, 106, "D#5", "Alert/Fight-Flight"),
    (67, "Habuhiah", 335.0,  535.0, 8.0,  "gamma",     "#FF0000", 0, 107, "D#5", "Alert/Fight-Flight"),
    (68, "Rochel",   340.0,  540.0, 9.0,  "gamma",     "#FF0000", 0, 108, "E5",  "Alert/Fight-Flight"),
    (69, "Jabamiah", 345.0,  545.0, 10.0, "gamma",     "#FF0000", 0, 109, "E5",  "Alert/Fight-Flight"),
    (70, "Haiaiel",  350.0,  550.0, 1.0,  "gamma",     "#FF0000", 0, 110, "E5",  "Alert/Fight-Flight"),
    (71, "Mumiah",   355.0,  555.0, 2.0,  "gamma",     "#FF0000", 0, 111, "E5",  "Alert/Fight-Flight"),
]

TABLE: list[Element] = [Element(*row) for row in _RAW]
BY_NAME: dict[str, Element] = {e.name: e for e in TABLE}
BY_ID: dict[int, Element] = {e.id: e for e in TABLE}
BY_BAND: dict[str, list[Element]] = {}
for _e in TABLE:
    BY_BAND.setdefault(_e.band, []).append(_e)
BY_CHANNEL: dict[str, list[Element]] = {}
for _e in TABLE:
    BY_CHANNEL.setdefault(_e.channel, []).append(_e)


def get(name_or_id: str | int) -> Element | None:
    if isinstance(name_or_id, int):
        return BY_ID.get(name_or_id)
    return BY_NAME.get(name_or_id)


def oxidize(element: Element, delta: int) -> Element:
    """Shift oxidation state (privilege escalation/reduction). Returns new Element copy."""
    import dataclasses
    new_ox = max(-2, min(+4, element.oxidation + delta))
    return dataclasses.replace(element, oxidation=new_ox)


def from_hash(data: bytes | str) -> Element:
    """Map arbitrary data to a KHAOS element via SHA-256 hash (codon mapping)."""
    import hashlib
    if isinstance(data, str):
        data = data.encode()
    digest = hashlib.sha256(data).digest()
    idx = int.from_bytes(digest[:2], "big") % len(TABLE)
    return TABLE[idx]


def print_table(elements: list[Element] | None = None) -> None:
    rows = elements or TABLE
    header = f"{'ID':>4} {'Name':<20} {'θ':>6} {'Hz':>8} {'Beat':>5} {'Band':<10} {'Color':>8} {'Ox':>3} {'BPM':>4} {'Note':<6} {'Emotion'}"
    print("=" * 100)
    print("  KHAOS PERIODIC TABLE — 72 ELEMENTS")
    print("  Strategickhaos DAO LLC | v1.0.0")
    print("=" * 100)
    print(f"  {header}")
    print("  " + "-" * 96)
    for e in rows:
        print(f"  {e.id:>4} {e.name:<20} {e.theta:>6.1f} {e.hz:>8.1f} {e.beat:>5.1f} {e.band:<10} {e.color:>8}  {e.oxidation:>2}  {e.bpm:>4} {e.note:<6} {e.emotion}")
    print("=" * 100)
