/*
 * knowledge.c — ML-KNOW-001/002  (knowledge subsystem dispatch)
 *
 * Routes knowledge sub-commands to entity_extractor and graph_builder.
 *
 * Usage:
 *   sagco knowledge entities --input <file>
 *   sagco knowledge graph    --input <file> [--out knowledge_graph.jsonl]
 *
 * Dispatch entry point:
 *   knowledge_handle(ctx)
 */

#include <stdio.h>
#include <string.h>
#include "../router/router.h"

int entities_handle(SagcoContext *ctx);
int graph_handle(SagcoContext *ctx);

int knowledge_handle(SagcoContext *ctx)
{
    if (!ctx->command || ctx->command[0] == '\0') {
        printf("  knowledge: entities | graph\n");
        return 0;
    }
    if (strcmp(ctx->command, "entities") == 0) return entities_handle(ctx);
    if (strcmp(ctx->command, "graph")    == 0) return graph_handle(ctx);

    fprintf(stderr, "  knowledge: unknown command '%s'\n", ctx->command);
    return 1;
}
