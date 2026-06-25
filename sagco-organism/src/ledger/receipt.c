/*
 * receipt.c — Append invocation receipt to log
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "receipt.h"
#include "sha256.h"

#ifdef _WIN32
#include <direct.h>
#define mkdir(p,m) _mkdir(p)
#else
#include <sys/stat.h>
#include <sys/types.h>
#endif

static void ensure_dir(const char *path)
{
    char buf[512];
    strncpy(buf, path, sizeof(buf)-1);
    char *slash = strrchr(buf, '/');
    if (!slash) return;
    *slash = '\0';
    mkdir(buf, 0755);
}

int receipt_append(const SagcoReceipt *r, const char *log_path)
{
    ensure_dir(log_path);
    FILE *f = fopen(log_path, "a");
    if (!f) return 1;

    time_t now = time(NULL);
    char   ts[32];
    strftime(ts, sizeof(ts), "%Y-%m-%dT%H:%M:%SZ", gmtime(&now));

    /* Build payload for SHA-256 */
    char payload[512];
    snprintf(payload, sizeof(payload),
        "{\"ts\":\"%s\",\"subsystem\":\"%s\",\"command\":\"%s\",\"verdict\":\"%s\",\"exit\":%d}",
        ts, r->subsystem ? r->subsystem : "",
        r->command   ? r->command   : "",
        r->verdict   ? r->verdict   : "UNCOMPUTED",
        r->exit_code);

    char hash[65];
    sha256_buf(payload, strlen(payload), hash);

    fprintf(f, "%s  sha256=%s\n", payload, hash);
    fclose(f);
    return 0;
}
