#ifndef DIVTRACK_REPORT_H
#define DIVTRACK_REPORT_H

#include "portfolio.h"
#include "calc.h"

void report_holdings(const Portfolio *p);
void report_income(const Portfolio *p, const PortfolioSummary *s);
void report_projection(const Portfolio *p, int years);
void report_full(const Portfolio *p);

#endif /* DIVTRACK_REPORT_H */
