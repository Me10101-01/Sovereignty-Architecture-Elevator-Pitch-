/*
 * exchanger_locator.c  — ML-ORGANISM-005
 *
 * The insight: a compass that fails near industrial equipment is not broken.
 * It is reading the equipment's unique electromagnetic fingerprint.
 *
 * Algorithm:
 *   1. Collect N compass readings at one GPS anchor (same lat/lon)
 *   2. Compute: mean_µT, range_µT, heading_spread_deg
 *   3. Compare against asset_fingerprints.json database
 *   4. Score with ERU: V = A / E (matched_features / total_features)
 *   5. Emit: candidate asset_id + confidence + verdict
 *
 * ERU thresholds:
 *   PROVEN    ≥ 1.00  (all fingerprint features match within tolerance)
 *   PROMISING ≥ 0.50  (majority match)
 *   UNPROVEN  ≥ 0.01  (partial match)
 *   INFLATED  < 0.01  (no match)
 *
 * Usage:
 *   exchanger_locator <readings.csv> <fingerprints.json>
 *
 * Validated against: PO-HDRFE-1B  (LyondellBasell, 2026-06-26)
 *   readings=9  mean=58.56µT  range=66.0µT  spread=316°  → MATCH confidence=1.00
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "exchanger_locator.h"

/* ── Tolerances for fingerprint matching ────────────────────────────────────── */
#define TOL_MEAN_UT      10.0   /* ±10 µT on mean field              */
#define TOL_RANGE_UT     15.0   /* ±15 µT on field range             */
#define TOL_SPREAD_DEG   30.0   /* ±30° on heading spread            */
#define MIN_READINGS      3     /* refuse to match on fewer than 3   */

/* ── ERU verdicts ────────────────────────────────────────────────────────────── */
static const char *eru_verdict(double ratio)
{
    if (ratio >= 1.00) return "PROVEN";
    if (ratio >= 0.50) return "PROMISING";
    if (ratio >= 0.01) return "UNPROVEN";
    return "INFLATED";
}

/* ── CSV reader ──────────────────────────────────────────────────────────────── */
int locator_read_csv(const char *path, CompassReadings *out)
{
    FILE *f = fopen(path, "r");
    if (!f) { fprintf(stderr, "  [locator] cannot open %s\n", path); return -1; }

    out->n = 0;
    char line[256];
    int header_skipped = 0;

    while (fgets(line, sizeof(line), f) && out->n < MAX_READINGS) {
        if (!header_skipped) { header_skipped = 1; continue; }   /* skip header row */

        int    seq;
        double lat, lon, alt_ft, heading, field_ut;
        char   cardinal[8], alert[8];

        int parsed = sscanf(line, "%d,%lf,%lf,%lf,%lf,%7[^,],%lf,%7s",
                            &seq, &lat, &lon, &alt_ft,
                            &heading, cardinal, &field_ut, alert);
        if (parsed < 7) continue;

        out->lat       = lat;
        out->lon       = lon;
        out->alt_ft    = alt_ft;
        out->heading[out->n]  = heading;
        out->field_ut[out->n] = field_ut;
        out->n++;
    }
    fclose(f);
    return (out->n > 0) ? 0 : -1;
}

/* ── Statistics ──────────────────────────────────────────────────────────────── */
void locator_compute_stats(const CompassReadings *r, LocationStats *s)
{
    s->n = r->n;
    s->field_min = s->field_max = r->field_ut[0];
    s->heading_min = s->heading_max = r->heading[0];
    double sum = 0.0;

    for (int i = 0; i < r->n; i++) {
        double f = r->field_ut[i];
        double h = r->heading[i];
        sum += f;
        if (f < s->field_min) s->field_min = f;
        if (f > s->field_max) s->field_max = f;
        if (h < s->heading_min) s->heading_min = h;
        if (h > s->heading_max) s->heading_max = h;
    }

    s->field_mean   = sum / r->n;
    s->field_range  = s->field_max - s->field_min;
    s->heading_spread = s->heading_max - s->heading_min;
}

/* ── JSON fingerprint loader (hand-rolled, zero deps) ───────────────────────── */
static double json_read_double(const char *buf, const char *key)
{
    char search[64];
    snprintf(search, sizeof(search), "\"%s\"", key);
    const char *p = strstr(buf, search);
    if (!p) return -9999.0;
    p = strchr(p, ':');
    if (!p) return -9999.0;
    return atof(p + 1);
}

static int json_read_string(const char *buf, const char *key, char *out, int maxlen)
{
    char search[64];
    snprintf(search, sizeof(search), "\"%s\"", key);
    const char *p = strstr(buf, search);
    if (!p) return -1;
    p = strchr(p, ':');
    if (!p) return -1;
    while (*p == ':' || *p == ' ') p++;
    if (*p == '"') p++;
    int i = 0;
    while (*p && *p != '"' && i < maxlen - 1)
        out[i++] = *p++;
    out[i] = '\0';
    return 0;
}

int locator_load_fingerprints(const char *path, AssetFingerprint *fps, int maxfp)
{
    FILE *f = fopen(path, "r");
    if (!f) { fprintf(stderr, "  [locator] cannot open %s\n", path); return -1; }

    fseek(f, 0, SEEK_END);
    long sz = ftell(f);
    rewind(f);

    char *buf = malloc(sz + 1);
    if (!buf) { fclose(f); return -1; }
    if (fread(buf, 1, sz, f) != (size_t)sz) { free(buf); return -1; }
    buf[sz] = '\0';
    fclose(f);

    int count = 0;
    const char *p = buf;

    while (count < maxfp) {
        /* Find next asset_id key to start a fingerprint block */
        const char *asset_start = strstr(p, "\"asset_id\"");
        if (!asset_start) break;

        /* Find the { before asset_id (within 256 chars back) */
        const char *block = asset_start;
        while (block > buf && *block != '{') block--;

        /* Find the matching closing } */
        const char *end = asset_start;
        int depth = 0;
        const char *scan = block;
        while (*scan) {
            if (*scan == '{') depth++;
            if (*scan == '}') { depth--; if (depth == 0) { end = scan + 1; break; } }
            scan++;
        }

        /* Copy block into a local buffer for parsing */
        int blen = (int)(end - block);
        if (blen <= 0 || blen > 4096) { p = asset_start + 1; continue; }

        char *block_buf = malloc(blen + 1);
        if (!block_buf) break;
        memcpy(block_buf, block, blen);
        block_buf[blen] = '\0';

        AssetFingerprint *fp = &fps[count];
        memset(fp, 0, sizeof(*fp));

        json_read_string(block_buf, "asset_id",  fp->asset_id,  sizeof(fp->asset_id));
        json_read_string(block_buf, "asset_type", fp->asset_type, sizeof(fp->asset_type));
        json_read_string(block_buf, "facility",  fp->facility,  sizeof(fp->facility));

        fp->mean_ut    = json_read_double(block_buf, "magnetic_mean_ut");
        fp->range_ut   = json_read_double(block_buf, "magnetic_range_ut");
        fp->spread_deg = json_read_double(block_buf, "heading_spread_deg");
        fp->n_readings = (int)json_read_double(block_buf, "n_readings");

        free(block_buf);

        if (fp->asset_id[0] != '\0') count++;
        p = end;
    }

    free(buf);
    return count;
}

/* ── Matching ────────────────────────────────────────────────────────────────── */
MatchResult locator_match(const LocationStats *s, const AssetFingerprint *fps, int nfp)
{
    MatchResult best;
    memset(&best, 0, sizeof(best));
    best.confidence = -1.0;

    if (s->n < MIN_READINGS) {
        strncpy(best.verdict, "NO_DATA", sizeof(best.verdict) - 1);
        return best;
    }

    for (int i = 0; i < nfp; i++) {
        const AssetFingerprint *fp = &fps[i];

        /* Score 3 features: mean_µT, range_µT, heading_spread */
        int features_match = 0;
        int features_total = 3;

        if (fabs(s->field_mean   - fp->mean_ut)    <= TOL_MEAN_UT)    features_match++;
        if (fabs(s->field_range  - fp->range_ut)   <= TOL_RANGE_UT)   features_match++;
        if (fabs(s->heading_spread - fp->spread_deg) <= TOL_SPREAD_DEG) features_match++;

        double confidence = (double)features_match / features_total;

        if (confidence > best.confidence) {
            best.confidence = confidence;
            strncpy(best.asset_id,  fp->asset_id,  sizeof(best.asset_id)  - 1);
            strncpy(best.facility,  fp->facility,  sizeof(best.facility)  - 1);
            strncpy(best.verdict, eru_verdict(confidence), sizeof(best.verdict) - 1);
        }
    }

    if (best.confidence < 0) {
        strncpy(best.asset_id, "UNKNOWN", sizeof(best.asset_id) - 1);
        strncpy(best.verdict,  "INFLATED", sizeof(best.verdict) - 1);
        best.confidence = 0.0;
    }

    return best;
}

/* ── Main ────────────────────────────────────────────────────────────────────── */
int main(int argc, char *argv[])
{
    const char *csv_path = (argc >= 2) ? argv[1] : "data/sample_readings.csv";
    const char *fp_path  = (argc >= 3) ? argv[2] : "data/asset_fingerprints.json";

    printf("\n  SAGCO exchanger_locator — ML-ORGANISM-005\n");
    printf("  ─────────────────────────────────────────\n");
    printf("  readings : %s\n", csv_path);
    printf("  database : %s\n\n", fp_path);

    /* Load readings */
    CompassReadings readings;
    memset(&readings, 0, sizeof(readings));
    if (locator_read_csv(csv_path, &readings) != 0) {
        fprintf(stderr, "  [locator] failed to load readings\n");
        return 1;
    }

    /* Compute statistics */
    LocationStats stats;
    locator_compute_stats(&readings, &stats);

    printf("  readings      = %d\n", stats.n);
    printf("  GPS anchor    = %.6f N, %.6f W\n", readings.lat, -readings.lon);
    printf("  field_ut      = min %.1f  mean %.2f  max %.1f  range %.1f\n",
           stats.field_min, stats.field_mean, stats.field_max, stats.field_range);
    printf("  heading_deg   = min %.1f  max %.1f  spread %.1f\n",
           stats.heading_min, stats.heading_max, stats.heading_spread);
    printf("\n");

    /* Load fingerprint database */
    AssetFingerprint fps[MAX_FINGERPRINTS];
    int nfp = locator_load_fingerprints(fp_path, fps, MAX_FINGERPRINTS);
    if (nfp <= 0) {
        fprintf(stderr, "  [locator] no fingerprints loaded\n");
        return 1;
    }
    printf("  fingerprints  = %d loaded\n\n", nfp);

    /* Match */
    MatchResult result = locator_match(&stats, fps, nfp);

    printf("  ─────────────────────────────────────────\n");
    printf("  candidate     = %s\n",  result.asset_id);
    printf("  confidence    = %.2f\n", result.confidence);
    printf("  verdict       = %s\n",  result.verdict);
    printf("  ─────────────────────────────────────────\n\n");

    /* Emit SAGCO receipt to stdout for ledger */
    printf("  SAGCO_RECEIPT asset=%s confidence=%.2f eru=%s lat=%.6f lon=%.6f\n\n",
           result.asset_id, result.confidence, result.verdict,
           readings.lat, readings.lon);

    return (strcmp(result.verdict, "PROVEN") == 0 ||
            strcmp(result.verdict, "PROMISING") == 0) ? 0 : 1;
}
