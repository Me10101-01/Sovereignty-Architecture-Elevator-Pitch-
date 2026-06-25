#include <stdio.h>
#include <string.h>
#include "report.h"

#define LINE "  ─────────────────────────────────────────────────────────────────\n"

static const char *bar(double ratio, int width)
{
    static char buf[128];
    int filled = (int)(ratio * width);
    if (filled > width) filled = width;
    if (filled < 0)     filled = 0;
    int i = 0;
    buf[i++] = '[';
    for (int j = 0; j < width; j++)
        buf[i++] = (j < filled) ? '#' : '-';
    buf[i++] = ']';
    buf[i]   = '\0';
    return buf;
}

void report_holdings(const Portfolio *p)
{
    printf("\n  DIVTRACK — Holdings\n");
    printf("  Owner: %s\n", p->owner);
    printf(LINE);
    printf("  %-6s  %-12s  %8s  %8s  %8s  %6s  %10s\n",
           "SYM", "ACCOUNT", "SHARES", "COST/SH", "PRICE", "YOC%", "$/MO");
    printf(LINE);

    for (int i = 0; i < p->n_holdings; i++) {
        HoldingCalc c;
        holding_calc(&p->holdings[i], &c);
        holding_print_row(&p->holdings[i], &c, i);
    }
    printf(LINE);
    printf("  %d holding(s)\n\n", p->n_holdings);
}

void report_income(const Portfolio *p, const PortfolioSummary *s)
{
    printf("\n  DIVTRACK — Income Summary\n");
    printf(LINE);
    printf("  %-28s: $%.2f\n", "Total Invested",       s->total_invested);
    printf("  %-28s: $%.2f\n", "Market Value",         s->total_market_value);
    printf("  %-28s: %.2f%%\n", "Blended Yield",        s->blended_yield * 100.0);
    printf("  %-28s: %.2f%%\n", "Blended Yield-on-Cost",s->blended_yoc * 100.0);
    printf(LINE);
    printf("  %-28s: $%.2f\n", "Annual Income",        s->total_annual_income);
    printf("  %-28s: $%.2f\n", "Monthly Income",       s->total_monthly_income);
    printf("  %-28s: $%.2f\n", "Target Monthly",       p->target_monthly);
    printf(LINE);
    printf("  %-28s: $%.2f\n", "Gap to Target",        s->monthly_to_target);
    printf("  %-28s: $%.2f\n", "Capital to Close Gap", s->capital_to_close);
    printf(LINE);
    printf("  Progress %s  %.1f%%  [%s]\n",
           bar(s->progress_ratio, 30),
           s->progress_ratio * 100.0,
           s->verdict);
    printf("\n");
}

void report_projection(const Portfolio *p, int years)
{
    printf("\n  DIVTRACK — Income Projection (%d years)\n", years);
    printf(LINE);
    printf("  %-6s  %12s  %12s  %8s\n",
           "Year", "Annual $", "Monthly $", "vs Target");
    printf(LINE);

    for (int y = 1; y <= years; y++) {
        double annual  = project_income_year(p, y);
        double monthly = annual / 12.0;
        double pct     = (p->target_monthly > 0) ? monthly / p->target_monthly * 100.0 : 0.0;
        const char *reached = (monthly >= p->target_monthly) ? " ★ TARGET" : "";
        printf("  +%-5d  $%11.2f  $%11.2f  %7.1f%%%s\n",
               y, annual, monthly, pct, reached);
    }
    printf(LINE);
    printf("\n  Assumes current shares + dividend growth rates. No new contributions.\n\n");
}

void report_full(const Portfolio *p)
{
    PortfolioSummary s;
    portfolio_summarize(p, &s);
    report_holdings(p);
    report_income(p, &s);
    report_projection(p, 15);
}
