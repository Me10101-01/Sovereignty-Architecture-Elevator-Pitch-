#include <string.h>
#include <math.h>
#include "calc.h"
#include "holding.h"

void portfolio_summarize(const Portfolio *p, PortfolioSummary *out)
{
    memset(out, 0, sizeof(PortfolioSummary));

    for (int i = 0; i < p->n_holdings; i++) {
        HoldingCalc c;
        holding_calc(&p->holdings[i], &c);
        out->total_invested      += c.total_cost;
        out->total_market_value  += c.market_value;
        out->total_annual_income += c.annual_income;
    }

    out->total_monthly_income = out->total_annual_income / 12.0;

    out->blended_yield = (out->total_market_value > 0)
                         ? out->total_annual_income / out->total_market_value : 0.0;
    out->blended_yoc   = (out->total_invested > 0)
                         ? out->total_annual_income / out->total_invested : 0.0;

    out->monthly_to_target = p->target_monthly - out->total_monthly_income;
    if (out->monthly_to_target < 0) out->monthly_to_target = 0;

    if (out->blended_yield > 0)
        out->capital_to_close = (out->monthly_to_target * 12.0) / out->blended_yield;

    out->progress_ratio = (p->target_monthly > 0)
                          ? out->total_monthly_income / p->target_monthly : 0.0;

    if      (out->progress_ratio >= 1.0)  out->verdict = "PROVEN";
    else if (out->progress_ratio >= 0.5)  out->verdict = "PROMISING";
    else if (out->progress_ratio >= 0.01) out->verdict = "UNPROVEN";
    else                                   out->verdict = "INFLATED";
}

double project_income_year(const Portfolio *p, int years_ahead)
{
    double total = 0.0;
    for (int i = 0; i < p->n_holdings; i++) {
        const Holding *h = &p->holdings[i];
        double grown_div = h->annual_div_per_share
                           * pow(1.0 + h->div_growth_rate, years_ahead);
        total += grown_div * h->shares;
    }
    return total;
}
