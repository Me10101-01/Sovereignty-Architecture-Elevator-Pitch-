/*
 * router.c — SAGCO subsystem dispatcher
 *
 * Routes incoming context to the correct subsystem handler.
 * This is the middleware that was missing.
 *
 * Dispatch table maps subsystem name → handler function.
 * Adding a new subsystem = one entry in the table. Nothing else changes.
 */

#include <stdio.h>
#include <string.h>
#include "router.h"
#include "route_table.h"
#include "dispatch.h"

int sagco_dispatch(SagcoContext *ctx)
{
    if (!ctx->subsystem || ctx->subsystem[0] == '\0') {
        fprintf(stderr, "  ERROR: no subsystem specified\n");
        return 1;
    }

    /* "analyze" is the auto-router — runs full lexer→parser→AST→subsystem chain */
    if (strcmp(ctx->subsystem, "analyze") == 0) {
        return sagco_analyze_pipeline(ctx);
    }

    /* Direct subsystem dispatch */
    SubsystemHandler handler = route_lookup(ctx->subsystem);
    if (!handler) {
        fprintf(stderr, "  ERROR: unknown subsystem '%s'\n", ctx->subsystem);
        fprintf(stderr, "  Run: sagco --help\n");
        return 1;
    }

    printf("  [DISPATCH] %s %s\n", ctx->subsystem, ctx->command);
    int result = handler(ctx);
    printf("  [%s] %s %s\n",
        result == 0 ? "COMPUTED" : "FAILED_COMPUTE",
        ctx->subsystem, ctx->command);

    return result;
}
