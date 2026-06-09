"""
Wafer: primameria_calendar
Tests the SAGCO Primameria Calendar system.
JDN-based cross-calendar engine, eru burn rate, and sovereign Primameria time.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sagco_true.khaos.calendar import (
    gregorian_to_jdn, jdn_to_gregorian,
    jdn_to_islamic, jdn_to_mayan, jdn_to_hebrew,
    jdn_to_persian, jdn_to_ethiopian, jdn_to_roman_auc, jdn_to_kali_yuga,
    jdn_to_chinese_cycle,
    calendar_date, eru_burn_rate, compare_all,
    primameria_day, today_vortex,
    EPOCH_JDN, SAGCO_EPOCH_JDN, MUMIAH_HZ,
    print_full_report,
)
from sagco_true.khaos.vortex import digital_root

PASS, FAIL = [], []

def check(name, result, expected=True):
    ok = result == expected
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    (PASS if ok else FAIL).append(name)

# ── 1. JDN round-trip ────────────────────────────────────────────────────────
check("JDN: gregorian_to_jdn(2026,6,9) == 2461201",
      gregorian_to_jdn(2026, 6, 9) == 2461201)
check("JDN: jdn_to_gregorian(2461201) == (2026,6,9)",
      jdn_to_gregorian(2461201) == (2026, 6, 9))
check("JDN: J2000 epoch = 2451545",
      gregorian_to_jdn(2000, 1, 1) == 2451545)
check("JDN: days since J2000 = 9656",
      gregorian_to_jdn(2026, 6, 9) - 2451545 == 9656)
check("JDN: gregorian_to_jdn(1,1,1) positive",
      gregorian_to_jdn(1, 1, 1) > 0)

# ── 2. Epoch anchors ─────────────────────────────────────────────────────────
check("Epoch: Hebrew epoch JDN == 347998",   EPOCH_JDN["hebrew"]    == 347998)
check("Epoch: Islamic epoch JDN == 1948439", EPOCH_JDN["islamic"]   == 1948439)
check("Epoch: Mayan epoch JDN == 584283",    EPOCH_JDN["mayan"]     == 584283)
check("Epoch: Kali Yuga JDN == 588466",      EPOCH_JDN["kali_yuga"] == 588466)
check("Epoch: Roman AUC JDN == 1446109",     EPOCH_JDN["roman_auc"] == 1446109)

# ── 3. Cross-calendar conversions ────────────────────────────────────────────
JDN_TEST = gregorian_to_jdn(2026, 6, 9)

hy, hm, hd = jdn_to_hebrew(JDN_TEST)
check("Hebrew: year > 5000",         hy > 5000)
check("Hebrew: month in [1,13]",     1 <= hm <= 13)
check("Hebrew: day in [1,30]",       1 <= hd <= 30)

iy, im, id_ = jdn_to_islamic(JDN_TEST)
check("Islamic: year > 1400",        iy > 1400)
check("Islamic: month in [1,12]",    1 <= im <= 12)
check("Islamic: day in [1,30]",      1 <= id_ <= 30)

bk, ka, tu, ui, ki = jdn_to_mayan(JDN_TEST)
check("Mayan: baktun >= 13",         bk >= 13)
check("Mayan: kin in [0,19]",        0 <= ki <= 19)
check("Mayan: uinal in [0,17]",      0 <= ui <= 17)

ry = jdn_to_roman_auc(JDN_TEST)
check("Roman AUC: year > 2700",      ry > 2700)

ky = jdn_to_kali_yuga(JDN_TEST)
check("Kali Yuga: year > 5000",      ky > 5000)

cycle, yr_in = jdn_to_chinese_cycle(JDN_TEST)
check("Chinese: cycle >= 78",        cycle >= 78)
check("Chinese: year in cycle 1-60", 1 <= yr_in <= 60)

py, pm, pd_ = jdn_to_persian(JDN_TEST)
check("Persian: year > 1400",        py > 1400)
check("Persian: month in [1,12]",    1 <= pm <= 12)

ey, em, ed_ = jdn_to_ethiopian(JDN_TEST)
check("Ethiopian: year > 2000",      ey > 2000)
check("Ethiopian: month in [1,13]",  1 <= em <= 13)

# ── 4. Calendar date objects ──────────────────────────────────────────────────
cd_greg = calendar_date("gregorian", JDN_TEST)
check("CalendarDate: gregorian label has 2026",   "2026" in cd_greg.label)
check("CalendarDate: gregorian jdn correct",       cd_greg.jdn == JDN_TEST)
check("CalendarDate: gregorian elapsed > 700000",  cd_greg.elapsed_days > 700000)

cd_mayan = calendar_date("mayan", JDN_TEST)
check("CalendarDate: mayan label has dots",        "." in cd_mayan.label)

cd_hebrew = calendar_date("hebrew", JDN_TEST)
check("CalendarDate: hebrew label has AM",         "AM" in cd_hebrew.label)

# ── 5. Eru burn rate ─────────────────────────────────────────────────────────
eru_greg = eru_burn_rate("gregorian", JDN_TEST)
check("Eru: gregorian burn > 0",         eru_greg.burn_fraction > 0)
check("Eru: gregorian burn < 1",         eru_greg.burn_fraction < 1)
check("Eru: gregorian burn_percent > 0", eru_greg.burn_percent > 0)

eru_mayan = eru_burn_rate("mayan", JDN_TEST)
check("Eru: mayan elapsed == JDN_TEST - 584283",
      eru_mayan.elapsed_days == JDN_TEST - 584283)
check("Eru: mayan burn >= 1.0 (past great cycle)", eru_mayan.burn_fraction >= 1.0)

eru_ky = eru_burn_rate("kali_yuga", JDN_TEST)
check("Eru: kali_yuga burn < 0.01 (vast epoch)",  eru_ky.burn_fraction < 0.01)

# ── 6. Compare all ───────────────────────────────────────────────────────────
comparisons = compare_all(JDN_TEST)
check("Compare: 10 calendars returned",  len(comparisons) == 10)
names = {c.calendar for c in comparisons}
for cal in ["gregorian", "islamic", "hebrew", "mayan", "kali_yuga"]:
    check(f"Compare: {cal} present",    cal in names)
for c in comparisons:
    check(f"Compare: {c.calendar} elapsed > 0", c.elapsed_days > 0)

# ── 7. Primameria sovereign calendar ─────────────────────────────────────────
pd = primameria_day(JDN_TEST)
check("Primameria: sagco_year >= 1",          pd.sagco_year >= 1)
check("Primameria: band_month in [1,6]",      1 <= pd.band_month <= 6)
check("Primameria: day_of_month in [1,60]",   1 <= pd.day_of_month <= 60)
check("Primameria: day_of_year in [1,365]",   1 <= pd.day_of_year <= 365)
check("Primameria: vortex_day in [1,9]",      1 <= pd.vortex_day <= 9)
check("Primameria: khaos_element non-empty",  len(pd.khaos_element) > 0)
check("Primameria: khaos_hz > 0",             pd.khaos_hz > 0)
check("Primameria: phase_rad in [0, 2π]",     0 <= pd.phase_rad <= 2 * 3.14159 + 0.01)
check("Primameria: mumiah_freq >= 555",        pd.primameria_freq >= 555.0)
check("Primameria: status non-empty",          len(pd.status) > 0)

# ── 8. Vortex-calendar invariants ────────────────────────────────────────────
# DR(360) = 9 — the year closes at 9
check("Invariant: DR(360) == 9",     digital_root(360) == 9)
# DR(60) = 6 — each month
check("Invariant: DR(60) == 6",      digital_root(60) == 6)
# DR(6 months) = 6
check("Invariant: DR(6) == 6",       digital_root(6) == 6)
# Mumiah hz
check("Invariant: MUMIAH_HZ == 555", MUMIAH_HZ == 555.0)
# DR(555) = 6 — Mumiah closes the 9-track (inverted)
check("Invariant: DR(555) == 6",     digital_root(555) == 6)
# 6 × 60 = 360
check("Invariant: 6*60 == 360",      6 * 60 == 360)
# DR(72) = 9 — the whole KHAOS table
check("Invariant: DR(72) == 9",      digital_root(72) == 9)

# ── 9. Today vortex quick report ─────────────────────────────────────────────
tv = today_vortex()
check("TodayVortex: date present",         "date" in tv)
check("TodayVortex: vortex_track present", "vortex_track" in tv)
check("TodayVortex: status present",       "status" in tv)
check("TodayVortex: mumiah_freq >= 555",   tv["mumiah_freq"] >= 555.0)

# ── Print full report ─────────────────────────────────────────────────────────
print_full_report()

# ── Summary ───────────────────────────────────────────────────────────────────
total = len(PASS) + len(FAIL)
print(f"\n  {len(PASS)}/{total} passed")
if FAIL:
    print(f"  FAILED: {FAIL}")
    print("  STATUS: NEEDS_HEALING")
    sys.exit(1)
else:
    print("  STATUS: PRIMAMERIA_SOVEREIGN")
    sys.exit(0)
