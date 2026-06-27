/*
 * graph_builder.c — ML-KNOW-002  (knowledge subsystem)
 *
 * Reads entity hits from entity_extractor, builds co-occurrence graph,
 * emits edges as JSONL to knowledge_graph.jsonl.
 *
 * Graph model:
 *   node = entity (e.g. "RFC4862", "SHA-256", "ERU")
 *   edge = co-occurrence in same artifact
 *   weight = 1 (binary presence per artifact)
 *   accumulate = merge across all ingested artifacts
 *
 * Usage:
 *   sagco knowledge graph --input <file> [--out knowledge_graph.jsonl]
 *
 * Output edges (JSONL):
 *   {"from":"SHA-256","from_class":"crypto","to":"ERU","to_class":"field",
 *    "weight":1,"source":"dark_matter_manifest.jsonl"}
 *
 * Dispatch entry point:
 *   graph_handle(ctx) registered in knowledge_handle()
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../router/router.h"
#include "entity_extractor.h"

#define MAX_EDGES 2048

typedef struct {
    char from[64];
    char from_class[16];
    char to[64];
    char to_class[16];
    int  weight;
    char source[128];
} GraphEdge;

static int build_edges(EntityHit *hits, int n, const char *source,
                       GraphEdge *edges, int *n_edges)
{
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            if (strcmp(hits[i].entity, hits[j].entity) == 0) continue;

            /* check for duplicate edge */
            int dup = 0;
            for (int e = 0; e < *n_edges; e++) {
                if ((strcmp(edges[e].from, hits[i].entity) == 0 &&
                     strcmp(edges[e].to,   hits[j].entity) == 0) ||
                    (strcmp(edges[e].from, hits[j].entity) == 0 &&
                     strcmp(edges[e].to,   hits[i].entity) == 0)) {
                    edges[e].weight++;
                    dup = 1; break;
                }
            }
            if (!dup && *n_edges < MAX_EDGES) {
                GraphEdge *ed = &edges[*n_edges];
                snprintf(ed->from,       64, "%s", hits[i].entity);
                snprintf(ed->from_class, 16, "%s", hits[i].entity_class);
                snprintf(ed->to,         64, "%s", hits[j].entity);
                snprintf(ed->to_class,   16, "%s", hits[j].entity_class);
                ed->weight = 1;
                strncpy(ed->source, source, 127);
                (*n_edges)++;
            }
        }
    }
    return *n_edges;
}

static const char *get_arg_g(SagcoContext *ctx, const char *flag)
{
    for (int i = 0; i < ctx->argc - 1; i++)
        if (strcmp(ctx->argv[i], flag) == 0) return ctx->argv[i + 1];
    return NULL;
}

int graph_handle(SagcoContext *ctx)
{
    const char *input  = get_arg_g(ctx, "--input");
    const char *outpath = get_arg_g(ctx, "--out");
    if (!outpath) outpath = "data/knowledge_graph.jsonl";
    if (!input) {
        fprintf(stderr, "  [graph] --input <file> required\n");
        return 1;
    }

    /* reuse entity scanner */
    FILE *fp = fopen(input, "r");
    if (!fp) { fprintf(stderr, "  [graph] cannot open %s\n", input); return 1; }

    EntityHit hits[MAX_ENTITIES];
    int n_hits = 0;
    char buf[CHUNK + 64];
    size_t prev_tail = 0;
    long base_offset = 0;

    while (!feof(fp)) {
        size_t n = fread(buf + prev_tail, 1, CHUNK, fp);
        size_t total = prev_tail + n;
        if (total == 0) break;
        scan_chunk(buf, total, input, hits, &n_hits, base_offset);
        prev_tail = total > 64 ? 64 : total;
        memmove(buf, buf + total - prev_tail, prev_tail);
        base_offset += (long)(total - prev_tail);
    }
    fclose(fp);

    if (n_hits == 0) {
        fprintf(stderr, "  [graph] no entities found in %s\n", input);
        return 1;
    }

    GraphEdge edges[MAX_EDGES];
    int n_edges = 0;
    build_edges(hits, n_hits, input, edges, &n_edges);

    /* append to knowledge graph JSONL */
    FILE *out = fopen(outpath, "a");
    if (!out) {
        fprintf(stderr, "  [graph] cannot open output %s\n", outpath);
        return 1;
    }

    for (int e = 0; e < n_edges; e++) {
        fprintf(out,
            "{\"from\":\"%s\",\"from_class\":\"%s\","
            "\"to\":\"%s\",\"to_class\":\"%s\","
            "\"weight\":%d,\"source\":\"%s\"}\n",
            edges[e].from, edges[e].from_class,
            edges[e].to,   edges[e].to_class,
            edges[e].weight, edges[e].source);
    }
    fclose(out);

    /* print summary */
    printf("\n  SAGCO knowledge graph — %s\n", input);
    printf("  ──────────────────────────────────────────────────────\n");
    printf("  %-24s  %-10s  →  %-24s  %-10s  W\n",
           "FROM", "CLASS", "TO", "CLASS");
    printf("  ──────────────────────────────────────────────────────\n");

    int shown = n_edges < 20 ? n_edges : 20;
    for (int e = 0; e < shown; e++) {
        printf("  %-24s  %-10s  →  %-24s  %-10s  %d\n",
               edges[e].from, edges[e].from_class,
               edges[e].to,   edges[e].to_class,
               edges[e].weight);
    }
    if (n_edges > shown)
        printf("  ... %d more edges (see %s)\n", n_edges - shown, outpath);

    printf("  ──────────────────────────────────────────────────────\n");
    printf("  Entities: %d  |  Edges: %d  |  Appended to: %s\n\n",
           n_hits, n_edges, outpath);

    printf("  SAGCO_RECEIPT subsystem=knowledge command=graph "
           "source=%s entities=%d edges=%d out=%s verdict=%s\n\n",
           input, n_hits, n_edges, outpath,
           n_edges >= 10 ? "PROVEN" : n_edges >= 3 ? "PROMISING" : "UNPROVEN");

    return 0;
}
