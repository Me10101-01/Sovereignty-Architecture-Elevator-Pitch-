#ifndef DIVTRACK_CALC_H
#define DIVTRACK_CALC_H

#include "portfolio.h"

typedef struct {
    double total_invested;
    double total_market_value;
    double total_annual_income;
    double total_monthly_income;
    double blended_yield;       /* income / market_value */
    double blended_yoc;         /* income / cost_basis */
    double monthly_to_target;   /* target_monthly - monthly_income */
    double capital_to_close;    /* additional capital needed at blended yield */
    double progress_ratio;      /* monthly_income / target_monthly */
    const char *verdict;        /* PROVEN / PROMISING / UNPROVEN / INFLATED */
} PortfolioSummary;

void   portfolio_summarize(const Portfolio *p, PortfolioSummary *out);
double project_income_year(const Portfolio *p, int years_ahead);

#endif /* DIVTRACK_CALC_H */
