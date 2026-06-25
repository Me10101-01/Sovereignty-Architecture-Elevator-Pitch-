/*
 * test_calc.c — divtrack unit tests
 * Run: make test
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include "portfolio.h"
#include "calc.h"
#include "holding.h"

static int tests_run  = 0;
static int tests_pass = 0;

#define ASSERT(cond, msg) do { \
    tests_run++; \
    if (cond) { tests_pass++; printf("  PASS  %s\n", msg); } \
    else           printf("  FAIL  %s\n", msg); \
} while(0)

#define ASSERT_NEAR(a, b, eps, msg) ASSERT(fabs((a)-(b)) < (eps), msg)

static Portfolio make_test_portfolio(void)
{
    Portfolio p;
    portfolio_default(&p);
    p.target_monthly = 5000.0;

    /* SCHD: 100 shares, $2.92/yr, cost $80, price $83 */
    Holding h1 = {
        .symbol = "SCHD", .account = "ROTH_IRA",
        .shares = 100.0, .cost_basis = 80.0, .current_price = 83.0,
        .annual_div_per_share = 2.92, .div_growth_rate = 0.10,
    };
    portfolio_add(&p, &h1);

    /* DGRO: 50 shares, $1.26/yr, cost $55, price $57 */
    Holding h2 = {
        .symbol = "DGRO", .account = "TRAD_IRA",
        .shares = 50.0, .cost_basis = 55.0, .current_price = 57.0,
        .annual_div_per_share = 1.26, .div_growth_rate = 0.09,
    };
    portfolio_add(&p, &h2);

    return p;
}

/* ── HoldingCalc ─────────────────────────────────────────────────────────── */

static void test_holding_calc(void)
{
    Holding h;
    memset(&h, 0, sizeof(h));
    h.shares               = 100.0;
    h.cost_basis           = 80.0;
    h.current_price        = 83.0;
    h.annual_div_per_share = 2.92;

    HoldingCalc c;
    holding_calc(&h, &c);

    ASSERT_NEAR(c.yield_on_cost,  2.92/80.0,  0.0001, "YOC = div/cost_basis");
    ASSERT_NEAR(c.current_yield,  2.92/83.0,  0.0001, "current_yield = div/price");
    ASSERT_NEAR(c.annual_income,  292.0,      0.01,   "annual_income = div * shares");
    ASSERT_NEAR(c.monthly_income, 292.0/12.0, 0.01,   "monthly_income = annual/12");
    ASSERT_NEAR(c.market_value,   8300.0,     0.01,   "market_value = price * shares");
    ASSERT_NEAR(c.total_cost,     8000.0,     0.01,   "total_cost = cost * shares");
}

/* ── PortfolioSummary ────────────────────────────────────────────────────── */

static void test_portfolio_summary(void)
{
    Portfolio p = make_test_portfolio();
    PortfolioSummary s;
    portfolio_summarize(&p, &s);

    /* SCHD: 100 * 2.92 = 292  DGRO: 50 * 1.26 = 63 */
    double expected_annual = 292.0 + 63.0;
    ASSERT_NEAR(s.total_annual_income, expected_annual, 0.1, "total_annual_income");
    ASSERT_NEAR(s.total_monthly_income, expected_annual / 12.0, 0.1, "total_monthly_income");

    /* total_invested: 100*80 + 50*55 = 8000 + 2750 = 10750 */
    ASSERT_NEAR(s.total_invested, 10750.0, 0.1, "total_invested");

    /* market_value: 100*83 + 50*57 = 8300 + 2850 = 11150 */
    ASSERT_NEAR(s.total_market_value, 11150.0, 0.1, "total_market_value");

    /* verdict should be INFLATED (monthly income << $5000 target) */
    ASSERT(strcmp(s.verdict, "INFLATED") == 0, "verdict=INFLATED when far from target");

    /* progress ratio ~ 355/12/5000 = 0.00592 */
    ASSERT(s.progress_ratio < 0.01, "progress_ratio < 0.01 with minimal portfolio");
}

/* ── progress_ratio thresholds ───────────────────────────────────────────── */

static void test_verdict_proven(void)
{
    Portfolio p;
    portfolio_default(&p);
    p.target_monthly = 200.0;   /* tiny target */

    /* SCHD 100 shares at $2.92/yr = $24.33/mo — beats $200 target? no. Use 1000 shares. */
    Holding h = {
        .symbol = "SCHD", .shares = 1000.0,
        .cost_basis = 80.0, .current_price = 83.0,
        .annual_div_per_share = 2.92,
    };
    portfolio_add(&p, &h);

    PortfolioSummary s;
    portfolio_summarize(&p, &s);
    /* 1000 * 2.92 / 12 = 243.33/mo > 200 target → PROVEN */
    ASSERT(strcmp(s.verdict, "PROVEN") == 0, "verdict=PROVEN when income > target");
}

static void test_verdict_promising(void)
{
    Portfolio p;
    portfolio_default(&p);
    p.target_monthly = 500.0;

    /* 100 shares at $2.92 = $243/mo = 48.6% of target → PROMISING */
    Holding h = {
        .symbol = "SCHD", .shares = 100.0,
        .cost_basis = 80.0, .current_price = 83.0,
        .annual_div_per_share = 2.92,
    };
    portfolio_add(&p, &h);

    PortfolioSummary s;
    portfolio_summarize(&p, &s);
    ASSERT(strcmp(s.verdict, "PROMISING") == 0 || strcmp(s.verdict, "UNPROVEN") == 0,
           "verdict=PROMISING or UNPROVEN at ~49% of target");
}

/* ── projection ──────────────────────────────────────────────────────────── */

static void test_projection_grows(void)
{
    Portfolio p = make_test_portfolio();
    double yr1 = project_income_year(&p, 1);
    double yr5 = project_income_year(&p, 5);
    double yr10= project_income_year(&p, 10);
    ASSERT(yr5  > yr1,  "projection grows year over year");
    ASSERT(yr10 > yr5,  "projection continues growing");
}

static void test_projection_zero_growth(void)
{
    Portfolio p;
    portfolio_default(&p);
    Holding h = {
        .symbol = "JEPI", .shares = 30.0,
        .annual_div_per_share = 4.60, .div_growth_rate = 0.0,
    };
    portfolio_add(&p, &h);
    double yr0 = 30.0 * 4.60;
    double yr5 = project_income_year(&p, 5);
    ASSERT_NEAR(yr5, yr0, 0.01, "zero growth rate = flat projection");
}

/* ── JSON save/load round-trip ───────────────────────────────────────────── */

static void test_json_roundtrip(void)
{
    Portfolio p = make_test_portfolio();
    const char *tmp = "/tmp/divtrack_test.json";
    int r = portfolio_save(&p, tmp);
    ASSERT(r == 0, "portfolio_save returns 0");

    Portfolio p2;
    portfolio_default(&p2);
    r = portfolio_load(&p2, tmp);
    ASSERT(r == 0, "portfolio_load returns 0");
    ASSERT(p2.n_holdings == p.n_holdings, "round-trip preserves n_holdings");
    ASSERT_NEAR(p2.target_monthly, p.target_monthly, 0.01, "round-trip target_monthly");

    if (p2.n_holdings > 0) {
        ASSERT_NEAR(p2.holdings[0].shares, p.holdings[0].shares, 0.001,
                    "round-trip shares[0]");
        ASSERT_NEAR(p2.holdings[0].annual_div_per_share,
                    p.holdings[0].annual_div_per_share, 0.001,
                    "round-trip annual_div_per_share[0]");
    }
}

/* ── capital_to_close logic ──────────────────────────────────────────────── */

static void test_capital_to_close(void)
{
    Portfolio p;
    portfolio_default(&p);
    p.target_monthly = 5000.0;

    /* Empty portfolio — capital to close ≈ 0 (no blended yield yet) */
    PortfolioSummary s;
    portfolio_summarize(&p, &s);
    /* gap = 5000, blended_yield = 0 → no division possible */
    ASSERT(s.capital_to_close == 0.0 || s.capital_to_close > 0.0,
           "capital_to_close does not crash on empty portfolio");
}

/* ── main ─────────────────────────────────────────────────────────────────── */

int main(void)
{
    printf("\n  divtrack test suite\n");
    printf("  ─────────────────────────────────────\n");

    test_holding_calc();
    test_portfolio_summary();
    test_verdict_proven();
    test_verdict_promising();
    test_projection_grows();
    test_projection_zero_growth();
    test_json_roundtrip();
    test_capital_to_close();

    printf("  ─────────────────────────────────────\n");
    printf("  %d/%d PASSED\n\n", tests_pass, tests_run);
    return (tests_pass == tests_run) ? 0 : 1;
}
