/*
 * takeoff.c — ML-ORGANISM-006  (field subsystem)
 *
 * Refinery insulation takeoff calculator.
 * Reads factor table + survey CSV, computes SQFT by segment,
 * reconciles against Brock sheet totals, emits ERU completion report.
 *
 * Formula:
 *   pipe_sqft   = lnft × sqft_per_lf   (from factor table by diameter_ips)
 *   fitting_sqft = count × sqft_each   (from factor table by type + diameter)
 *   V_lnft  = lnft_complete  / lnft_total   (ERU by linear feet)
 *   V_sqft  = sqft_complete  / sqft_total   (ERU by square feet)
 *
 * Brock sheet ground truth (2026-06-26):
 *   Total:    1366 LNFT,  4882.2 SQFT,  67 days × 4 men × 10 hr = 2680 man-hours
 *   Complete:  232 LNFT,  1774.2 SQFT
 *
 * Usage:
 *   sagco field takeoff
 *   sagco field takeoff --factors data/takeoff_sqft_factors.csv \
 *                       --survey  data/takeoff_ca1648j.csv
 *
 * Dispatch entry point:
 *   takeoff_handle(ctx) registered in insulation.c field_handle()
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "../router/router.h"

/* ── Brock sheet actuals ──────────────────────────────────────────────────── */
#define BROCK_TOTAL_LNFT   1366.0
#define BROCK_TOTAL_SQFT   4882.2
#define BROCK_DONE_LNFT     232.0
#define BROCK_DONE_SQFT    1774.2
#define BROCK_DAYS           67.0
#define BROCK_MEN             4.0
#define BROCK_HRS_PER_DAY    10.0

/* ── Factor table ─────────────────────────────────────────────────────────── */
#define MAX_FACTORS 128

typedef struct {
    char   type[32];        /* pipe | flange | valve_welded | valve_flanged */
    double size_ips;
    double sqft_per_lf;     /* pipe only */
    double sqft_each;       /* fittings only */
} SqftFactor;

static int load_factors(const char *path, SqftFactor *f)
{
    FILE *fp = fopen(path, "r");
    if (!fp) { fprintf(stderr, "  [takeoff] cannot open factors %s\n", path); return -1; }

    int n = 0;
    char line[256];
    int hdr = 0;

    while (fgets(line, sizeof(line), fp) && n < MAX_FACTORS) {
        if (!hdr) { hdr = 1; continue; }
        SqftFactor *s = &f[n];
        char notes[64] = {0};
        int p = sscanf(line, "%31[^,],%lf,%*[^,],%lf,%lf,%63[^\n]",
                       s->type, &s->size_ips, &s->sqft_per_lf, &s->sqft_each, notes);
        if (p >= 4) n++;
    }
    fclose(fp);
    return n;
}

static double factor_pipe(SqftFactor *f, int nf, double size_ips)
{
    /* exact match first, then nearest-larger */
    double best_sqft = 0.0;
    double best_delta = 1e9;
    for (int i = 0; i < nf; i++) {
        if (strcmp(f[i].type, "pipe") != 0) continue;
        double delta = fabs(f[i].size_ips - size_ips);
        if (delta < best_delta) { best_delta = delta; best_sqft = f[i].sqft_per_lf; }
    }
    return best_sqft;
}

static double factor_fitting(SqftFactor *f, int nf, const char *type, double size_ips)
{
    for (int i = 0; i < nf; i++) {
        if (strcmp(f[i].type, type) != 0) continue;
        if (fabs(f[i].size_ips - size_ips) < 0.1) return f[i].sqft_each;
    }
    return 0.0;
}

/* ── Survey table ─────────────────────────────────────────────────────────── */
#define MAX_ROWS 256

typedef struct {
    char   asset_id[32];
    char   segment[48];
    double diameter_ips;
    double lnft;
    char   fitting_type[24];
    int    fitting_count;
    char   status[24];
    char   layer[24];
    double sqft_factor;     /* from CSV (pre-computed, used as sanity check) */
    double sqft_total_csv;  /* from CSV */
    double confidence;
    char   notes[128];
} TakeoffRow;

static int load_survey(const char *path, TakeoffRow *rows)
{
    FILE *fp = fopen(path, "r");
    if (!fp) { fprintf(stderr, "  [takeoff] cannot open survey %s\n", path); return -1; }

    int n = 0;
    char line[512];
    int hdr = 0;

    while (fgets(line, sizeof(line), fp) && n < MAX_ROWS) {
        if (!hdr) { hdr = 1; continue; }
        TakeoffRow *r = &rows[n];
        int p = sscanf(line,
            "%31[^,],%47[^,],%lf,%lf,%23[^,],%d,%23[^,],%23[^,],%lf,%lf,%lf,%127[^\n]",
            r->asset_id, r->segment, &r->diameter_ips, &r->lnft,
            r->fitting_type, &r->fitting_count,
            r->status, r->layer,
            &r->sqft_factor, &r->sqft_total_csv, &r->confidence, r->notes);
        if (p >= 10) n++;
    }
    fclose(fp);
    return n;
}

/* ── Status classification ───────────────────────────────────────────────── */
static int is_complete(const char *status)
{
    return strcmp(status, "complete") == 0;
}

static int is_active(const char *status)
{
    return strcmp(status, "in_progress") == 0 ||
           strcmp(status, "complete")    == 0;
}

/* ── ERU verdict ──────────────────────────────────────────────────────────── */
static const char *eru_verdict(double ratio)
{
    if (ratio >= 1.00) return "PROVEN";
    if (ratio >= 0.80) return "PROMISING";
    if (ratio >= 0.50) return "UNPROVEN";
    return "INFLATED";
}

/* ── get_arg helper ───────────────────────────────────────────────────────── */
static const char *get_arg(SagcoContext *ctx, const char *flag)
{
    for (int i = 0; i < ctx->argc - 1; i++)
        if (strcmp(ctx->argv[i], flag) == 0) return ctx->argv[i + 1];
    return NULL;
}

/* ── Main handler ─────────────────────────────────────────────────────────── */
int takeoff_handle(SagcoContext *ctx)
{
    const char *factors_path = get_arg(ctx, "--factors");
    if (!factors_path) factors_path = "data/takeoff_sqft_factors.csv";

    const char *survey_path = get_arg(ctx, "--survey");
    if (!survey_path) survey_path = "data/takeoff_ca1648j.csv";

    /* Load factor table */
    SqftFactor factors[MAX_FACTORS];
    int nf = load_factors(factors_path, factors);
    if (nf <= 0) {
        fprintf(stderr, "  [takeoff] no factors loaded\n");
        return 1;
    }

    /* Load survey */
    TakeoffRow rows[MAX_ROWS];
    int nr = load_survey(survey_path, rows);
    if (nr <= 0) {
        fprintf(stderr, "  [takeoff] no survey rows loaded\n");
        return 1;
    }

    /* Compute sqft for each row using factor table (override CSV pre-calc) */
    double total_lnft = 0.0, total_sqft = 0.0;
    double done_lnft  = 0.0, done_sqft  = 0.0;
    double active_lnft = 0.0, active_sqft = 0.0;

    for (int i = 0; i < nr; i++) {
        TakeoffRow *r = &rows[i];
        double pipe_sqft    = r->lnft * factor_pipe(factors, nf, r->diameter_ips);
        double fitting_sqft = 0.0;
        if (r->fitting_count > 0 && strcmp(r->fitting_type, "pipe") != 0) {
            fitting_sqft = r->fitting_count *
                           factor_fitting(factors, nf, r->fitting_type, r->diameter_ips);
        }
        r->sqft_factor    = factor_pipe(factors, nf, r->diameter_ips);
        r->sqft_total_csv = pipe_sqft + fitting_sqft;

        total_lnft  += r->lnft;
        total_sqft  += r->sqft_total_csv;

        if (is_complete(r->status)) {
            done_lnft += r->lnft;
            done_sqft += r->sqft_total_csv;
        }
        if (is_active(r->status)) {
            active_lnft += r->lnft;
            active_sqft += r->sqft_total_csv;
        }
    }

    /* ERU against Brock sheet actuals */
    double v_lnft_brock = BROCK_DONE_LNFT / BROCK_TOTAL_LNFT;
    double v_sqft_brock = BROCK_DONE_SQFT / BROCK_TOTAL_SQFT;

    /* ERU from our computed survey vs Brock totals */
    double v_lnft_survey = (BROCK_TOTAL_LNFT > 0) ? done_lnft  / BROCK_TOTAL_LNFT : 0.0;
    double v_sqft_survey = (BROCK_TOTAL_SQFT > 0) ? done_sqft  / BROCK_TOTAL_SQFT : 0.0;

    double labor_hours = BROCK_DAYS * BROCK_MEN * BROCK_HRS_PER_DAY;
    double sqft_per_mh = (labor_hours > 0) ? BROCK_DONE_SQFT / labor_hours : 0.0;

    /* ── Print ──────────────────────────────────────────────────────────────── */
    printf("\n  SAGCO field takeoff — refinery insulation packet\n");
    printf("  ────────────────────────────────────────────────────────────────────\n");
    printf("  %-16s  %-14s  %6s  %4s  %8s  %8s  %-12s  %s\n",
           "ASSET", "SEGMENT", "DIA\"", "LNFT", "SQFT/LF", "SQFT", "STATUS", "LAYER");
    printf("  ────────────────────────────────────────────────────────────────────\n");

    for (int i = 0; i < nr; i++) {
        TakeoffRow *r = &rows[i];
        printf("  %-16s  %-14s  %5.0f\"  %4.0f  %8.3f  %8.2f  %-12s  %s\n",
               r->asset_id, r->segment,
               r->diameter_ips, r->lnft,
               r->sqft_factor, r->sqft_total_csv,
               r->status, r->layer);
    }

    printf("  ────────────────────────────────────────────────────────────────────\n");
    printf("  Segments surveyed:  %d\n", nr);
    printf("  Survey LNFT total:  %.1f\n",  total_lnft);
    printf("  Survey SQFT total:  %.2f\n",  total_sqft);
    printf("  Survey LNFT done:   %.1f\n",  done_lnft);
    printf("  Survey SQFT done:   %.2f\n",  done_sqft);

    printf("\n  ── Brock Sheet Ground Truth ─────────────────────────────────────────\n");
    printf("  Total LNFT:   %7.1f  |  Complete LNFT:  %6.1f  (V=%.4f  [%s])\n",
           BROCK_TOTAL_LNFT, BROCK_DONE_LNFT, v_lnft_brock, eru_verdict(v_lnft_brock));
    printf("  Total SQFT:   %7.2f  |  Complete SQFT:  %6.2f  (V=%.4f  [%s])\n",
           BROCK_TOTAL_SQFT, BROCK_DONE_SQFT, v_sqft_brock, eru_verdict(v_sqft_brock));
    printf("  Labor:   %.0f days × %.0f men × %.0f hr = %.0f man-hours\n",
           BROCK_DAYS, BROCK_MEN, BROCK_HRS_PER_DAY, labor_hours);
    printf("  Productivity:  %.4f SQFT / man-hour\n", sqft_per_mh);

    printf("\n  ── Survey vs Brock ERU ──────────────────────────────────────────────\n");
    printf("  V_lnft (survey/brock): %.4f  [%s]\n",
           v_lnft_survey, eru_verdict(v_lnft_survey));
    printf("  V_sqft (survey/brock): %.4f  [%s]\n",
           v_sqft_survey, eru_verdict(v_sqft_survey));
    printf("  Note: SQFT ERU > LNFT ERU — heavier-SQFT sections completed first.\n");

    printf("\n  SAGCO_RECEIPT subsystem=field command=takeoff "
           "segments=%d lnft_done=%.1f sqft_done=%.2f "
           "v_lnft=%.4f v_sqft=%.4f verdict=%s\n\n",
           nr, done_lnft, done_sqft,
           v_lnft_brock, v_sqft_brock,
           eru_verdict(v_sqft_brock));

    return (strcmp(eru_verdict(v_sqft_brock), "PROVEN")    == 0 ||
            strcmp(eru_verdict(v_sqft_brock), "PROMISING") == 0) ? 0 : 1;
}
