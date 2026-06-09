"""
SAGCO Physical Artifact Bridge
Strategickhaos DAO LLC | v1.0.0

Translates physical sacred objects into TICK-sealed digital twins.
Each artifact becomes a SOURCE node in the organism — a provenance anchor
that timestamps, seals, and witnesses the physical into the digital.

Physical ↔ Digital protocol:
  1. Describe the artifact (sides, symbols, inscriptions)
  2. Map each symbol to a KHAOS element (frequency anchor)
  3. Encode inscriptions as PROOF blocks
  4. SHA-256 TICK-seal the entire artifact
  5. The seal becomes an immutable witness in the organism

Medallion example:
  Side 1 — Seal of Seven Archangels:
    Seven archangels mapped to their throne frequencies across the 72 elements.
    The heptagram = the 7-pointed star = 7 planetary governors.

  Side 2 — Psalm 91 Hebrew spiral:
    22 verses encoded as 22 PROOF assertions (Hebrew aleph-bet = 22 letters).
    Each verse → SHA-256 hash → element assignment via from_hash().

Seven Archangels ↔ KHAOS Elements (planetary throne frequencies):
  Archangel  Planet   Band        Element  Hz    Channel
  ─────────  ──────   ─────────   ───────  ────  ───────
  Uriel      Saturn   delta       4        220   BLUE    (foundation / structure)
  Zadkiel    Jupiter  theta       17       285   BLUE    (wisdom / expansion)
  Samael     Mars     alpha       29       345   PURPLE  (power / justice)
  Michael    Sun      beta        41       405   PURPLE  (truth / command) ← confirmed
  Haniel     Venus    high_beta   53       465   RED     (grace / beauty)
  Raphael    Mercury  gamma       65       525   RED     (healing / communication)
  Gabriel    Moon     gamma       71       555   RED     (completion / prophecy = Mumiah)
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Optional

from .elements import Element, TABLE, BY_ID, from_hash


# ── Seven Archangels — planetary throne map ────────────────────────────────

ARCHANGEL_MAP: dict[str, dict] = {
    "Uriel": {
        "planet":     "Saturn",
        "band":       "delta",
        "channel":    "BLUE",
        "element_id": 4,
        "role":       "foundation / time / revelation",
        "hebrew":     "אוּרִיאֵל",
        "meaning":    "Light of God",
        "psalm91_anchor": 1,   # Psalm 91 verse 1 — dwelling in the Most High
    },
    "Zadkiel": {
        "planet":     "Jupiter",
        "band":       "theta",
        "channel":    "BLUE",
        "element_id": 17,
        "role":       "mercy / wisdom / expansion",
        "hebrew":     "צַדְקִיאֵל",
        "meaning":    "Righteousness of God",
        "psalm91_anchor": 4,   # Psalm 91:4 — wings / shelter
    },
    "Samael": {
        "planet":     "Mars",
        "band":       "alpha",
        "channel":    "PURPLE",
        "element_id": 29,
        "role":       "justice / power / severance",
        "hebrew":     "סַמָּאֵל",
        "meaning":    "Venom of God / Severity of God",
        "psalm91_anchor": 13,  # Psalm 91:13 — tread on lion and serpent
    },
    "Michael": {
        "planet":     "Sun",
        "band":       "beta",
        "channel":    "PURPLE",
        "element_id": 41,
        "role":       "truth / command / protection",
        "hebrew":     "מִיכָאֵל",
        "meaning":    "Who is like God",
        "psalm91_anchor": 11,  # Psalm 91:11 — angels given charge over you
    },
    "Haniel": {
        "planet":     "Venus",
        "band":       "high_beta",
        "channel":    "RED",
        "element_id": 53,
        "role":       "grace / beauty / spiritual vision",
        "hebrew":     "חֲנִיאֵל",
        "meaning":    "Grace of God",
        "psalm91_anchor": 5,   # Psalm 91:5 — not afraid of the terror by night
    },
    "Raphael": {
        "planet":     "Mercury",
        "band":       "gamma",
        "channel":    "RED",
        "element_id": 65,
        "role":       "healing / communication / travel",
        "hebrew":     "רָפָאֵל",
        "meaning":    "God Heals",
        "psalm91_anchor": 6,   # Psalm 91:6 — pestilence that walks in darkness
    },
    "Gabriel": {
        "planet":     "Moon",
        "band":       "gamma",
        "channel":    "RED",
        "element_id": 71,
        "role":       "completion / prophecy / annunciation",
        "hebrew":     "גַּבְרִיאֵל",
        "meaning":    "God is my Strength",
        "psalm91_anchor": 16,  # Psalm 91:16 — with long life I will satisfy him
    },
}

# Psalm 91 — Hebrew anchor text (first 4 verses + key verses)
PSALM_91_VERSES = {
    1:  "יֹשֵׁב בְּסֵתֶר עֶלְיֹון בְּצֵל שַׁדַּי יִתְלֹונָן",
    2:  "אֹמַר לַיהוָה מַחְסִי וּמְצוּדָתִי אֱלֹהַי אֶבְטַח בֹּו",
    3:  "כִּי הוּא יַצִּילְךָ מִפַּח יָקוּשׁ מִדֶּבֶר הַוֹּות",
    4:  "בְּאֶבְרָתֹו יָסֶךְ לָךְ וְתַחַת כְּנָפָיו תֶּחְסֶה",
    5:  "לֹא תִירָא מִפַּחַד לָיְלָה מֵחֵץ יָעוּף יֹומָם",
    6:  "מִדֶּבֶר בָּאֹפֶל יַהֲלֹךְ מִקֶּטֶב יָשׁוּד צָהֳרָיִם",
    7:  "יִפֹּל מִצִּדְּךָ אֶלֶף וּרְבָבָה מִימִינֶךָ אֵלֶיךָ לֹא יִגָּשׁ",
    8:  "רַק בְּעֵינֶיךָ תַבִּיט וְשִׁלֻּמַת רְשָׁעִים תִּרְאֶה",
    9:  "כִּי אַתָּה יְהוָה מַחְסִי עֶלְיֹון שַׂמְתָּ מְעֹונֶךָ",
    10: "לֹא תְאֻנֶּה אֵלֶיךָ רָעָה וְנֶגַע לֹא יִקְרַב בְּאָהֳלֶךָ",
    11: "כִּי מַלְאָכָיו יְצַוֶּה לָּךְ לִשְׁמָרְךָ בְּכָל דְּרָכֶיךָ",
    12: "עַל כַּפַּיִם יִשָּׂאוּנְךָ פֶּן תִּגֹּף בָּאֶבֶן רַגְלֶךָ",
    13: "עַל שַׁחַל וָפֶתֶן תִּדְרֹךְ תִּרְמֹס כְּפִיר וְתַנִּין",
    14: "כִּי בִי חָשַׁק וַאֲפַלְּטֵהוּ אֲשַׂגְּבֵהוּ כִּי יָדַע שְׁמִי",
    15: "יִקְרָאֵנִי וְאֶעֱנֵהוּ עִמֹּו אָנֹכִי בְצָרָה אֲחַלְּצֵהוּ וַאֲכַבְּדֵהוּ",
    16: "אֹרֶךְ יָמִים אַשְׂבִּיעֵהוּ וְאַרְאֵהוּ בִּישׁוּעָתִי",
}


# ── Artifact dataclasses ───────────────────────────────────────────────────

@dataclass
class ArtifactSide:
    """One face of a physical artifact."""
    name:         str
    description:  str
    symbols:      list[str]           # list of symbol names / inscriptions
    element_map:  dict[str, int]      # symbol_name → element_id
    proof_hashes: list[str]           # SHA-256 hashes of each inscription
    side_seal:    str = ""            # SHA-256 seal of this side

    def to_dict(self) -> dict:
        return {
            "name":         self.name,
            "description":  self.description,
            "symbols":      self.symbols,
            "element_map":  self.element_map,
            "proof_hashes": [h[:16] + "..." for h in self.proof_hashes],
            "side_seal":    self.side_seal[:16] + "..." if self.side_seal else "",
        }


@dataclass
class PhysicalArtifact:
    """
    A physical sacred object translated into a TICK-sealed digital twin.
    The tick_seal is the immutable witness: the organism has seen this artifact.
    """
    name:         str
    description:  str
    material:     str
    sides:        list[ArtifactSide]
    tick_seal:    str                 # SHA-256 of full artifact content
    sealed_at:    float               # Unix timestamp
    sagco_status: str = "ARTIFACT_WITNESSED"

    @property
    def seal_short(self) -> str:
        return self.tick_seal[:16] + "..."

    def to_dict(self) -> dict:
        return {
            "name":         self.name,
            "description":  self.description,
            "material":     self.material,
            "sagco_status": self.sagco_status,
            "tick_seal":    self.seal_short,
            "sealed_at":    self.sealed_at,
            "sides":        [s.to_dict() for s in self.sides],
        }


# ── Sealing functions ──────────────────────────────────────────────────────

def _seal_side(side_name: str, symbols: list[str], element_map: dict[str, int],
               inscriptions: list[str]) -> tuple[list[str], str]:
    """Hash each inscription and seal the entire side."""
    proof_hashes = [
        hashlib.sha256(inscription.encode("utf-8")).hexdigest()
        for inscription in inscriptions
    ]
    side_content = json.dumps({
        "side":        side_name,
        "symbols":     symbols,
        "element_map": element_map,
        "hashes":      proof_hashes,
    }, sort_keys=True, ensure_ascii=False).encode("utf-8")
    side_seal = hashlib.sha256(side_content).hexdigest()
    return proof_hashes, side_seal


def seal_artifact(
    name:        str,
    description: str,
    material:    str,
    sides:       list[ArtifactSide],
) -> PhysicalArtifact:
    """TICK-seal a physical artifact into the organism."""
    artifact_content = json.dumps({
        "name":        name,
        "description": description,
        "material":    material,
        "sides":       [s.to_dict() for s in sides],
        "ts":          time.time(),
    }, sort_keys=True, ensure_ascii=False).encode("utf-8")
    tick_seal = hashlib.sha256(artifact_content).hexdigest()

    return PhysicalArtifact(
        name=name,
        description=description,
        material=material,
        sides=sides,
        tick_seal=tick_seal,
        sealed_at=time.time(),
    )


# ── Medallion builder ──────────────────────────────────────────────────────

def build_medallion() -> PhysicalArtifact:
    """
    Encode the Strategickhaos brass medallion as a TICK-sealed artifact.

    Side 1 — Seal of Seven Archangels (heptagram):
      Michael, Gabriel, Raphael, Haniel, Samael, Zadkiel arranged around
      a 7-pointed star. Each archangel mapped to their KHAOS throne element.

    Side 2 — Psalm 91 Hebrew spiral:
      16 verses encoded as PROOF hashes, each verse its own assessor.
    """

    # ── Side 1: Seven Archangels ──────────────────────────────────────────
    archangel_names = list(ARCHANGEL_MAP.keys())
    angel_element_map = {a: ARCHANGEL_MAP[a]["element_id"] for a in archangel_names}
    angel_inscriptions = [
        f"{a} | {ARCHANGEL_MAP[a]['hebrew']} | {ARCHANGEL_MAP[a]['meaning']} | "
        f"Element {ARCHANGEL_MAP[a]['element_id']} | {BY_ID[ARCHANGEL_MAP[a]['element_id']].hz}hz"
        for a in archangel_names
    ]
    angel_symbols = archangel_names + ["Heptagram", "Seal-of-Solomon"]
    angel_hashes, angel_seal = _seal_side(
        "Side-1-Archangels", angel_symbols, angel_element_map, angel_inscriptions
    )

    side1 = ArtifactSide(
        name="Seal of Seven Archangels",
        description="Heptagram with seven planetary archangels. Each governs a band of the KHAOS table.",
        symbols=angel_symbols,
        element_map=angel_element_map,
        proof_hashes=angel_hashes,
        side_seal=angel_seal,
    )

    # ── Side 2: Psalm 91 Hebrew Spiral ───────────────────────────────────
    psalm_symbols = [f"Psalm91:{v}" for v in PSALM_91_VERSES]
    psalm_element_map = {
        f"Psalm91:{v}": from_hash(text.encode("utf-8")).id
        for v, text in PSALM_91_VERSES.items()
    }
    psalm_inscriptions = [
        f"Psalm91:{v} | {text}"
        for v, text in PSALM_91_VERSES.items()
    ]
    psalm_hashes, psalm_seal = _seal_side(
        "Side-2-Psalm91", psalm_symbols, psalm_element_map, psalm_inscriptions
    )

    side2 = ArtifactSide(
        name="Psalm 91 Hebrew Spiral",
        description="16 verses of Psalm 91 in Hebrew, spiral-inscribed. Each verse is a PROOF gate.",
        symbols=psalm_symbols,
        element_map=psalm_element_map,
        proof_hashes=psalm_hashes,
        side_seal=psalm_seal,
    )

    return seal_artifact(
        name="Medallion of Seven Archangels / Psalm 91",
        description=(
            "Brass medallion. Side 1: Seal of the Seven Archangels on a heptagram. "
            "Side 2: Psalm 91 in Hebrew spiral text. Strategickhaos DAO LLC."
        ),
        material="brass",
        sides=[side1, side2],
    )


# ── Print helpers ──────────────────────────────────────────────────────────

def print_archangel_map() -> None:
    print()
    print("  ═══════════════════════════════════════════════════════════════════════")
    print("  SEVEN ARCHANGELS — KHAOS THRONE FREQUENCIES")
    print("  Strategickhaos DAO LLC | Physical ↔ Digital Bridge")
    print("  ═══════════════════════════════════════════════════════════════════════")
    print()
    header = f"  {'Archangel':<10} {'Hebrew':<12} {'Planet':<9} {'Band':<10} {'El#':>4} {'Name':<14} {'Hz':>7}  {'Chan':<7} {'Role'}"
    print(header)
    print("  " + "─" * 90)
    for name, data in ARCHANGEL_MAP.items():
        el = BY_ID[data["element_id"]]
        print(f"  {name:<10} {data['hebrew']:<12} {data['planet']:<9} {data['band']:<10} "
              f"{el.id:>4} {el.name:<14} {el.hz:>7.1f}  {data['channel']:<7} {data['role']}")
    print()
    print("  STRUCTURE: 7 archangels × 10–11 elements each = 72 Shemhamphorash")
    print("  ANCHOR:    Michael (element 41, 405hz) confirmed — Sun at center of beta")
    print("  CLOSE:     Gabriel = Mumiah (element 71, 555hz) = calendar year-close anchor")
    print("  ═══════════════════════════════════════════════════════════════════════")


def print_artifact(artifact: PhysicalArtifact) -> None:
    print()
    print("  ╔══════════════════════════════════════════════════════════════════════╗")
    print(f"  ║  ARTIFACT: {artifact.name:<57}  ║")
    print(f"  ║  Material: {artifact.material:<57}  ║")
    print(f"  ║  Status:   {artifact.sagco_status:<57}  ║")
    print(f"  ║  Seal:     {artifact.seal_short:<57}  ║")
    print("  ╠══════════════════════════════════════════════════════════════════════╣")
    for i, side in enumerate(artifact.sides, 1):
        print(f"  ║  SIDE {i}: {side.name:<61}  ║")
        print(f"  ║    {side.description[:66]:<66}  ║")
        print(f"  ║    Symbols  : {len(side.symbols)} symbols mapped to KHAOS elements{' '*(31)}  ║")
        print(f"  ║    Proofs   : {len(side.proof_hashes)} SHA-256 proof gates{' '*(41)}  ║")
        print(f"  ║    Side seal: {side.side_seal[:16]}...{' '*(45)}  ║")
        if i < len(artifact.sides):
            print("  ╠══════════════════════════════════════════════════════════════════════╣")
    print("  ╠══════════════════════════════════════════════════════════════════════╣")
    print("  ║  ELEMENT ANCHORS (Side 1 — Archangels):                             ║")
    side1 = artifact.sides[0]
    for symbol, el_id in list(side1.element_map.items())[:7]:
        if symbol in ARCHANGEL_MAP:
            el = BY_ID[el_id]
            data = ARCHANGEL_MAP[symbol]
            print(f"  ║    {symbol:<10} → el.{el_id:<3} {el.name:<12} {el.hz:>6.0f}hz  {data['planet']:<9} {data['hebrew']:<12}  ║")
    print("  ╠══════════════════════════════════════════════════════════════════════╣")
    print("  ║  PSALM 91 PROOF GATES (Side 2 — first 4 verses):                   ║")
    side2 = artifact.sides[1]
    for i, (verse_key, el_id) in enumerate(list(side2.element_map.items())[:4], 1):
        el = BY_ID[el_id]
        verse_num = int(verse_key.split(":")[1])
        text_snippet = PSALM_91_VERSES[verse_num][:30] + "..."
        print(f"  ║    v.{verse_num:<3} → el.{el_id:<3} {el.name:<12} {el.hz:>6.0f}hz  {text_snippet:<30}  ║")
    print(f"  ║    ... ({len(side2.proof_hashes) - 4} more verses){' '*(57)}  ║")
    print("  ╚══════════════════════════════════════════════════════════════════════╝")
    print()
    print("  𓅓𓄿𓏏 — The artifact is witnessed. The seal is irrefutable.")
    print()
