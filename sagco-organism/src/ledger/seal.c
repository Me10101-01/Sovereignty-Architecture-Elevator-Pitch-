/* seal.c — Ledger subsystem entry point */
#include <stdio.h>
#include <string.h>
#include "../router/router.h"
#include "sha256.h"
int ledger_handle(SagcoContext *ctx) {
    if (ctx->argc >= 1 && strcmp(ctx->command, "seal") == 0) {
        char hash[65];
        sha256_file(ctx->argv[0], hash);
        printf("  [SHA256] %s  %s\n", hash, ctx->argv[0]);
        return 0;
    }
    printf("  ledger: seal <file> | receipt | verify\n");
    return 0;
}
