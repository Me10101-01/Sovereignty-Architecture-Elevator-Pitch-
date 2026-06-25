/*
 * divtrack — Dividend Portfolio Tracker
 *
 * Usage:
 *   divtrack                     — show full report
 *   divtrack report              — same
 *   divtrack holdings            — list holdings only
 *   divtrack income              — income summary only
 *   divtrack project [years]     — income projection
 *   divtrack add <sym> <shares> <cost> <price> <annual_div> <acct>
 *   divtrack update <sym> <field> <value>
 *   divtrack remove <sym>
 *   divtrack target <monthly>    — set monthly income target
 *   divtrack help
 *
 * Data file: $HOME/SAGCO/portfolio/portfolio.json
 *            (or DIVTRACK_DATA env var)
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "portfolio.h"
#include "calc.h"
#include "report.h"

#ifdef _WIN32
#include <direct.h>
#define mkdir_p(p) _mkdir(p)
#else
#include <sys/stat.h>
#define mkdir_p(p) mkdir(p, 0755)
#endif

static void get_data_path(char *out, size_t len)
{
    const char *env = getenv("DIVTRACK_DATA");
    if (env) {
        strncpy(out, env, len - 1);
        return;
    }
    const char *home = getenv("HOME");
    if (!home) home = ".";
    snprintf(out, len, "%s/SAGCO/portfolio/portfolio.json", home);
}

static void ensure_dir(const char *path)
{
    char buf[512];
    strncpy(buf, path, sizeof(buf) - 1);
    /* Walk up to the last slash and mkdir each component */
    for (char *p = buf + 1; *p; p++) {
        if (*p == '/') {
            *p = '\0';
            mkdir_p(buf);   /* ignore errors — dir may already exist */
            *p = '/';
        }
    }
    /* Create the final directory component (strip filename) */
    char *slash = strrchr(buf, '/');
    if (slash) { *slash = '\0'; mkdir_p(buf); }
}

static void usage(void)
{
    printf("\n  divtrack — Dividend Portfolio Tracker\n\n");
    printf("  Commands:\n");
    printf("    divtrack                        Full report\n");
    printf("    divtrack report                 Full report\n");
    printf("    divtrack holdings               List holdings\n");
    printf("    divtrack income                 Income summary\n");
    printf("    divtrack project [years]        Income projection (default 15yr)\n");
    printf("    divtrack add SYM SHARES COST PRICE ANNUAL_DIV ACCOUNT\n");
    printf("    divtrack update SYM FIELD VALUE  (fields: shares cost price div growth drip)\n");
    printf("    divtrack remove SYM\n");
    printf("    divtrack target MONTHLY_AMT\n");
    printf("    divtrack help\n\n");
    printf("  Example:\n");
    printf("    divtrack add SCHD 100 80.00 83.00 2.92 ROTH_IRA\n");
    printf("    divtrack update SCHD price 86.50\n");
    printf("    divtrack project 20\n\n");
}

int main(int argc, char *argv[])
{
    char data_path[512];
    get_data_path(data_path, sizeof(data_path));

    Portfolio p;
    portfolio_default(&p);

    /* Load existing portfolio (ignore error if file doesn't exist yet) */
    portfolio_load(&p, data_path);

    const char *cmd = (argc >= 2) ? argv[1] : "report";

    /* ── report ─────────────────────────────────────────────────────────── */
    if (strcmp(cmd, "report") == 0 || strcmp(cmd, "") == 0) {
        report_full(&p);
    }

    /* ── holdings ───────────────────────────────────────────────────────── */
    else if (strcmp(cmd, "holdings") == 0) {
        report_holdings(&p);
    }

    /* ── income ─────────────────────────────────────────────────────────── */
    else if (strcmp(cmd, "income") == 0) {
        PortfolioSummary s;
        portfolio_summarize(&p, &s);
        report_income(&p, &s);
    }

    /* ── project ────────────────────────────────────────────────────────── */
    else if (strcmp(cmd, "project") == 0) {
        int years = (argc >= 3) ? atoi(argv[2]) : 15;
        if (years <= 0 || years > 50) years = 15;
        report_projection(&p, years);
    }

    /* ── add ────────────────────────────────────────────────────────────── */
    else if (strcmp(cmd, "add") == 0) {
        if (argc < 8) {
            fprintf(stderr, "  Usage: divtrack add SYM SHARES COST PRICE ANNUAL_DIV ACCOUNT\n");
            return 1;
        }
        Holding h;
        memset(&h, 0, sizeof(h));
        strncpy(h.symbol,  argv[2], sizeof(h.symbol) - 1);
        h.shares               = atof(argv[3]);
        h.cost_basis           = atof(argv[4]);
        h.current_price        = atof(argv[5]);
        h.annual_div_per_share = atof(argv[6]);
        strncpy(h.account, argv[7], sizeof(h.account) - 1);
        h.div_growth_rate = 0.07;  /* default 7% — update with: divtrack update SYM growth X */
        h.drip = 1;

        if (portfolio_add(&p, &h) != 0) return 1;
        ensure_dir(data_path);
        portfolio_save(&p, data_path);
        printf("  Added %s. Portfolio: %d holding(s).\n", h.symbol, p.n_holdings);

        PortfolioSummary s;
        portfolio_summarize(&p, &s);
        printf("  Monthly income now: $%.2f  [%s]\n", s.total_monthly_income, s.verdict);
    }

    /* ── update ─────────────────────────────────────────────────────────── */
    else if (strcmp(cmd, "update") == 0) {
        if (argc < 5) {
            fprintf(stderr, "  Usage: divtrack update SYM FIELD VALUE\n");
            return 1;
        }
        const char *sym   = argv[2];
        const char *field = argv[3];
        double val = atof(argv[4]);

        int idx = portfolio_find(&p, sym);
        if (idx < 0) { fprintf(stderr, "  Not found: %s\n", sym); return 1; }

        Holding *h = &p.holdings[idx];
        if      (strcmp(field, "shares")  == 0) h->shares                = val;
        else if (strcmp(field, "cost")    == 0) h->cost_basis             = val;
        else if (strcmp(field, "price")   == 0) h->current_price          = val;
        else if (strcmp(field, "div")     == 0) h->annual_div_per_share   = val;
        else if (strcmp(field, "growth")  == 0) h->div_growth_rate        = val;
        else if (strcmp(field, "drip")    == 0) h->drip                   = (int)val;
        else { fprintf(stderr, "  Unknown field: %s\n", field); return 1; }

        portfolio_save(&p, data_path);
        printf("  Updated %s.%s = %.4f\n", sym, field, val);

        PortfolioSummary s;
        portfolio_summarize(&p, &s);
        printf("  Monthly income now: $%.2f  [%s]\n", s.total_monthly_income, s.verdict);
    }

    /* ── remove ─────────────────────────────────────────────────────────── */
    else if (strcmp(cmd, "remove") == 0) {
        if (argc < 3) { fprintf(stderr, "  Usage: divtrack remove SYM\n"); return 1; }
        if (portfolio_remove(&p, argv[2]) != 0) {
            fprintf(stderr, "  Not found: %s\n", argv[2]); return 1;
        }
        portfolio_save(&p, data_path);
        printf("  Removed %s. Portfolio: %d holding(s).\n", argv[2], p.n_holdings);
    }

    /* ── target ─────────────────────────────────────────────────────────── */
    else if (strcmp(cmd, "target") == 0) {
        if (argc < 3) { fprintf(stderr, "  Usage: divtrack target MONTHLY_AMT\n"); return 1; }
        p.target_monthly = atof(argv[2]);
        portfolio_save(&p, data_path);
        printf("  Target set to $%.2f/month\n", p.target_monthly);
    }

    /* ── help ───────────────────────────────────────────────────────────── */
    else if (strcmp(cmd, "help") == 0) {
        usage();
    }

    else {
        fprintf(stderr, "  Unknown command: %s\n", cmd);
        usage();
        return 1;
    }

    return 0;
}
