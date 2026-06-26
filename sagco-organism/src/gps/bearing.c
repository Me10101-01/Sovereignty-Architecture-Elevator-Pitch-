/*
 * bearing.c — GPS bearing + distance calculator
 *
 * Usage: sagco gps bearing --lat1 29.76 --lon1 -95.36 --lat2 40.71 --lon2 -74.00
 *
 * Haversine formula. Output: bearing (degrees true), distance (miles + km).
 * ERU: expected heading vs actual GPS heading (if --actual-bearing supplied).
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "../router/router.h"

#define PI       3.14159265358979323846
#define R_EARTH  3958.8   /* miles */
#define DEG2RAD(d) ((d) * PI / 180.0)
#define RAD2DEG(r) ((r) * 180.0 / PI)

static double get_arg(SagcoContext *ctx, const char *flag)
{
    for (int i = 0; i < ctx->argc - 1; i++)
        if (strcmp(ctx->argv[i], flag) == 0) return atof(ctx->argv[i+1]);
    return NAN;
}

static int bearing_handle(SagcoContext *ctx)
{
    double lat1 = get_arg(ctx, "--lat1");
    double lon1 = get_arg(ctx, "--lon1");
    double lat2 = get_arg(ctx, "--lat2");
    double lon2 = get_arg(ctx, "--lon2");
    double actual_bearing = get_arg(ctx, "--actual-bearing");

    if (isnan(lat1)||isnan(lon1)||isnan(lat2)||isnan(lon2)) {
        fprintf(stderr, "  GPS BEARING: --lat1 --lon1 --lat2 --lon2 required\n");
        return 1;
    }

    double φ1 = DEG2RAD(lat1), φ2 = DEG2RAD(lat2);
    double dφ = DEG2RAD(lat2 - lat1);
    double dλ = DEG2RAD(lon2 - lon1);

    /* Haversine distance */
    double a    = sin(dφ/2)*sin(dφ/2) + cos(φ1)*cos(φ2)*sin(dλ/2)*sin(dλ/2);
    double c    = 2 * atan2(sqrt(a), sqrt(1-a));
    double dist_mi = R_EARTH * c;
    double dist_km = dist_mi * 1.60934;

    /* Bearing */
    double y        = sin(dλ) * cos(φ2);
    double x        = cos(φ1)*sin(φ2) - sin(φ1)*cos(φ2)*cos(dλ);
    double bearing  = fmod(RAD2DEG(atan2(y, x)) + 360.0, 360.0);

    printf("\n  GPS BEARING\n");
    printf("  %-20s: (%.6f, %.6f)\n", "From", lat1, lon1);
    printf("  %-20s: (%.6f, %.6f)\n", "To",   lat2, lon2);
    printf("  %-20s: %.2f°\n",  "True Bearing", bearing);
    printf("  %-20s: %.2f mi  (%.2f km)\n", "Distance", dist_mi, dist_km);

    /* ERU: expected bearing vs actual GPS reading */
    if (!isnan(actual_bearing)) {
        double diff  = fabs(bearing - actual_bearing);
        if (diff > 180) diff = 360 - diff;
        double ratio = diff <= 5.0 ? 1.0 : (diff <= 15.0 ? 0.75 : 0.3);
        const char *v = ratio >= 1.0 ? "PROVEN" : ratio >= 0.5 ? "PROMISING" : "UNPROVEN";
        printf("\n  ERU: computed=%.1f° actual=%.1f° diff=%.1f°  [%s]\n",
            bearing, actual_bearing, diff, v);
    }

    return 0;
}

int gps_handle(SagcoContext *ctx)
{
    if (!ctx->command || ctx->command[0] == '\0') {
        printf("  gps: bearing | compass | declination | exchanger-locator\n");
        return 0;
    }
    if (strcmp(ctx->command, "bearing") == 0) return bearing_handle(ctx);
    fprintf(stderr, "  gps: unknown command '%s'\n", ctx->command);
    return 1;
}
