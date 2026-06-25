/*
 * portfolio.c — Load/save portfolio from JSON.
 *
 * Uses a minimal hand-written JSON parser (no external deps).
 * Format: { "owner": "...", "target_monthly": 5000, "holdings": [ {...}, ... ] }
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "portfolio.h"

/* ── Minimal JSON helpers ───────────────────────────────────────────────── */

static char *json_find_key(const char *buf, const char *key)
{
    char needle[128];
    snprintf(needle, sizeof(needle), "\"%s\"", key);
    return strstr(buf, needle);
}

static int json_read_string(const char *pos, const char *key, char *out, int maxlen)
{
    char *p = json_find_key(pos, key);
    if (!p) return 0;
    p = strchr(p, ':'); if (!p) return 0;
    while (*p == ':' || *p == ' ' || *p == '\t') p++;
    if (*p != '"') return 0;
    p++;
    int i = 0;
    while (*p && *p != '"' && i < maxlen - 1)
        out[i++] = *p++;
    out[i] = '\0';
    return 1;
}

static int json_read_double(const char *pos, const char *key, double *out)
{
    char *p = json_find_key(pos, key);
    if (!p) return 0;
    p = strchr(p, ':'); if (!p) return 0;
    while (*p == ':' || *p == ' ' || *p == '\t') p++;
    *out = atof(p);
    return 1;
}

static int json_read_int(const char *pos, const char *key, int *out)
{
    char *p = json_find_key(pos, key);
    if (!p) return 0;
    p = strchr(p, ':'); if (!p) return 0;
    while (*p == ':' || *p == ' ' || *p == '\t') p++;
    *out = atoi(p);
    return 1;
}

/* ── Save ───────────────────────────────────────────────────────────────── */

int portfolio_save(const Portfolio *p, const char *path)
{
    FILE *f = fopen(path, "w");
    if (!f) { fprintf(stderr, "divtrack: cannot open %s for write\n", path); return 1; }

    fprintf(f, "{\n");
    fprintf(f, "  \"owner\": \"%s\",\n", p->owner);
    fprintf(f, "  \"target_monthly\": %.2f,\n", p->target_monthly);
    fprintf(f, "  \"holdings\": [\n");

    for (int i = 0; i < p->n_holdings; i++) {
        const Holding *h = &p->holdings[i];
        fprintf(f, "    {\n");
        fprintf(f, "      \"symbol\": \"%s\",\n",   h->symbol);
        fprintf(f, "      \"name\": \"%s\",\n",     h->name);
        fprintf(f, "      \"account\": \"%s\",\n",  h->account);
        fprintf(f, "      \"shares\": %.4f,\n",     h->shares);
        fprintf(f, "      \"cost_basis\": %.4f,\n", h->cost_basis);
        fprintf(f, "      \"current_price\": %.4f,\n", h->current_price);
        fprintf(f, "      \"annual_div_per_share\": %.4f,\n", h->annual_div_per_share);
        fprintf(f, "      \"div_growth_rate\": %.4f,\n", h->div_growth_rate);
        fprintf(f, "      \"drip\": %d,\n", h->drip);
        fprintf(f, "      \"notes\": \"%s\"\n", h->notes);
        fprintf(f, "    }%s\n", (i < p->n_holdings - 1) ? "," : "");
    }

    fprintf(f, "  ]\n");
    fprintf(f, "}\n");
    fclose(f);
    return 0;
}

/* ── Load ───────────────────────────────────────────────────────────────── */

int portfolio_load(Portfolio *p, const char *path)
{
    FILE *f = fopen(path, "r");
    if (!f) return 1;

    fseek(f, 0, SEEK_END);
    long sz = ftell(f);
    rewind(f);

    char *buf = malloc(sz + 1);
    if (!buf) { fclose(f); return 1; }
    fread(buf, 1, sz, f);
    buf[sz] = '\0';
    fclose(f);

    /* Meta */
    json_read_string(buf, "owner", p->owner, sizeof(p->owner));
    json_read_double(buf, "target_monthly", &p->target_monthly);

    /* Holdings array */
    p->n_holdings = 0;
    char *cursor = strstr(buf, "\"holdings\"");
    if (!cursor) { free(buf); return 0; }
    cursor = strchr(cursor, '[');
    if (!cursor) { free(buf); return 0; }

    while (p->n_holdings < MAX_HOLDINGS) {
        char *obj_start = strchr(cursor, '{');
        if (!obj_start) break;
        char *obj_end   = strchr(obj_start, '}');
        if (!obj_end) break;

        /* Copy object to tmp buf */
        int obj_len = (int)(obj_end - obj_start + 1);
        char *tmp   = malloc(obj_len + 1);
        if (!tmp) break;
        strncpy(tmp, obj_start, obj_len);
        tmp[obj_len] = '\0';

        Holding *h = &p->holdings[p->n_holdings];
        memset(h, 0, sizeof(Holding));

        json_read_string(tmp, "symbol",   h->symbol,  sizeof(h->symbol));
        json_read_string(tmp, "name",     h->name,    sizeof(h->name));
        json_read_string(tmp, "account",  h->account, sizeof(h->account));
        json_read_string(tmp, "notes",    h->notes,   sizeof(h->notes));
        json_read_double(tmp, "shares",              &h->shares);
        json_read_double(tmp, "cost_basis",          &h->cost_basis);
        json_read_double(tmp, "current_price",       &h->current_price);
        json_read_double(tmp, "annual_div_per_share",&h->annual_div_per_share);
        json_read_double(tmp, "div_growth_rate",     &h->div_growth_rate);
        json_read_int   (tmp, "drip",                &h->drip);

        if (h->symbol[0] != '\0')
            p->n_holdings++;

        free(tmp);
        cursor = obj_end + 1;
    }

    free(buf);
    return 0;
}

/* ── CRUD ───────────────────────────────────────────────────────────────── */

int portfolio_find(const Portfolio *p, const char *symbol)
{
    for (int i = 0; i < p->n_holdings; i++)
        if (strcmp(p->holdings[i].symbol, symbol) == 0) return i;
    return -1;
}

int portfolio_add(Portfolio *p, const Holding *h)
{
    if (p->n_holdings >= MAX_HOLDINGS) {
        fprintf(stderr, "divtrack: max holdings (%d) reached\n", MAX_HOLDINGS);
        return 1;
    }
    /* Update if exists */
    int idx = portfolio_find(p, h->symbol);
    if (idx >= 0) {
        p->holdings[idx] = *h;
        return 0;
    }
    p->holdings[p->n_holdings++] = *h;
    return 0;
}

int portfolio_remove(Portfolio *p, const char *symbol)
{
    int idx = portfolio_find(p, symbol);
    if (idx < 0) return 1;
    for (int i = idx; i < p->n_holdings - 1; i++)
        p->holdings[i] = p->holdings[i + 1];
    p->n_holdings--;
    return 0;
}

void portfolio_default(Portfolio *p)
{
    memset(p, 0, sizeof(Portfolio));
    strncpy(p->owner, "Strategickhaos DAO LLC", sizeof(p->owner) - 1);
    p->target_monthly = 5000.0;
}
