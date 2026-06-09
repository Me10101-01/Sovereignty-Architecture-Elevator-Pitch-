"""
SAGCO Primameria Calendar
Prima Materia + 3-6-9 Vortex Time Encoding

All calendars are compared via Julian Day Number (JDN) as the universal spine.
Every date reduces through digital root to the vortex track (3-6-9 or main).
Eru = epoch burn rate: what fraction of the current cosmic cycle is consumed.

Sovereign SAGCO Primameria Calendar:
  6 band-months × 60 days = 360 days (the pure orbital period)
  Drift = leftover days beyond 360 — "vortex debt"
  Named months after the 6 brainwave bands.
  Day names cycle through the 72 KHAOS elements.
  Mumiah (element 71, 555hz) anchors the year-close at day 360.

JDN reference:
  J2000 epoch = JDN 2451545 (2000-01-01 noon)
  Today (2026-06-09) = JDN 2461201
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional

from .vortex import digital_root, classify_vortex, complement
from .elements import TABLE, BY_NAME


# ── JDN core ─────────────────────────────────────────────────────────────────

def gregorian_to_jdn(y: int, m: int, d: int) -> int:
    """Convert proleptic Gregorian date to Julian Day Number."""
    a = (14 - m) // 12
    y2 = y + 4800 - a
    m2 = m + 12 * a - 3
    return d + (153 * m2 + 2) // 5 + 365 * y2 + y2 // 4 - y2 // 100 + y2 // 400 - 32045


def jdn_to_gregorian(jdn: int) -> tuple[int, int, int]:
    """Convert Julian Day Number to proleptic Gregorian (year, month, day)."""
    a = jdn + 32044
    b = (4 * a + 3) // 146097
    c = a - (146097 * b) // 4
    d = (4 * c + 3) // 1461
    e = c - (1461 * d) // 4
    m = (5 * e + 2) // 153
    day   = e - (153 * m + 2) // 5 + 1
    month = m + 3 - 12 * (m // 10)
    year  = 100 * b + d - 4800 + m // 10
    return year, month, day


def julian_to_jdn(y: int, m: int, d: int) -> int:
    """Convert Julian (Old Style) date to JDN."""
    return 367 * y - (7 * (y + (m + 9) // 12)) // 4 + (275 * m) // 9 + d + 1721013 + 1


# ── Ancient calendar epoch anchors (JDN) ─────────────────────────────────────

# These are the JDN of each calendar's epoch (year 0 / year 1 equivalent)
EPOCH_JDN = {
    "gregorian":  gregorian_to_jdn(1, 1, 1),   # Jan 1, 1 CE proleptic
    "julian":     julian_to_jdn(1, 1, 1),        # Jan 1, 1 CE Julian
    "hebrew":     347998,                         # 1 Tishri 1 AM — Oct 7, 3761 BCE
    "islamic":    1948439,                        # 1 Muharram 1 AH — Jul 16, 622 CE
    "mayan":      584283,                         # 0.0.0.0.0 (GMT correlation) — Aug 11, 3114 BCE
    "kali_yuga":  588466,                         # Kali Yuga starts Jan 23, 3102 BCE Julian
    "roman_auc":  1446109,                        # Ab Urbe Condita — Apr 21, 753 BCE Julian
    "persian":    1948320,                        # Nowruz epoch — 622 CE
    "ethiopian":  1724221,                        # Ethiopian epoch — Aug 27, 8 CE
    "chinese":    758326,                         # Legendary start ~2697 BCE (Yellow Emperor)
}

# Approximate total cycle length in days for eru calculation
# (current great cycle / yuga / era — rounded to known cosmic scales)
ERA_LENGTH_DAYS = {
    "gregorian":  3652059,       # 10000 years (arbitrary horizon)
    "julian":     3652060,
    "hebrew":     2127456,       # ~5827 years total (current 6000-year plan = 2,190,000 days)
    "islamic":    3543480,       # ~9700 AH years horizon
    "mayan":      1872000,       # 13 Baktuns — the Long Count Great Cycle
    "kali_yuga":  1577917500,    # Full Kali Yuga = 432,000 years
    "roman_auc":  3652059,
    "persian":    3652500,
    "ethiopian":  3652059,
    "chinese":    21990000,      # 60,000 years (60 cycles of 60 years)
}

# Year length in days for each calendar
YEAR_LENGTH = {
    "gregorian":  365.2425,
    "julian":     365.25,
    "hebrew":     365.2468,      # mean Hebrew year
    "islamic":    354.3671,      # mean lunar year
    "mayan":      365.0,         # Haab = 365 days (Tzolkin=260 for ritual)
    "kali_yuga":  365.25636,     # sidereal year
    "roman_auc":  365.25,
    "persian":    365.24219,     # solar Hijri year
    "ethiopian":  365.25,
    "chinese":    365.2425,
}


@dataclass
class CalendarDate:
    calendar: str
    year: int
    month: int
    day: int
    label: str       # human-readable "Year X, Month Y, Day Z"
    jdn: int
    elapsed_days: int  # days since that calendar's epoch
    elapsed_years: float


@dataclass
class EruBurnRate:
    """
    Epoch Burn Rate — what fraction of the current cosmic cycle is consumed.
    0.0 = epoch just started, 1.0 = epoch fully consumed.
    """
    calendar: str
    elapsed_days: int
    era_length_days: int
    burn_fraction: float     # elapsed / era_length  (0.0 – 1.0+)
    burn_percent: float
    remaining_days: int
    vortex_track: str        # which 3-6-9 track the burn fraction's digit root falls on


@dataclass
class CalendarComparison:
    calendar: str
    today_jdn: int
    elapsed_days: int
    elapsed_years: float
    expected_year: float     # what year would a pure-math count say
    actual_year: int         # what the calendar says
    variance_days: float     # drift = actual_year*year_length - elapsed_days
    drift_rate: float        # days per century of drift
    eru: EruBurnRate
    date: CalendarDate


@dataclass
class PrimameriaDay:
    """
    SAGCO Primameria sovereign calendar day.
    360-day year (6 band-months × 60 days) + vortex debt (drift days).
    """
    sagco_year: int          # years since SAGCO epoch (vortex_369_genesis)
    band_month: int          # 1-6 (delta/theta/alpha/beta/high_beta/gamma)
    band_name: str
    day_of_month: int        # 1-60
    day_of_year: int         # 1-360 (or 361-365 in drift zone)
    in_drift_zone: bool      # beyond day 360
    vortex_day: int          # digital root of day_of_year → 3,6,9 or main
    vortex_track: str
    khaos_element: str       # KHAOS element for this day (id = (day_of_year-1) % 72)
    khaos_hz: float          # Hz of today's element
    mumiah_phase: float      # phase relative to Mumiah (555hz anchor)
    primameria_freq: float   # 555 + vortex_day * 5  (vortex-nudged frequency)
    phase_rad: float         # mumiah_phase in radians
    complement_day: int      # 9-complement of vortex_day
    status: str              # VORTEX_FLOW | DRIFT_DEBT | FIXED_POINT


# ── SAGCO epoch ──────────────────────────────────────────────────────────────

# The SAGCO vortex genesis tick — anchored to the date vortex_369 was proven
SAGCO_EPOCH_GREGORIAN = (2025, 1, 1)   # sovereign start: 2025-01-01
SAGCO_EPOCH_JDN = gregorian_to_jdn(*SAGCO_EPOCH_GREGORIAN)

BAND_MONTHS = [
    (1, "delta"),
    (2, "theta"),
    (3, "alpha"),
    (4, "beta"),
    (5, "high_beta"),
    (6, "gamma"),
]

MUMIAH_HZ = 555.0  # closing element, position 72, DR(555)=6


# ── Conversion functions ──────────────────────────────────────────────────────

def today_jdn() -> int:
    t = date.today()
    return gregorian_to_jdn(t.year, t.month, t.day)


def jdn_to_hebrew(jdn: int) -> tuple[int, int, int]:
    """Approximate JDN → Hebrew calendar (Gregorian proleptic approximation)."""
    elapsed = jdn - EPOCH_JDN["hebrew"]
    year = int(elapsed / 365.2468) + 1
    rem = elapsed - int((year - 1) * 365.2468)
    month = max(1, min(13, 1 + rem // 30))
    day = max(1, rem % 30 + 1)
    return year, int(month), int(day)


def jdn_to_islamic(jdn: int) -> tuple[int, int, int]:
    """JDN → Islamic Hijri calendar (Kuwaiti algorithm)."""
    l = jdn - 1948440 + 10632
    n = (l - 1) // 10631
    l = l - 10631 * n + 354
    j = (10985 - l) // 5320 * 74 + (l * 50) // 1765
    l = l - (j * 1765) // 50 + 29
    month = l // 29
    day = l - 29 * month + 1
    year = 30 * n + j - 30
    # Clamp to valid ranges
    month = max(1, min(12, month))
    day   = max(1, min(30, day))
    return int(year), int(month), int(day)


def jdn_to_mayan(jdn: int) -> tuple[int, int, int, int, int]:
    """JDN → Mayan Long Count (baktun, katun, tun, uinal, kin)."""
    elapsed = jdn - EPOCH_JDN["mayan"]
    baktun = elapsed // 144000
    rem = elapsed % 144000
    katun = rem // 7200
    rem = rem % 7200
    tun = rem // 360
    rem = rem % 360
    uinal = rem // 20
    kin = rem % 20
    return baktun, katun, tun, uinal, kin


def jdn_to_persian(jdn: int) -> tuple[int, int, int]:
    """JDN → Persian Solar Hijri (Solar calendar)."""
    elapsed = jdn - EPOCH_JDN["persian"]
    year = int(elapsed / 365.24219) + 1
    rem = elapsed - int((year - 1) * 365.24219)
    month = max(1, min(12, 1 + rem // 30))
    day = max(1, rem % 30 + 1)
    return year, int(month), int(day)


def jdn_to_ethiopian(jdn: int) -> tuple[int, int, int]:
    """JDN → Ethiopian calendar."""
    elapsed = jdn - EPOCH_JDN["ethiopian"]
    year = int(elapsed / 365.25) + 1
    rem = elapsed - int((year - 1) * 365.25)
    month = max(1, min(13, 1 + rem // 30))
    day = max(1, rem % 30 + 1)
    return year, int(month), int(day)


def jdn_to_roman_auc(jdn: int) -> int:
    """JDN → Roman AUC year."""
    elapsed = jdn - EPOCH_JDN["roman_auc"]
    return max(1, int(elapsed / 365.25) + 1)


def jdn_to_kali_yuga(jdn: int) -> int:
    """JDN → Kali Yuga year."""
    elapsed = jdn - EPOCH_JDN["kali_yuga"]
    return max(1, int(elapsed / 365.25636) + 1)


def jdn_to_chinese_cycle(jdn: int) -> tuple[int, int]:
    """JDN → Chinese 60-year cycle (cycle_num, year_in_cycle)."""
    elapsed = jdn - EPOCH_JDN["chinese"]
    total_years = int(elapsed / 365.2425)
    cycle = total_years // 60 + 1
    year_in_cycle = total_years % 60 + 1
    return cycle, year_in_cycle


CHINESE_STEMS = ["Jia", "Yi", "Bing", "Ding", "Wu", "Ji", "Geng", "Xin", "Ren", "Gui"]
CHINESE_BRANCHES = ["Zi", "Chou", "Yin", "Mao", "Chen", "Si", "Wu", "Wei", "Shen", "You", "Xu", "Hai"]
CHINESE_ANIMALS = ["Rat","Ox","Tiger","Rabbit","Dragon","Snake","Horse","Goat","Monkey","Rooster","Dog","Pig"]


# ── Calendar date builder ─────────────────────────────────────────────────────

def calendar_date(name: str, jdn: int) -> CalendarDate:
    elapsed = jdn - EPOCH_JDN[name]
    elapsed_years = elapsed / YEAR_LENGTH[name]

    if name == "gregorian":
        y, m, d = jdn_to_gregorian(jdn)
        label = f"{y:04d}-{m:02d}-{d:02d}"
    elif name == "julian":
        # Julian calendar: subtract correction days
        j_jdn = jdn - 13  # rough modern correction (~2026)
        y, m, d = jdn_to_gregorian(j_jdn)
        label = f"{y:04d}-{m:02d}-{d:02d} OS"
    elif name == "hebrew":
        y, m, d = jdn_to_hebrew(jdn)
        label = f"{y} AM, month {m}, day {d}"
    elif name == "islamic":
        y, m, d = jdn_to_islamic(jdn)
        label = f"{y} AH, month {m}, day {d}"
    elif name == "mayan":
        bk, ka, tu, ui, ki = jdn_to_mayan(jdn)
        y, m, d = bk, ka, tu
        label = f"{bk}.{ka}.{tu}.{ui}.{ki}"
    elif name == "kali_yuga":
        y = jdn_to_kali_yuga(jdn)
        m, d = 1, 1
        label = f"KY {y}"
    elif name == "roman_auc":
        y = jdn_to_roman_auc(jdn)
        m, d = 1, 1
        label = f"AUC {y}"
    elif name == "persian":
        y, m, d = jdn_to_persian(jdn)
        label = f"{y} SH, month {m}, day {d}"
    elif name == "ethiopian":
        y, m, d = jdn_to_ethiopian(jdn)
        label = f"{y} EE, month {m}, day {d}"
    elif name == "chinese":
        cycle, yr = jdn_to_chinese_cycle(jdn)
        y, m, d = cycle, yr, 1
        stem = CHINESE_STEMS[(yr - 1) % 10]
        branch = CHINESE_BRANCHES[(yr - 1) % 12]
        animal = CHINESE_ANIMALS[(yr - 1) % 12]
        label = f"Cycle {cycle}, Year {yr} ({stem}-{branch}, {animal})"
    else:
        y, m, d = 0, 0, 0
        label = f"Unknown calendar: {name}"

    return CalendarDate(
        calendar=name,
        year=int(y), month=int(m), day=int(d),
        label=label,
        jdn=jdn,
        elapsed_days=elapsed,
        elapsed_years=elapsed_years,
    )


# ── Eru burn rate ─────────────────────────────────────────────────────────────

def eru_burn_rate(calendar_name: str, jdn: int) -> EruBurnRate:
    elapsed = jdn - EPOCH_JDN[calendar_name]
    era = ERA_LENGTH_DAYS[calendar_name]
    fraction = elapsed / era
    remaining = max(0, era - elapsed)
    dr = digital_root(int(fraction * 100) % 100 or 9)
    track = classify_vortex(dr)
    return EruBurnRate(
        calendar=calendar_name,
        elapsed_days=elapsed,
        era_length_days=era,
        burn_fraction=fraction,
        burn_percent=fraction * 100,
        remaining_days=remaining,
        vortex_track=track,
    )


# ── Cross-calendar comparison ─────────────────────────────────────────────────

def compare_all(jdn: Optional[int] = None) -> list[CalendarComparison]:
    if jdn is None:
        jdn = today_jdn()

    results = []
    for name in EPOCH_JDN:
        elapsed = jdn - EPOCH_JDN[name]
        elapsed_years = elapsed / YEAR_LENGTH[name]
        actual_year = int(elapsed_years) + 1

        # expected: pure math says how many days should have passed by this calendar year
        expected_elapsed = (actual_year - 1) * YEAR_LENGTH[name]
        variance_days = elapsed - expected_elapsed

        # drift rate: variance_days per 36524.25 days (century)
        if elapsed > 0:
            drift_rate = variance_days / elapsed * 36524.25
        else:
            drift_rate = 0.0

        eru = eru_burn_rate(name, jdn)
        cd  = calendar_date(name, jdn)

        results.append(CalendarComparison(
            calendar=name,
            today_jdn=jdn,
            elapsed_days=elapsed,
            elapsed_years=elapsed_years,
            expected_year=elapsed_years + 1,
            actual_year=actual_year,
            variance_days=variance_days,
            drift_rate=drift_rate,
            eru=eru,
            date=cd,
        ))

    return results


# ── Primameria sovereign calendar ─────────────────────────────────────────────

def primameria_day(jdn: Optional[int] = None) -> PrimameriaDay:
    if jdn is None:
        jdn = today_jdn()

    elapsed = jdn - SAGCO_EPOCH_JDN
    sagco_year = elapsed // 365 + 1
    day_of_year = elapsed % 365 + 1     # 1-365

    in_drift = day_of_year > 360

    if in_drift:
        band_idx = 5         # gamma (last band) during drift zone
        day_of_month = day_of_year - 360
    else:
        band_idx = (day_of_year - 1) // 60
        day_of_month = (day_of_year - 1) % 60 + 1

    band_num, band_name = BAND_MONTHS[min(band_idx, 5)]

    vd = digital_root(day_of_year)
    vortex_track = classify_vortex(vd)

    element_idx = (day_of_year - 1) % 72
    khaos_el = TABLE[element_idx]

    # mumiah phase: position in the 555hz cycle
    mumiah_phase = (day_of_year / 360.0) * 2 * math.pi
    primameria_freq = MUMIAH_HZ + vd * 5.0  # vortex nudge

    comp = complement(vd) if vd in (3, 6, 9) else (9 - vd)

    if vd == 9:
        status = "FIXED_POINT"
    elif in_drift:
        status = "DRIFT_DEBT"
    elif vd in (3, 6):
        status = "VORTEX_FLOW"
    else:
        status = "MAIN_TRACK"

    return PrimameriaDay(
        sagco_year=sagco_year,
        band_month=band_num,
        band_name=band_name,
        day_of_month=day_of_month,
        day_of_year=day_of_year,
        in_drift_zone=in_drift,
        vortex_day=vd,
        vortex_track=vortex_track,
        khaos_element=khaos_el.name,
        khaos_hz=khaos_el.hz,
        mumiah_phase=mumiah_phase,
        primameria_freq=primameria_freq,
        phase_rad=mumiah_phase,
        complement_day=comp,
        status=status,
    )


def today_vortex() -> dict:
    """Quick summary for today in Primameria time."""
    pd = primameria_day()
    y, m, d = jdn_to_gregorian(today_jdn())
    return {
        "date": f"{y:04d}-{m:02d}-{d:02d}",
        "sagco_year": pd.sagco_year,
        "band_month": f"{pd.band_month}-{pd.band_name}",
        "day_of_year": pd.day_of_year,
        "day_vortex": pd.vortex_day,
        "vortex_track": pd.vortex_track,
        "complement": pd.complement_day,
        "khaos_element": pd.khaos_element,
        "khaos_hz": pd.khaos_hz,
        "mumiah_freq": pd.primameria_freq,
        "phase": round(pd.phase_rad, 3),
        "status": pd.status,
        "glyph": f"\U0001F300{pd.vortex_day}" if pd.vortex_day in (3, 6, 9) else f"□{pd.vortex_day}",
    }


# ── Daily Primameria Rite WAV ─────────────────────────────────────────────────

# Vortex track anchor frequencies (from vortex.py WAV encoder)
_TRACK_HZ = {
    "3-track": 300.0,   # Nelchael — 3-track anchor
    "6-track": 360.0,   # Iehuiah  — 6-track anchor (hz DR=9, inverted)
    "9-track": 240.0,   # Haziel   — 9-track anchor (hz DR=6, inverted)
}


def daily_rite_wav(output_path: str, jdn: Optional[int] = None, duration: float = 9.0) -> str:
    """
    Generate the Primameria Daily Rite WAV.

    Layer 1: today's KHAOS element carrier (left = hz, right = hz + beat)
    Layer 2: vortex track anchor frequency blended in
    Layer 3: Mumiah 555hz overlay at Primameria phase angle — faint attractor

    Duration: 9 seconds by default (the fixed-point number).
    """
    import struct
    import wave as _wave

    SAMPLE_RATE = 44100
    pd = primameria_day(jdn)

    # Carrier = today's element
    carrier_hz = float(pd.khaos_hz)
    beat_hz    = 4.0   # default 4hz beat (theta boundary)

    # Track layer
    track_hz = _TRACK_HZ.get(pd.vortex_track, MUMIAH_HZ)

    # Mumiah phase offset converts to a time shift
    mumiah_offset = pd.phase_rad / (2 * math.pi)  # [0,1] fraction of its period

    amp_carrier = 0.45
    amp_track   = 0.25
    amp_mumiah  = 0.15

    n_samples = int(duration * SAMPLE_RATE)
    fade      = int(0.03 * SAMPLE_RATE)
    frames    = []

    for i in range(n_samples):
        t   = i / SAMPLE_RATE

        # Layer 1: binaural carrier
        left_c  = amp_carrier * math.sin(2 * math.pi * carrier_hz * t)
        right_c = amp_carrier * math.sin(2 * math.pi * (carrier_hz + beat_hz) * t)

        # Layer 2: vortex track anchor
        v_track = amp_track * math.sin(2 * math.pi * track_hz * t)

        # Layer 3: Mumiah phase attractor (mono overlay, phase-shifted)
        t_mumiah = t + mumiah_offset / MUMIAH_HZ
        mumiah   = amp_mumiah * math.sin(2 * math.pi * MUMIAH_HZ * t_mumiah)

        left  = left_c  + v_track + mumiah
        right = right_c + v_track + mumiah

        # fade envelope
        fv    = min(1.0, i / fade, (n_samples - i) / fade)
        left  = max(-1.0, min(1.0, left  * fv))
        right = max(-1.0, min(1.0, right * fv))

        frames.append(struct.pack("<h", int(left  * 32767)))
        frames.append(struct.pack("<h", int(right * 32767)))

    with _wave.open(output_path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(b"".join(frames))

    return output_path


# ── Print helpers ─────────────────────────────────────────────────────────────

def print_primameria(pd: Optional[PrimameriaDay] = None) -> None:
    if pd is None:
        pd = primameria_day()

    print("\n  ═══════════════════════════════════════════════════════════════")
    print("  SAGCO PRIMAMERIA CALENDAR  — Prima Materia · Vortex Time")
    print("  ═══════════════════════════════════════════════════════════════")
    print(f"  Sovereign Year  : {pd.sagco_year}")
    print(f"  Band-Month      : {pd.band_month} — {pd.band_name.upper()}")
    print(f"  Day of Month    : {pd.day_of_month:3d} / 60")
    print(f"  Day of Year     : {pd.day_of_year:3d} / 360" + (" [DRIFT ZONE]" if pd.in_drift_zone else ""))
    print(f"  Vortex Day      : {pd.vortex_day}  ({pd.vortex_track})")
    print(f"  Complement      : {pd.complement_day}  (day + complement = 9)")
    print(f"  KHAOS Element   : {pd.khaos_element}  @ {pd.khaos_hz} Hz")
    print(f"  Mumiah Phase    : {pd.mumiah_phase:.4f} rad  ({pd.mumiah_phase * 180 / math.pi:.1f}°)")
    print(f"  Primameria Freq : {pd.primameria_freq:.1f} Hz  (555 + {pd.vortex_day}×5)")
    print(f"  Status          : {pd.status}")
    print("  ═══════════════════════════════════════════════════════════════")


def print_calendar_table(comparisons: Optional[list[CalendarComparison]] = None) -> None:
    if comparisons is None:
        comparisons = compare_all()

    jdn = comparisons[0].today_jdn
    y, m, d = jdn_to_gregorian(jdn)

    print(f"\n  ══════════════════════════════════════════════════════════════════════")
    print(f"  SAGCO CALENDAR COMPARISON — {y:04d}-{m:02d}-{d:02d}  (JDN {jdn})")
    print(f"  ══════════════════════════════════════════════════════════════════════")
    print(f"  {'Calendar':<14}  {'Date Label':<35}  {'Elapsed':<9}  {'Variance':<10}  {'Eru%':<8}  {'Track'}")
    print(f"  {'─'*14}  {'─'*35}  {'─'*9}  {'─'*10}  {'─'*8}  {'─'*12}")

    for c in comparisons:
        var_str = f"{c.variance_days:+.1f}d"
        eru_str = f"{c.eru.burn_percent:.4f}%"
        print(f"  {c.calendar:<14}  {c.date.label:<35}  {c.elapsed_days:<9d}  {var_str:<10}  {eru_str:<8}  {c.eru.vortex_track}")

    print(f"  ══════════════════════════════════════════════════════════════════════")


def print_eru_report(comparisons: Optional[list[CalendarComparison]] = None) -> None:
    if comparisons is None:
        comparisons = compare_all()

    print("\n  ─── ERU BURN RATE REPORT ───────────────────────────────────────────")
    print(f"  {'Calendar':<14}  {'Elapsed Days':<14}  {'Era Length':<14}  {'Burn%':<12}  {'Remaining':<14}  {'Vortex'}")
    print(f"  {'─'*14}  {'─'*14}  {'─'*14}  {'─'*12}  {'─'*14}  {'─'*10}")
    for c in comparisons:
        e = c.eru
        print(f"  {e.calendar:<14}  {e.elapsed_days:<14,d}  {e.era_length_days:<14,d}  "
              f"{e.burn_percent:<12.6f}  {e.remaining_days:<14,d}  {e.vortex_track}")
    print(f"  ──────────────────────────────────────────────────────────────────")


def print_full_report() -> None:
    jdn = today_jdn()
    comparisons = compare_all(jdn)
    pd = primameria_day(jdn)

    print_primameria(pd)
    print_calendar_table(comparisons)
    print_eru_report(comparisons)


if __name__ == "__main__":
    print_full_report()
