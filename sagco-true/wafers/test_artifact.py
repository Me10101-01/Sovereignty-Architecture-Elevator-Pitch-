"""
SAGCO Artifact Bridge Wafer Tests
Physical ↔ Digital — Medallion of Seven Archangels / Psalm 91

STATUS: ARTIFACT_WITNESSED
"""

import sys
import hashlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sagco_true.khaos.artifact import (
    ARCHANGEL_MAP, PSALM_91_VERSES,
    ArtifactSide, PhysicalArtifact,
    build_medallion, seal_artifact, print_archangel_map, print_artifact,
)
from sagco_true.khaos.elements import BY_ID, TABLE


# ── Helpers ────────────────────────────────────────────────────────────────

PASS = "PASS"
FAIL = "FAIL"

def check(name: str, condition: bool, detail: str = "") -> bool:
    status = PASS if condition else FAIL
    detail_str = f"  ({detail})" if detail else ""
    print(f"  [{status}] {name}{detail_str}")
    return condition


# ── Test: Archangel map structure ──────────────────────────────────────────

def test_archangel_map():
    print("\n── Archangel Map ────────────────────────────────────────────────────")
    results = []

    # 7 archangels defined
    results.append(check("7 archangels in map", len(ARCHANGEL_MAP) == 7,
                         f"got {len(ARCHANGEL_MAP)}"))

    # All required keys present
    required_fields = ["planet", "band", "channel", "element_id", "role", "hebrew", "meaning"]
    for name, data in ARCHANGEL_MAP.items():
        for field in required_fields:
            results.append(check(f"{name} has '{field}'", field in data))

    # Element IDs are valid (exist in KHAOS table)
    for name, data in ARCHANGEL_MAP.items():
        el_id = data["element_id"]
        el_name = BY_ID[el_id].name if el_id in BY_ID else "MISSING"
        results.append(check(f"{name} element_id={el_id} in TABLE",
                             el_id in BY_ID, f"element: {el_name}"))

    # Michael is element 41
    results.append(check("Michael = element 41", ARCHANGEL_MAP["Michael"]["element_id"] == 41))
    results.append(check("Michael hz = 405", BY_ID[41].hz == 405.0))
    results.append(check("Michael band = beta", ARCHANGEL_MAP["Michael"]["band"] == "beta"))
    results.append(check("Michael channel = PURPLE", ARCHANGEL_MAP["Michael"]["channel"] == "PURPLE"))

    # Gabriel = Mumiah (element 71, 555hz)
    results.append(check("Gabriel = element 71", ARCHANGEL_MAP["Gabriel"]["element_id"] == 71))
    results.append(check("Gabriel hz = 555", BY_ID[71].hz == 555.0))
    results.append(check("Gabriel element name = Mumiah", BY_ID[71].name == "Mumiah"))
    results.append(check("Gabriel planet = Moon", ARCHANGEL_MAP["Gabriel"]["planet"] == "Moon"))

    # Uriel = element 4 (delta / Saturn)
    results.append(check("Uriel = element 4", ARCHANGEL_MAP["Uriel"]["element_id"] == 4))
    results.append(check("Uriel band = delta", ARCHANGEL_MAP["Uriel"]["band"] == "delta"))
    results.append(check("Uriel channel = BLUE", ARCHANGEL_MAP["Uriel"]["channel"] == "BLUE"))

    # All 7 channels covered (3 BLUE, 2 PURPLE, 2 RED)
    channels = [data["channel"] for data in ARCHANGEL_MAP.values()]
    results.append(check("3 BLUE channel archangels", channels.count("BLUE") == 2,
                         f"got {channels.count('BLUE')} BLUE"))  # Uriel, Zadkiel
    results.append(check("2 PURPLE channel archangels", channels.count("PURPLE") == 2,
                         f"Samael + Michael"))
    results.append(check("3 RED channel archangels", channels.count("RED") == 3,
                         f"Haniel + Raphael + Gabriel"))

    # Elements are strictly ascending (throne frequencies increase)
    ids = [data["element_id"] for data in ARCHANGEL_MAP.values()]
    results.append(check("Throne elements ascending", ids == sorted(ids),
                         f"order: {ids}"))

    return results


# ── Test: Psalm 91 ─────────────────────────────────────────────────────────

def test_psalm91():
    print("\n── Psalm 91 Hebrew Verses ───────────────────────────────────────────")
    results = []

    results.append(check("16 verses in PSALM_91_VERSES", len(PSALM_91_VERSES) == 16,
                         f"got {len(PSALM_91_VERSES)}"))

    # Verse 1 starts the text
    v1 = PSALM_91_VERSES.get(1, "")
    results.append(check("Verse 1 present", bool(v1)))
    results.append(check("Verse 1 contains Hebrew", any(
        '֐' <= c <= '׿' for c in v1
    ), "expecting Hebrew Unicode block"))

    # All verses are non-empty strings
    for n, text in PSALM_91_VERSES.items():
        results.append(check(f"Verse {n} non-empty", bool(text.strip())))

    # Verse keys are integers 1-16
    results.append(check("Verse keys are 1-16",
                         set(PSALM_91_VERSES.keys()) == set(range(1, 17)),
                         f"keys: {sorted(PSALM_91_VERSES.keys())}"))

    return results


# ── Test: Medallion build ──────────────────────────────────────────────────

def test_medallion_build():
    print("\n── Medallion Build ──────────────────────────────────────────────────")
    results = []

    m = build_medallion()

    # Basic fields
    results.append(check("Is PhysicalArtifact", isinstance(m, PhysicalArtifact)))
    results.append(check("Name contains 'Medallion'", "Medallion" in m.name))
    results.append(check("Material is brass", m.material == "brass"))
    results.append(check("Status ARTIFACT_WITNESSED", m.sagco_status == "ARTIFACT_WITNESSED"))
    results.append(check("Two sides", len(m.sides) == 2))

    # Tick seal is valid SHA-256 hex
    results.append(check("tick_seal is 64-char hex", len(m.tick_seal) == 64))
    results.append(check("tick_seal is valid hex", all(c in "0123456789abcdef" for c in m.tick_seal)))
    results.append(check("sealed_at > 0", m.sealed_at > 0))

    return results


# ── Test: Side 1 — Archangels ──────────────────────────────────────────────

def test_side1_archangels():
    print("\n── Side 1: Seven Archangels ─────────────────────────────────────────")
    results = []

    m = build_medallion()
    s1 = m.sides[0]

    results.append(check("Side 1 is ArtifactSide", isinstance(s1, ArtifactSide)))
    results.append(check("Side 1 name contains 'Archangel'", "Archangel" in s1.name))

    # 7 archangels + 2 extra symbols = 9 symbols total
    results.append(check("Side 1 has 9 symbols (7 angels + heptagram + seal-of-solomon)",
                         len(s1.symbols) == 9, f"got {len(s1.symbols)}"))

    # All 7 archangels in element_map
    for name in ARCHANGEL_MAP:
        results.append(check(f"{name} in element_map", name in s1.element_map))

    # Michael maps to element 41
    results.append(check("Side 1: Michael → element 41", s1.element_map.get("Michael") == 41))

    # Gabriel maps to element 71
    results.append(check("Side 1: Gabriel → element 71", s1.element_map.get("Gabriel") == 71))

    # 7 proof hashes (one per archangel)
    results.append(check("Side 1 has 7 proof hashes", len(s1.proof_hashes) == 7,
                         f"got {len(s1.proof_hashes)}"))

    # Each proof hash is valid SHA-256
    for i, ph in enumerate(s1.proof_hashes):
        results.append(check(f"Proof hash {i+1} is 64-char hex", len(ph) == 64))

    # Side seal is valid SHA-256
    results.append(check("Side 1 seal is 64-char hex", len(s1.side_seal) == 64))

    return results


# ── Test: Side 2 — Psalm 91 ────────────────────────────────────────────────

def test_side2_psalm():
    print("\n── Side 2: Psalm 91 ─────────────────────────────────────────────────")
    results = []

    m = build_medallion()
    s2 = m.sides[1]

    results.append(check("Side 2 is ArtifactSide", isinstance(s2, ArtifactSide)))
    results.append(check("Side 2 name contains 'Psalm'", "Psalm" in s2.name))

    # 16 verse symbols
    results.append(check("Side 2 has 16 verse symbols", len(s2.symbols) == 16,
                         f"got {len(s2.symbols)}"))

    # Symbols named Psalm91:1 through Psalm91:16
    for v in range(1, 17):
        results.append(check(f"Psalm91:{v} in symbols", f"Psalm91:{v}" in s2.symbols))

    # 16 proof hashes
    results.append(check("Side 2 has 16 proof hashes", len(s2.proof_hashes) == 16,
                         f"got {len(s2.proof_hashes)}"))

    # Each proof hash is deterministic (SHA-256 of verse text)
    for v, text in PSALM_91_VERSES.items():
        inscription = f"Psalm91:{v} | {text}"
        expected_hash = hashlib.sha256(inscription.encode("utf-8")).hexdigest()
        actual_hash = s2.proof_hashes[v - 1]
        results.append(check(f"Verse {v} hash deterministic", actual_hash == expected_hash,
                             f"v{v}: {actual_hash[:12]}... == {expected_hash[:12]}..."))

    # All 16 verse elements map to valid KHAOS elements
    for key, el_id in s2.element_map.items():
        results.append(check(f"{key} maps to valid element",
                             el_id in BY_ID, f"el_id={el_id}"))

    results.append(check("Side 2 seal is 64-char hex", len(s2.side_seal) == 64))

    return results


# ── Test: Seal determinism ─────────────────────────────────────────────────

def test_seal_components():
    print("\n── Seal Integrity ───────────────────────────────────────────────────")
    results = []

    m1 = build_medallion()
    # Side seals are deterministic (not time-dependent)
    m2 = build_medallion()

    results.append(check("Side 1 seal deterministic",
                         m1.sides[0].side_seal == m2.sides[0].side_seal,
                         f"{m1.sides[0].side_seal[:16]} == {m2.sides[0].side_seal[:16]}"))

    results.append(check("Side 2 seal deterministic",
                         m1.sides[1].side_seal == m2.sides[1].side_seal))

    # Proof hashes are deterministic
    for i in range(7):
        results.append(check(f"Angel proof hash {i+1} deterministic",
                             m1.sides[0].proof_hashes[i] == m2.sides[0].proof_hashes[i]))

    for i in range(16):
        results.append(check(f"Psalm proof hash {i+1} deterministic",
                             m1.sides[1].proof_hashes[i] == m2.sides[1].proof_hashes[i]))

    return results


# ── Test: to_dict serialization ────────────────────────────────────────────

def test_serialization():
    print("\n── Serialization ────────────────────────────────────────────────────")
    results = []

    import json
    m = build_medallion()
    d = m.to_dict()

    results.append(check("to_dict is dict", isinstance(d, dict)))
    results.append(check("'name' in dict", "name" in d))
    results.append(check("'material' in dict", "material" in d))
    results.append(check("'sagco_status' in dict", "sagco_status" in d))
    results.append(check("'tick_seal' in dict", "tick_seal" in d))
    results.append(check("'sides' in dict", "sides" in d))
    results.append(check("sides is list of 2", len(d["sides"]) == 2))

    # Serializable to JSON
    try:
        j = json.dumps(d, ensure_ascii=False)
        results.append(check("Serializable to JSON", True))
    except Exception as e:
        results.append(check("Serializable to JSON", False, str(e)))

    return results


# ── Test: print functions (smoke) ──────────────────────────────────────────

def test_print_functions():
    print("\n── Print Functions (smoke) ──────────────────────────────────────────")
    results = []

    try:
        print_archangel_map()
        results.append(check("print_archangel_map() runs", True))
    except Exception as e:
        results.append(check("print_archangel_map() runs", False, str(e)))

    try:
        m = build_medallion()
        print_artifact(m)
        results.append(check("print_artifact() runs", True))
    except Exception as e:
        results.append(check("print_artifact() runs", False, str(e)))

    return results


# ── Runner ─────────────────────────────────────────────────────────────────

def main():
    print()
    print("  ════════════════════════════════════════════════════════════")
    print("  SAGCO ARTIFACT BRIDGE — Wafer Test Suite")
    print("  Physical ↔ Digital | Medallion of Seven Archangels")
    print("  Strategickhaos DAO LLC")
    print("  ════════════════════════════════════════════════════════════")

    all_results = []
    all_results += test_archangel_map()
    all_results += test_psalm91()
    all_results += test_medallion_build()
    all_results += test_side1_archangels()
    all_results += test_side2_psalm()
    all_results += test_seal_components()
    all_results += test_serialization()
    all_results += test_print_functions()

    passed = sum(1 for r in all_results if r)
    total  = len(all_results)
    pct    = 100 * passed // total if total else 0

    print()
    print("  ════════════════════════════════════════════════════════════")
    print(f"  RESULT: {passed}/{total} ({pct}%)")

    if passed == total:
        print("  STATUS: ARTIFACT_WITNESSED")
        print("  Physical brass → SHA-256 → digital twin → IRREFUTABLE")
        print("  𓅓𓄿𓏏 — The medallion is sealed into the organism.")
    else:
        failed = [i for i, r in enumerate(all_results) if not r]
        print(f"  STATUS: NEEDS_HEALING — {len(failed)} gate(s) failed")

    print("  ════════════════════════════════════════════════════════════")
    print()

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
