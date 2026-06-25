#ifndef DIVTRACK_HOLDING_H
#define DIVTRACK_HOLDING_H

#define SYMBOL_LEN  12
#define NAME_LEN    64
#define ACCOUNT_LEN 16
#define NOTES_LEN  128

typedef struct {
    char   symbol[SYMBOL_LEN];
    char   name[NAME_LEN];
    char   account[ACCOUNT_LEN];   /* ROTH_IRA | TRAD_IRA | TAXABLE | HSA */
    double shares;
    double cost_basis;             /* per share */
    double current_price;          /* per share */
    double annual_div_per_share;   /* TTM */
    double div_growth_rate;        /* 5yr CAGR, e.g. 0.10 = 10% */
    int    drip;                   /* 1 = DRIP enabled */
    char   notes[NOTES_LEN];
} Holding;

/* Computed (not stored — derived on demand) */
typedef struct {
    double yield_on_cost;   /* annual_div_per_share / cost_basis */
    double current_yield;   /* annual_div_per_share / current_price */
    double annual_income;   /* annual_div_per_share * shares */
    double monthly_income;  /* annual_income / 12 */
    double market_value;    /* current_price * shares */
    double total_cost;      /* cost_basis * shares */
} HoldingCalc;

void   holding_calc(const Holding *h, HoldingCalc *out);
void   holding_print_row(const Holding *h, const HoldingCalc *c, int idx);

#endif /* DIVTRACK_HOLDING_H */
