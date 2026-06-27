/*
 * entity_extractor.c — ML-KNOW-001  (knowledge subsystem)
 *
 * Named entity recognition over any text artifact.
 * Scans the lexer token stream for known entity patterns,
 * emits (entity, class, source_artifact) tuples to stdout.
 *
 * Entity classes:
 *   protocol  — RFC\d+, IPv6, SLAAC, RPKI, ROA, BGP, TLS, GPG
 *   crypto    — SHA-256, Ed25519, RSA, BFT, merkle
 *   cloud     — Cloud_Run, GCP, GCS, compute, container, monitoring
 *   field     — GPS, µT, ERU, SQFT, LNFT, insulation, exchanger, flange
 *   finance   — NinjaTrader, dividend, DRIP, ValorYield
 *   physics   — tension, FOS, ohm, resistance, bearing, circumference
 *   software  — Rust, C11, Python, SAGCO, organism, hydra, dispatch
 *   document  — RFC, patent, CN-001, BRICK, JSONL, manifest, receipt
 *
 * Usage:
 *   sagco knowledge entities --input <file>
 *
 * Output (one JSON per line):
 *   {"entity":"RFC4862","class":"protocol","source":"<file>","offset":42}
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <ctype.h>
#include "../router/router.h"
#include "entity_extractor.h"

#define MAX_VOCAB 256

typedef struct {
    char pattern[64];
    char entity_class[16];
    int  is_regex_prefix;   /* 1 = pattern is a prefix, match until non-alnum */
} VocabEntry;

/* ── Domain vocabulary ────────────────────────────────────────────────────── */
static const VocabEntry VOCAB[] = {
    /* protocols */
    {"RFC",         "protocol",  1},  /* RFC + digits = RFC4862, RFC2460 ... */
    {"IPv6",        "protocol",  0},
    {"IPv4",        "protocol",  0},
    {"SLAAC",       "protocol",  0},
    {"RPKI",        "protocol",  0},
    {"ROA",         "protocol",  0},
    {"BGP",         "protocol",  0},
    {"TLS",         "protocol",  0},
    {"GPG",         "protocol",  0},
    {"TCP",         "protocol",  0},
    {"UDP",         "protocol",  0},
    {"OSI",         "protocol",  0},
    {"ARIN",        "protocol",  0},
    {"ASN",         "protocol",  0},
    /* crypto */
    {"SHA-256",     "crypto",    0},
    {"SHA256",      "crypto",    0},
    {"Ed25519",     "crypto",    0},
    {"RSA",         "crypto",    0},
    {"BFT",         "crypto",    0},
    {"merkle",      "crypto",    0},
    {"clearsign",   "crypto",    0},
    /* cloud */
    {"Cloud Run",   "cloud",     0},
    {"GCP",         "cloud",     0},
    {"GCS",         "cloud",     0},
    {"compute",     "cloud",     0},
    {"container",   "cloud",     0},
    {"monitoring",  "cloud",     0},
    {"run.googleapis", "cloud",  0},
    {"Cloud_Run",   "cloud",     0},
    /* field */
    {"GPS",         "field",     0},
    {"ERU",         "field",     0},
    {"SQFT",        "field",     0},
    {"LNFT",        "field",     0},
    {"insulation",  "field",     0},
    {"exchanger",   "field",     0},
    {"flange",      "field",     0},
    {"isometric",   "field",     0},
    {"LyondellBasell", "field",  0},
    {"compass",     "field",     0},
    {"magnetic",    "field",     0},
    /* finance */
    {"NinjaTrader", "finance",   0},
    {"dividend",    "finance",   0},
    {"DRIP",        "finance",   0},
    {"ValorYield",  "finance",   0},
    {"futures",     "finance",   0},
    /* physics */
    {"tension",     "physics",   0},
    {"FOS",         "physics",   0},
    {"ohm",         "physics",   0},
    {"resistance",  "physics",   0},
    {"bearing",     "physics",   0},
    {"circumference","physics",  0},
    {"insulation",  "physics",   0},
    /* software */
    {"SAGCO",       "software",  0},
    {"organism",    "software",  0},
    {"hydra",       "software",  0},
    {"dispatch",    "software",  0},
    {"lexer",       "software",  0},
    {"parser",      "software",  0},
    {"Python",      "software",  0},
    {"Rust",        "software",  0},
    {"C11",         "software",  0},
    /* document */
    {"CN-001",      "document",  0},
    {"BRICK",       "document",  1},  /* BRICK + digits */
    {"JSONL",       "document",  0},
    {"manifest",    "document",  0},
    {"receipt",     "document",  0},
    {"teleportation","document", 0},
    {"provenance",  "document",  0},
};
static const int N_VOCAB = (int)(sizeof(VOCAB) / sizeof(VOCAB[0]));

/* ── Scanner ──────────────────────────────────────────────────────────────── */
int scan_chunk(const char *buf, size_t len,
               const char *source __attribute__((unused)),
               EntityHit *hits, int *n_hits, long base_offset)
{
    for (int v = 0; v < N_VOCAB; v++) {
        const VocabEntry *e = &VOCAB[v];
        size_t plen = strlen(e->pattern);
        for (size_t i = 0; i + plen <= len; i++) {
            if (strncasecmp(buf + i, e->pattern, plen) == 0) {
                /* skip if part of a longer word (prefix match context) */
                if (i > 0 && (isalnum((unsigned char)buf[i-1]) || buf[i-1] == '-'))
                    continue;

                char entity[64] = {0};
                if (e->is_regex_prefix) {
                    /* capture prefix + trailing digits/dots */
                    size_t j = plen;
                    while (j < sizeof(entity) - 1 && i + j < len &&
                           (isdigit((unsigned char)buf[i+j]) || buf[i+j] == '.'))
                        j++;
                    if (j == plen) continue; /* prefix only, no digits → skip */
                    strncpy(entity, buf + i, j < sizeof(entity) ? j : sizeof(entity)-1);
                } else {
                    snprintf(entity, sizeof(entity), "%s", e->pattern);
                }

                /* dedup: skip if same entity already recorded from same source */
                int dup = 0;
                for (int h = 0; h < *n_hits; h++) {
                    if (strcmp(hits[h].entity, entity) == 0 &&
                        strcmp(hits[h].entity_class, e->entity_class) == 0) {
                        dup = 1; break;
                    }
                }
                if (!dup && *n_hits < MAX_ENTITIES) {
                    snprintf(hits[*n_hits].entity,       64, "%s", entity);
                    snprintf(hits[*n_hits].entity_class, 16, "%s", e->entity_class);
                    hits[*n_hits].offset = base_offset + (long)i;
                    (*n_hits)++;
                }
            }
        }
    }
    return *n_hits;
}

/* ── get_arg ──────────────────────────────────────────────────────────────── */
static const char *get_arg(SagcoContext *ctx, const char *flag)
{
    for (int i = 0; i < ctx->argc - 1; i++)
        if (strcmp(ctx->argv[i], flag) == 0) return ctx->argv[i + 1];
    return NULL;
}

/* ── Main handler ─────────────────────────────────────────────────────────── */
int entities_handle(SagcoContext *ctx)
{
    const char *input = get_arg(ctx, "--input");
    if (!input) {
        fprintf(stderr, "  [entities] --input <file> required\n");
        return 1;
    }

    FILE *fp = fopen(input, "r");
    if (!fp) { fprintf(stderr, "  [entities] cannot open %s\n", input); return 1; }

    EntityHit hits[MAX_ENTITIES];
    int n_hits = 0;
    char buf[CHUNK + 64]; /* overlap for cross-boundary matches */
    size_t prev_tail = 0;
    long base_offset = 0;

    while (!feof(fp)) {
        size_t n = fread(buf + prev_tail, 1, CHUNK, fp);
        size_t total = prev_tail + n;
        if (total == 0) break;

        scan_chunk(buf, total, input, hits, &n_hits, base_offset);

        /* keep last 64 bytes for next chunk overlap */
        prev_tail = total > 64 ? 64 : total;
        memmove(buf, buf + total - prev_tail, prev_tail);
        base_offset += (long)(total - prev_tail);
    }
    fclose(fp);

    /* emit JSONL */
    printf("\n  SAGCO knowledge entities — %s\n", input);
    printf("  ──────────────────────────────────────────\n");
    printf("  %-30s  %-10s  %s\n", "ENTITY", "CLASS", "OFFSET");
    printf("  ──────────────────────────────────────────\n");

    for (int i = 0; i < n_hits; i++) {
        printf("  %-30s  %-10s  %ld\n",
               hits[i].entity, hits[i].entity_class, hits[i].offset);
    }

    printf("  ──────────────────────────────────────────\n");
    printf("  Entities extracted: %d\n\n", n_hits);

    /* JSONL output — one entity per line */
    for (int i = 0; i < n_hits; i++) {
        printf("  SAGCO_ENTITY {\"entity\":\"%s\",\"class\":\"%s\","
               "\"source\":\"%s\",\"offset\":%ld}\n",
               hits[i].entity, hits[i].entity_class, input, hits[i].offset);
    }

    printf("\n  SAGCO_RECEIPT subsystem=knowledge command=entities "
           "source=%s entities=%d verdict=%s\n\n",
           input, n_hits, n_hits >= 5 ? "PROVEN" : n_hits >= 2 ? "PROMISING" : "UNPROVEN");

    return 0;
}
