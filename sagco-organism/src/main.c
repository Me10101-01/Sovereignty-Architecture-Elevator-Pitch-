/*
 * main.c — SAGCO Organism dispatcher
 *
 * The front door. Every subsystem is reachable from here.
 *
 * Usage:
 *   sagco physics ohm --voltage 120 --current 10
 *   sagco gps bearing --lat1 29.76 --lon1 -95.36 --lat2 40.71 --lon2 -74.00
 *   sagco ninja debug
 *   sagco ledger seal <file>
 *   sagco analyze <input>   -- auto-routes through lexer → parser → dispatcher
 *
 * Dispatch pipeline:
 *   INPUT → lexer → parser → AST → router → [subsystem] → ledger → sha256 seal
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "router/router.h"
#include "ledger/sha256.h"
#include "ledger/receipt.h"

#define SAGCO_VERSION "0.1.0"
#define SAGCO_BRICK   "BRICK-020"

static void print_banner(void)
{
    printf("\n  SAGCO Organism  v%s  (%s)\n", SAGCO_VERSION, SAGCO_BRICK);
    printf("  %-40s\n\n", "It either computes or it doesn't.");
}

static void print_usage(void)
{
    printf("  Usage: sagco <subsystem> <command> [args...]\n\n");
    printf("  Subsystems:\n");
    printf("    physics   ohm / lever / tension / fos / rc\n");
    printf("    gps       bearing / compass / declination / exchanger-locator\n");
    printf("    field     exchanger / insulation / pipe / rope-access\n");
    printf("    network   curl / ssh / http-parse\n");
    printf("    ninja     debug / trace / volume / risk / seal\n");
    printf("    ledger    seal / receipt / verify\n");
    printf("    analyze   <pdf|url|file>   -- auto-dispatch\n");
    printf("\n");
    printf("  Dispatch chain:\n");
    printf("    INPUT → lexer → parser → AST → router → subsystem → ledger → SHA-256 seal\n\n");
}

int main(int argc, char *argv[])
{
    if (argc < 2) {
        print_banner();
        print_usage();
        return 0;
    }

    if (strcmp(argv[1], "--version") == 0 || strcmp(argv[1], "-v") == 0) {
        printf("sagco %s (%s)\n", SAGCO_VERSION, SAGCO_BRICK);
        return 0;
    }

    print_banner();

    /* Build dispatch context */
    SagcoContext ctx = {
        .subsystem = argv[1],
        .command   = argc > 2 ? argv[2] : "",
        .argc      = argc - 2,
        .argv      = argv + 2,
    };

    /* Dispatch */
    int result = sagco_dispatch(&ctx);

    /* Every invocation gets a receipt — even failures */
    SagcoReceipt receipt = {
        .subsystem = ctx.subsystem,
        .command   = ctx.command,
        .verdict   = result == 0 ? "COMPUTED" : "FAILED_COMPUTE",
        .exit_code = result,
    };
    receipt_append(&receipt, "logs/invocations.log");

    return result;
}
