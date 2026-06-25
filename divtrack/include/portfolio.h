#ifndef DIVTRACK_PORTFOLIO_H
#define DIVTRACK_PORTFOLIO_H

#include "holding.h"

#define MAX_HOLDINGS 64

typedef struct {
    char    owner[64];
    double  target_monthly;
    int     n_holdings;
    Holding holdings[MAX_HOLDINGS];
} Portfolio;

int  portfolio_load(Portfolio *p, const char *path);
int  portfolio_save(const Portfolio *p, const char *path);
int  portfolio_add(Portfolio *p, const Holding *h);
int  portfolio_remove(Portfolio *p, const char *symbol);
int  portfolio_find(const Portfolio *p, const char *symbol);
void portfolio_default(Portfolio *p);

#endif /* DIVTRACK_PORTFOLIO_H */
