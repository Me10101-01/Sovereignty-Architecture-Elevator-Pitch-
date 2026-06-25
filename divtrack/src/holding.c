#include <stdio.h>
#include <string.h>
#include "holding.h"

void holding_calc(const Holding *h, HoldingCalc *out)
{
    out->yield_on_cost  = (h->cost_basis > 0)
                          ? h->annual_div_per_share / h->cost_basis : 0.0;
    out->current_yield  = (h->current_price > 0)
                          ? h->annual_div_per_share / h->current_price : 0.0;
    out->annual_income  = h->annual_div_per_share * h->shares;
    out->monthly_income = out->annual_income / 12.0;
    out->market_value   = h->current_price * h->shares;
    out->total_cost     = h->cost_basis * h->shares;
}

void holding_print_row(const Holding *h, const HoldingCalc *c, int idx)
{
    printf("  %2d  %-6s  %-12s  %8.2f sh  $%8.2f cb  $%8.2f price"
           "  YOC:%5.2f%%  $%7.2f/mo\n",
           idx + 1,
           h->symbol,
           h->account,
           h->shares,
           h->cost_basis,
           h->current_price,
           c->yield_on_cost * 100.0,
           c->monthly_income);
}
