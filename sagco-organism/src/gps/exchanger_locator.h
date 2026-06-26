#ifndef EXCHANGER_LOCATOR_H
#define EXCHANGER_LOCATOR_H

#define MAX_READINGS      64
#define MAX_FINGERPRINTS  32

typedef struct {
    int    n;
    double lat, lon, alt_ft;
    double heading[MAX_READINGS];
    double field_ut[MAX_READINGS];
} CompassReadings;

typedef struct {
    int    n;
    double field_min, field_max, field_mean, field_range;
    double heading_min, heading_max, heading_spread;
} LocationStats;

typedef struct {
    char   asset_id[64];
    char   asset_type[64];
    char   facility[64];
    double mean_ut;
    double range_ut;
    double spread_deg;
    int    n_readings;
} AssetFingerprint;

typedef struct {
    char   asset_id[64];
    char   facility[64];
    double confidence;
    char   verdict[16];
} MatchResult;

int         locator_read_csv(const char *path, CompassReadings *out);
void        locator_compute_stats(const CompassReadings *r, LocationStats *s);
int         locator_load_fingerprints(const char *path, AssetFingerprint *fps, int maxfp);
MatchResult locator_match(const LocationStats *s, const AssetFingerprint *fps, int nfp);

#endif
