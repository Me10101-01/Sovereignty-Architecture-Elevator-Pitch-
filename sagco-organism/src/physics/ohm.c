/*
 * ohm.c — Ohm's Law calculator: V = IR, P = IV
 *
 * Usage: sagco physics ohm --voltage 120 --current 10
 *        sagco physics ohm --resistance 12 --current 10
 *
 * ERU: expected = rated/spec value, actual = measured value
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "../../router/router.h"
#include "../../ledger/receipt.h"

static double get_arg(SagcoContext *ctx, const char *flag)
{
    for (int i = 0; i < ctx->argc - 1; i++)
        if (strcmp(ctx->argv[i], flag) == 0)
            return atof(ctx->argv[i+1]);
    return NAN;
}

int ohm_handle(SagcoContext *ctx)
{
    double V = get_arg(ctx, "--voltage");
    double I = get_arg(ctx, "--current");
    double R = get_arg(ctx, "--resistance");
    double P_rated = get_arg(ctx, "--rated-power");

    int known = (!isnan(V)) + (!isnan(I)) + (!isnan(R));
    if (known < 2) {
        fprintf(stderr, "  OHM: need any 2 of --voltage, --current, --resistance\n");
        return 1;
    }

    if (isnan(V)) V = I * R;
    if (isnan(I)) I = V / R;
    if (isnan(R)) R = V / I;
    double P = V * I;

    printf("\n  OHM'S LAW\n");
    printf("  %-15s: %.4f V\n",  "Voltage",    V);
    printf("  %-15s: %.4f A\n",  "Current",    I);
    printf("  %-15s: %.4f Ω\n",  "Resistance", R);
    printf("  %-15s: %.4f W\n",  "Power",      P);

    /* ERU: actual power vs rated power */
    if (!isnan(P_rated) && P_rated > 0) {
        double ratio   = P / P_rated;
        const char *verdict = ratio >= 1.0 ? "PROVEN" : ratio >= 0.5 ? "PROMISING" : "UNPROVEN";
        printf("\n  ERU: P_actual=%.2fW / P_rated=%.2fW  V=%.4f  [%s]\n",
            P, P_rated, ratio, verdict);
    }

    return 0;
}

/* Subsystem entry — routes ohm / lever / fos / etc */
int physics_handle(SagcoContext *ctx)
{
    if (!ctx->command || ctx->command[0] == '\0') {
        printf("  physics: ohm | lever | tension | fos | rc\n");
        return 0;
    }
    if (strcmp(ctx->command, "ohm") == 0) return ohm_handle(ctx);
    fprintf(stderr, "  physics: unknown command '%s'\n", ctx->command);
    return 1;
}
