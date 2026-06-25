/*
 * omni_calc.c  —  SAGCO OmniCalculator: Mechanical Advantage Compiler
 *
 * Pipeline:  Source text → Lexer → Parser → Evaluator → Enumerator
 *
 * Compile:   gcc omni_calc.c -o omni_calc -lm
 * REPL:      ./omni_calc
 * One-shot:  ./omni_calc "zdrag 500lbs 10%"
 * Batch:     ./omni_calc < problems.txt
 *
 * Commands:
 *   zdrag    <load> [friction%]                  3:1 Z-drag
 *   crig     <load> [friction%]                  3:1 C-rig
 *   simple   <n>[:1]  <load> [friction%]         n:1 simple (any n ≥ 2)
 *   compound <m>[:1] <n>[:1] <load> [f%]         m:1 piggybacked on n:1
 *   cascade  <a>[:1] [+] <b>[:1] <load> [f%]     a:1 pulling on b:1 haul line
 *   travel   <n>[:1]  [distance_ft]               rope movement per load displacement
 *   solve    <load> [max_input] [f%]              enumerate valid systems
 *   anchor   <n>[:1]  <load> [f%]                anchor load for n:1
 *   lever    <effort_arm> <load_arm> <load>          lever/fulcrum MA
 *   fos      <breaking_strength> <applied_load>      factor of safety
 *   bridle   <included_angle_deg> <load>             2-leg sling tension
 *   pipe_span <od_in> <wall_in> <len_ft> [fluid_sg]  pipe weight + span reaction
 *   bearing  <lat1> <lon1> : <lat2> <lon2>           GPS bearing + distance (ft)
 *   euclid   x1 [y1 [z1]] : x2 [y2 [z2]]            Euclidean distance 1–4D
 *   list                                             show all built-in systems
 *   help
 *
 * Load units:  lbs  kg  kn  n   (default: lbs)
 * Friction:    % per sheave      (default: 9%)
 *
 * Examples:
 *   zdrag 500lbs 10%
 *   cascade 6 4 1000lbs 9%
 *   bridle 90 2000lbs
 *   pipe_span 10.75 0.365 20 1.0
 *   fos 9600 1200
 *   lever 6 2 500lbs
 *   bearing 27.8 -97.583 : 27.801 -97.582
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <math.h>
#include <unistd.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define VERSION          "0.2"
#define DEFAULT_FRICTION 0.09     /* 9% loss per sheave = 91% efficiency */
#define MAX_TLEN         64

/* ════════════════════════════════════════════════════════════════════════════
   LEXER
   ════════════════════════════════════════════════════════════════════════════ */

typedef enum {
    TK_NUM, TK_IDENT, TK_COLON, TK_PLUS, TK_EQ,
    TK_PCT, TK_LPAREN, TK_RPAREN, TK_EOF, TK_ERR
} TKind;

typedef struct { TKind k; char s[MAX_TLEN]; double v; } Tok;

static const char *lex_p;

static Tok lex_next(void) {
    Tok t; memset(&t, 0, sizeof t);
    /* skip whitespace and comma separators */
    while (*lex_p == ' ' || *lex_p == '\t' || *lex_p == ',') lex_p++;
    if (!*lex_p || *lex_p == '\n' || *lex_p == ';' || *lex_p == '\r') {
        t.k = TK_EOF; return t;
    }
    if (*lex_p == '#') {                        /* line comment */
        while (*lex_p && *lex_p != '\n') lex_p++;
        t.k = TK_EOF; return t;
    }
    switch (*lex_p) {
        case ':': t.k=TK_COLON;  t.s[0]=':'; lex_p++; return t;
        case '+': t.k=TK_PLUS;   t.s[0]='+'; lex_p++; return t;
        case '=': t.k=TK_EQ;     t.s[0]='='; lex_p++; return t;
        case '%': t.k=TK_PCT;    t.s[0]='%'; lex_p++; return t;
        case '(': t.k=TK_LPAREN; t.s[0]='('; lex_p++; return t;
        case ')': t.k=TK_RPAREN; t.s[0]=')'; lex_p++; return t;
    }
    /* negative numbers: '-' immediately followed by digit or dot+digit */
    if (*lex_p == '-' && (isdigit(lex_p[1]) ||
                          (lex_p[1] == '.' && isdigit(lex_p[2])))) {
        int i = 0;
        t.s[i++] = *lex_p++;
        while ((isdigit(*lex_p) || *lex_p == '.') && i < MAX_TLEN-1)
            t.s[i++] = *lex_p++;
        t.s[i] = 0; t.v = atof(t.s); t.k = TK_NUM;
        return t;
    }
    if (isdigit(*lex_p) || (*lex_p == '.' && isdigit(lex_p[1]))) {
        int i = 0;
        while ((isdigit(*lex_p) || *lex_p == '.') && i < MAX_TLEN-1)
            t.s[i++] = *lex_p++;
        t.s[i] = 0; t.v = atof(t.s); t.k = TK_NUM;
        return t;
    }
    if (isalpha(*lex_p) || *lex_p == '_') {
        int i = 0;
        while ((isalnum(*lex_p) || *lex_p == '_') && i < MAX_TLEN-1)
            t.s[i++] = tolower(*lex_p++);
        t.s[i] = 0; t.k = TK_IDENT;
        return t;
    }
    t.k = TK_ERR; t.s[0] = *lex_p++; return t;
}

/* single-token lookahead */
static Tok cur;
static void advance(void) { cur = lex_next(); }

static int accept(TKind k) {
    if (cur.k == k) { advance(); return 1; }
    return 0;
}

/* ════════════════════════════════════════════════════════════════════════════
   QUANTITY PARSER  (number + optional unit)
   ════════════════════════════════════════════════════════════════════════════ */

typedef enum { U_LBS, U_KG, U_KN, U_N, U_NONE } Unit;

static Unit parse_unit(void) {
    if (cur.k != TK_IDENT) return U_NONE;
    const char *s = cur.s;
    if (!strcmp(s,"lbs")||!strcmp(s,"lb")||!strcmp(s,"pounds")) { advance(); return U_LBS; }
    if (!strcmp(s,"kg") ||!strcmp(s,"kilograms"))               { advance(); return U_KG;  }
    if (!strcmp(s,"kn") ||!strcmp(s,"kilonewtons"))             { advance(); return U_KN;  }
    if (!strcmp(s,"n")  ||!strcmp(s,"newtons"))                 { advance(); return U_N;   }
    return U_NONE;
}

static double to_lbs(double v, Unit u) {
    switch (u) {
        case U_KG: return v * 2.20462;
        case U_KN: return v * 224.809;
        case U_N:  return v * 0.224809;
        default:   return v;            /* lbs or unitless → treat as lbs */
    }
}

/* parse load → lbs.  Returns -1 on failure. */
static double parse_load(void) {
    if (cur.k != TK_NUM) return -1.0;
    double v = cur.v; advance();
    return to_lbs(v, parse_unit());
}

/* parse friction → 0..1.  Returns DEFAULT_FRICTION on failure. */
static double parse_friction(void) {
    if (cur.k != TK_NUM) return DEFAULT_FRICTION;
    double v = cur.v; advance();
    accept(TK_PCT);                     /* eat optional % */
    if (cur.k == TK_IDENT &&
        (!strcmp(cur.s,"pct") || !strcmp(cur.s,"percent"))) advance();
    return (v > 1.0) ? v / 100.0 : v;  /* 9 → 0.09,  0.09 → 0.09 */
}

/* parse MA ratio: <n>  or  <n>:1  →  integer n */
static int parse_ma(void) {
    if (cur.k != TK_NUM) return -1;
    int n = (int)cur.v; advance();
    if (cur.k == TK_COLON) {
        advance();
        if (cur.k == TK_NUM && (int)cur.v == 1) advance(); /* eat the "1" */
    }
    return n;
}

/* ════════════════════════════════════════════════════════════════════════════
   PHYSICS ENGINE
   ════════════════════════════════════════════════════════════════════════════ */

typedef struct {
    char   name[80];
    double load;          /* lbs                         */
    int    ma_theo;       /* theoretical MA              */
    int    n_sheaves;     /* total sheaves in system     */
    double friction;      /* per-sheave loss, 0–1        */
    double efficiency;    /* overall system efficiency   */
    double actual_ma;     /* effective MA after friction */
    double haul_force;    /* force applied at rope end   */
    double anchor_load;   /* tension at fixed anchor     */
} Result;

/*
 * System efficiency:  η_sys = (1 − f)^n
 *   where f = per-sheave friction loss (e.g. 0.09 for 9%)
 *         n = number of sheaves in the path
 *
 * Actual MA:          MA_act = MA_theo × η_sys
 * Haul force:         F_haul = W / MA_act
 * Anchor load:        F_anchor ≈ W + F_haul  (in-line, worst-case)
 *   (real value depends on geometry; this is conservative)
 *
 * Simple n:1 sheave count:  n_sheaves = n − 1
 *   (e.g. 3:1 Z-drag has 2 sheaves: 1 movable + 1 redirect)
 *
 * Compound m:1 on n:1:
 *   MA_theo  = m × n
 *   sheaves  = (m−1) + (n−1)
 */

static Result calc(const char *name, double load, int ma_theo,
                   int n_sheaves, double friction) {
    Result r;
    strncpy(r.name, name, sizeof r.name - 1);
    r.load       = load;
    r.ma_theo    = ma_theo;
    r.n_sheaves  = n_sheaves;
    r.friction   = friction;
    r.efficiency = pow(1.0 - friction, n_sheaves);
    r.actual_ma  = ma_theo * r.efficiency;
    r.haul_force = (r.actual_ma > 0.0) ? load / r.actual_ma : 0.0;
    r.anchor_load = load + r.haul_force;   /* conservative in-line */
    return r;
}

/* ─── Built-in system templates (for enumerator) ──────────────────────── */

typedef struct {
    const char *name;
    int         ma;
    int         sheaves;
    const char *desc;
} SysTpl;

static const SysTpl SYSTEMS[] = {
    { "2:1",       2,  1, "Single movable pulley"          },
    { "Z-DRAG",    3,  2, "Z-drag / 3:1 haul (2 sheaves)"  },
    { "C-RIG",     3,  2, "C-rig / 3:1 alternative"        },
    { "4:1",       4,  3, "4:1 simple (3 sheaves)"         },
    { "5:1",       5,  4, "5:1 simple (4 sheaves)"         },
    { "6:1",       6,  5, "6:1 simple (5 sheaves)"         },
    { "3:1+3:1",   9,  4, "Compound 3:1 on 3:1 = 9:1"      },
    { "3:1+5:1",  15,  6, "Compound 3:1 on 5:1 = 15:1"     },
    { "5:1+3:1",  15,  6, "Compound 5:1 on 3:1 = 15:1"     },
    { "5:1+5:1",  25,  8, "Compound 5:1 on 5:1 = 25:1"     },
};
#define N_SYS (int)(sizeof(SYSTEMS)/sizeof(SYSTEMS[0]))

/* ════════════════════════════════════════════════════════════════════════════
   OUTPUT
   ════════════════════════════════════════════════════════════════════════════ */

static void print_result(const Result *r) {
    printf("\n");
    printf("  ┌─ %-44s ─┐\n", r->name);
    printf("  │  Load            %8.1f lbs  (%6.1f kg)        │\n",
           r->load, r->load / 2.20462);
    printf("  │  MA  theoretical    %3d:1                             │\n",
           r->ma_theo);
    printf("  │  Sheaves            %3d                               │\n",
           r->n_sheaves);
    printf("  │  Friction/sheave  %5.1f%%                             │\n",
           r->friction * 100.0);
    printf("  │  System eff.      %5.1f%%                             │\n",
           r->efficiency * 100.0);
    printf("  │  MA  actual       %5.2f:1                            │\n",
           r->actual_ma);
    printf("  │  ─────────────────────────────────────────────────  │\n");
    printf("  │  HAUL FORCE      %8.1f lbs  (%6.1f kg) ← apply │\n",
           r->haul_force, r->haul_force / 2.20462);
    printf("  │  ANCHOR LOAD     %8.1f lbs  (%6.1f kg) ← rig   │\n",
           r->anchor_load, r->anchor_load / 2.20462);
    printf("  └────────────────────────────────────────────────────┘\n\n");
}

static void print_enum_row(const SysTpl *s, const Result *r, int fits) {
    printf("  %c  %-11s  %3d:1  %2d shv  haul=%6.1f lbs  anch=%7.1f lbs  %s\n",
           fits ? '*' : ' ',
           s->name, s->ma, s->sheaves,
           r->haul_force, r->anchor_load, s->desc);
}

/* ════════════════════════════════════════════════════════════════════════════
   COMMAND HANDLERS
   ════════════════════════════════════════════════════════════════════════════ */

static void cmd_zdrag(void) {
    double load = parse_load();
    if (load < 0) { fprintf(stderr, "zdrag: expected load\n"); return; }
    double fric = (cur.k == TK_NUM) ? parse_friction() : DEFAULT_FRICTION;
    Result r = calc("Z-DRAG  3:1", load, 3, 2, fric);
    print_result(&r);
}

static void cmd_crig(void) {
    double load = parse_load();
    if (load < 0) { fprintf(stderr, "crig: expected load\n"); return; }
    double fric = (cur.k == TK_NUM) ? parse_friction() : DEFAULT_FRICTION;
    Result r = calc("C-RIG  3:1", load, 3, 2, fric);
    print_result(&r);
}

static void cmd_simple(void) {
    int ma = parse_ma();
    if (ma < 2) { fprintf(stderr, "simple: expected MA ≥ 2  (e.g. 5  or  5:1)\n"); return; }
    double load = parse_load();
    if (load < 0) { fprintf(stderr, "simple: expected load\n"); return; }
    double fric = (cur.k == TK_NUM) ? parse_friction() : DEFAULT_FRICTION;
    char name[64]; snprintf(name, sizeof name, "SIMPLE  %d:1", ma);
    Result r = calc(name, load, ma, ma - 1, fric);
    print_result(&r);
}

static void cmd_compound(void) {
    int base = parse_ma();
    if (base < 2) { fprintf(stderr, "compound: expected base MA\n"); return; }
    accept(TK_PLUS);               /* optional + between the two ratios */
    int rider = parse_ma();
    if (rider < 2) { fprintf(stderr, "compound: expected rider MA\n"); return; }
    double load = parse_load();
    if (load < 0) { fprintf(stderr, "compound: expected load\n"); return; }
    double fric = (cur.k == TK_NUM) ? parse_friction() : DEFAULT_FRICTION;

    int ma_theo  = base * rider;
    int n_sheaves = (base - 1) + (rider - 1);
    char name[64];
    snprintf(name, sizeof name, "COMPOUND  %d:1 + %d:1 = %d:1", base, rider, ma_theo);
    Result r = calc(name, load, ma_theo, n_sheaves, fric);
    print_result(&r);
}

static void cmd_anchor(void) {
    int ma = parse_ma();
    if (ma < 2) { fprintf(stderr, "anchor: expected MA ≥ 2\n"); return; }
    double load = parse_load();
    if (load < 0) { fprintf(stderr, "anchor: expected load\n"); return; }
    double fric = (cur.k == TK_NUM) ? parse_friction() : DEFAULT_FRICTION;
    char name[64]; snprintf(name, sizeof name, "ANCHOR for %d:1", ma);
    Result r = calc(name, load, ma, ma - 1, fric);

    printf("\n  ANCHOR LOAD  ─  %d:1  @ %.1f lbs  (%.1f%% friction/sheave)\n",
           ma, load, fric * 100.0);
    printf("  ───────────────────────────────────────────────────────\n");
    printf("  MA actual      : %.2f:1\n",   r.actual_ma);
    printf("  Haul force     : %.1f lbs  (%.1f kg)\n",
           r.haul_force, r.haul_force / 2.20462);
    printf("  ANCHOR LOAD    : %.1f lbs  (%.1f kg)\n",
           r.anchor_load, r.anchor_load / 2.20462);
    printf("  ─  (in-line estimate: anchor = load + haul_force)\n\n");
}

static void cmd_solve(void) {
    double load = parse_load();
    if (load < 0) { fprintf(stderr, "solve: expected load\n"); return; }
    double max_haul = 150.0;
    if (cur.k == TK_NUM) max_haul = parse_load();   /* accepts lbs/kg */
    double fric = (cur.k == TK_NUM) ? parse_friction() : DEFAULT_FRICTION;

    printf("\n  ENUMERATE  load=%.1f lbs  max_input=%.1f lbs  friction=%.1f%%/sheave\n",
           load, max_haul, fric * 100.0);
    printf("  ──────────────────────────────────────────────────────────────────────\n");
    printf("  *  system       MA   shv  haul          anchor        notes\n");
    printf("  ──────────────────────────────────────────────────────────────────────\n");

    int any = 0;
    for (int i = 0; i < N_SYS; i++) {
        Result r = calc(SYSTEMS[i].name, load,
                        SYSTEMS[i].ma, SYSTEMS[i].sheaves, fric);
        int fits = (r.haul_force <= max_haul);
        print_enum_row(&SYSTEMS[i], &r, fits);
        if (fits) any++;
    }

    printf("  ──────────────────────────────────────────────────────────────────────\n");
    if (any)
        printf("  %d system(s) marked * achieve haul ≤ %.1f lbs\n\n", any, max_haul);
    else
        printf("  ⚠  No standard system achieves target — try a compound system\n\n");
}

/*
 * CASCADE  —  System A pulling on System B's haul line.
 *
 * This is different from a simple piggyback (compound):
 *   - Two physically separate systems connected in series
 *   - System B is anchored to the load
 *   - System B's haul line feeds into System A's load point
 *   - System A is anchored to a fixed point
 *   - Human pulls System A's haul end
 *
 * Force path:
 *   F_input → [System A  MA_a × η_a] → [System B  MA_b × η_b] → Load
 *
 * F_between = F_input × MA_a × η_a          (force between the two stages)
 * F_load    = F_between × MA_b × η_b
 *           = F_input × (MA_a × MA_b) × (η_a × η_b)
 *
 * Rope travel per unit of load movement:
 *   load moves 1 ft → System B haul end moves MA_b ft
 *   System B haul end (= System A load) moves 1 ft → haul rope moves MA_a ft
 *   ∴  human pulls  MA_a × MA_b  ft  per  1 ft  of load travel
 *
 * Motion begins when:
 *   F_input ≥ Load / (MA_a × MA_b × η_total)  [dynamic]
 *   Add ~15% for static breakaway friction.
 */
static void cmd_cascade(void) {
    int ma_a = parse_ma();
    if (ma_a < 2) { fprintf(stderr, "cascade: expected MA for system A  (e.g. 6)\n"); return; }
    accept(TK_PLUS);
    int ma_b = parse_ma();
    if (ma_b < 2) { fprintf(stderr, "cascade: expected MA for system B  (e.g. 4)\n"); return; }
    double load = parse_load();
    if (load < 0) { fprintf(stderr, "cascade: expected load\n"); return; }
    double fric = (cur.k == TK_NUM) ? parse_friction() : DEFAULT_FRICTION;

    int    shv_a   = ma_a - 1;
    int    shv_b   = ma_b - 1;
    double eta_a   = pow(1.0 - fric, shv_a);
    double eta_b   = pow(1.0 - fric, shv_b);
    double ma_act_a = ma_a * eta_a;
    double ma_act_b = ma_b * eta_b;

    int    ma_total_theo = ma_a * ma_b;
    double eta_total     = eta_a * eta_b;
    double ma_total_act  = ma_total_theo * eta_total;

    double f_input     = load / ma_total_act;
    double f_between   = f_input * ma_act_a;   /* tension in the line joining A→B */
    double rope_per_ft = (double)(ma_a * ma_b); /* ft of rope per ft of load travel */

    /* static breakaway: ~15% more than dynamic (stiction) */
    double f_static = f_input * 1.15;
    /*
     * Anchor loads (in-line, conservative):
     *   System B (inner, load side): its fixed anchor bears load + f_between
     *     because the rope from load + the haul from A both pull on B's anchor.
     *   System A (outer, haul side): its fixed anchor bears f_between + f_input
     *     because the "load" for A is f_between, and human pulls f_input.
     */
    double anchor_b = load     + f_between;  /* primary (load-side) anchor */
    double anchor_a = f_between + f_input;   /* secondary (haul-side) anchor */

    printf("\n");
    printf("  CASCADE  %d:1 pulling on %d:1  —  load = %.1f lbs"
           "  friction = %.1f%%/sheave\n",
           ma_a, ma_b, load, fric * 100.0);
    printf("  ═══════════════════════════════════════════════════════════════\n");
    printf("  Force path:\n");
    printf("    Human ──► [%d:1  η=%.0f%%] ──► [%d:1  η=%.0f%%] ──► LOAD\n",
           ma_a, eta_a * 100.0, ma_b, eta_b * 100.0);
    printf("\n");
    printf("  Gain stages:\n");
    printf("    Stage A (outer %d:1)   %2d sheaves  eff=%.2f  MA_act=%.2f:1\n",
           ma_a, shv_a, eta_a, ma_act_a);
    printf("    Stage B (inner %d:1)   %2d sheaves  eff=%.2f  MA_act=%.2f:1\n",
           ma_b, shv_b, eta_b, ma_act_b);
    printf("    ─────────────────────────────────────────────────────────────\n");
    printf("    TOTAL  %2d:1 theoretical  /  %.2f:1 actual  (%.0f%% overall eff)\n",
           ma_total_theo, ma_total_act, eta_total * 100.0);
    printf("\n");
    printf("  Forces:\n");
    printf("    Input  (human)       %8.1f lbs  (%6.1f kg)  ← you pull this\n",
           f_input,   f_input   / 2.20462);
    printf("    Between stages       %8.1f lbs  (%6.1f kg)  ← A output = B haul\n",
           f_between, f_between / 2.20462);
    printf("    At load              %8.1f lbs  (%6.1f kg)\n",
           load,      load      / 2.20462);
    printf("\n");
    printf("  Rope travel per 1 ft of load movement:\n");
    printf("    System B haul end    %6.1f ft\n", (double)ma_b);
    printf("    Human haul rope      %6.1f ft  ← how much you pull\n", rope_per_ft);
    printf("\n");
    printf("  Motion threshold:\n");
    printf("    Dynamic (moving)     %8.1f lbs  — system moves once past this\n", f_input);
    printf("    Static  (breakaway)  %8.1f lbs  — first pull to unstick load\n", f_static);
    printf("    Everything moves simultaneously when F_input ≥ %.1f lbs\n", f_static);
    printf("\n");
    printf("  Anchor loads (in-line estimate):\n");
    printf("    System B anchor (load side)  %7.1f lbs  (%6.1f kg)"
           "  ← load + between\n",
           anchor_b, anchor_b / 2.20462);
    printf("    System A anchor (haul side)  %7.1f lbs  (%6.1f kg)"
           "  ← between + input\n",
           anchor_a, anchor_a / 2.20462);
    printf("  ═══════════════════════════════════════════════════════════════\n\n");
}

/* TRAVEL  —  rope movement for a given load displacement */
static void cmd_travel(void) {
    int ma = parse_ma();
    if (ma < 2) { fprintf(stderr, "travel: expected MA  (e.g. 5  or  5:1)\n"); return; }
    double dist = 1.0;
    if (cur.k == TK_NUM) { dist = cur.v; advance(); accept(TK_IDENT); /* eat ft/m */ }

    printf("\n  ROPE TRAVEL  —  %d:1  system  (load moves %.2f ft)\n", ma, dist);
    printf("  ──────────────────────────────────────────────────\n");
    printf("  Haul rope to pull   : %.2f ft  (%.0f in)\n",
           ma * dist, ma * dist * 12.0);
    printf("  Rope-to-load ratio  : %d:1   (pull %d ft → load moves 1 ft)\n", ma, ma);
    printf("  Load displacement   : %.2f ft\n", dist);
    printf("\n");
    printf("  Progress capture reset cycle:\n");
    printf("    each reset feeds the stroke length of your device\n");
    printf("    strokes needed ≈ %.0f  (assuming 12 in stroke)\n",
           ma * dist);
    printf("  ──────────────────────────────────────────────────\n\n");
}

static void cmd_list(void) {
    printf("\n  Built-in system templates:\n");
    printf("  %-12s  %4s  %8s  Description\n", "Name", "MA", "Sheaves");
    printf("  ─────────────────────────────────────────────────────\n");
    for (int i = 0; i < N_SYS; i++) {
        printf("  %-12s  %3d:1  %7d  %s\n",
               SYSTEMS[i].name, SYSTEMS[i].ma,
               SYSTEMS[i].sheaves, SYSTEMS[i].desc);
    }
    printf("\n");
}

/*
 * EUCLID  —  Euclidean distance in 1–4 dimensions.
 *
 * Formula (n-dimensional generalization of Pythagorean theorem):
 *   d(p, q) = sqrt( Σᵢ (qᵢ − pᵢ)² )
 *
 * Syntax (up to 4 coordinates per point, missing ones default to 0):
 *   euclid  x1 [y1 [z1 [w1]]]  :  x2 [y2 [z2 [w2]]]
 *
 * Field uses:
 *   - Rope length between two anchor points in 3D space
 *   - Diagonal distance across a work area
 *   - Multi-point rigging triangle perimeters
 *
 * With 3 points, also computes all three pairwise distances and
 * the triangle perimeter (useful for load triangle rigging).
 */
static void cmd_euclid(void) {
    /* parse up to 4 coordinates for point 1, then ':', then point 2 */
    double p[4] = {0,0,0,0}, q[4] = {0,0,0,0};
    int    dim = 0;

    /* point 1 coords until we hit ':' or EOF */
    while (cur.k == TK_NUM && dim < 4) {
        p[dim++] = cur.v; advance();
        accept(TK_IDENT);  /* eat optional unit like ft/m */
    }
    if (dim == 0) { fprintf(stderr, "euclid: expected coordinates\n"); return; }

    if (!accept(TK_COLON)) {
        /* if no ':', maybe it was "euclid x1 y1 x2 y2" space-separated style */
        int half = dim / 2;
        if (dim >= 2 && dim % 2 == 0) {
            for (int i = 0; i < half; i++) { q[i] = p[half + i]; p[half + i] = 0; }
            dim = half;
        } else {
            fprintf(stderr, "euclid: use  x1 [y1 [z1]] : x2 [y2 [z2]]\n");
            return;
        }
    } else {
        /* read point 2 with same dimensionality */
        int j = 0;
        while (cur.k == TK_NUM && j < dim) {
            q[j++] = cur.v; advance();
            accept(TK_IDENT);
        }
        /* fill remaining with 0 if fewer coords given for point 2 */
    }

    /* optional third point */
    double r[4] = {0,0,0,0}; int has_r = 0;
    if (accept(TK_COLON) && cur.k == TK_NUM) {
        has_r = 1;
        int j = 0;
        while (cur.k == TK_NUM && j < dim) {
            r[j++] = cur.v; advance(); accept(TK_IDENT);
        }
    }

    /* compute pairwise distances */
    double sum_pq = 0, sum_qr = 0, sum_pr = 0;
    for (int i = 0; i < dim; i++) {
        sum_pq += (q[i]-p[i])*(q[i]-p[i]);
        if (has_r) {
            sum_qr += (r[i]-q[i])*(r[i]-q[i]);
            sum_pr += (r[i]-p[i])*(r[i]-p[i]);
        }
    }
    double d_pq = sqrt(sum_pq);
    double d_qr = has_r ? sqrt(sum_qr) : 0;
    double d_pr = has_r ? sqrt(sum_pr) : 0;

    /* label coordinates based on dimension */
    const char *axes[] = {"x","y","z","w"};

    printf("\n  EUCLIDEAN DISTANCE  (%dD)\n", dim);
    printf("  ────────────────────────────────────────────────────\n");

    printf("  Point P  ( ");
    for (int i = 0; i < dim; i++) printf("%s=%.3g%s", axes[i], p[i], i<dim-1?" ":"");
    printf(" )\n");

    printf("  Point Q  ( ");
    for (int i = 0; i < dim; i++) printf("%s=%.3g%s", axes[i], q[i], i<dim-1?" ":"");
    printf(" )\n");

    if (has_r) {
        printf("  Point R  ( ");
        for (int i = 0; i < dim; i++) printf("%s=%.3g%s", axes[i], r[i], i<dim-1?" ":"");
        printf(" )\n");
    }

    printf("\n");

    /* formula display */
    printf("  d(P,Q) = √(");
    for (int i = 0; i < dim; i++) {
        double diff = q[i] - p[i];
        printf("(%.3g)²%s", diff, i<dim-1?"+":"");
    }
    printf(")\n");
    printf("         = %.6g\n", d_pq);

    if (has_r) {
        printf("\n");
        printf("  d(P,Q) = %10.6g\n", d_pq);
        printf("  d(Q,R) = %10.6g\n", d_qr);
        printf("  d(P,R) = %10.6g\n", d_pr);
        printf("  ────────────────────────────────────────\n");
        printf("  Perimeter (triangle) = %.6g\n", d_pq + d_qr + d_pr);
    }

    printf("  ────────────────────────────────────────────────────\n\n");
}

/*
 * LEVER  —  lever / fulcrum mechanical advantage.
 *
 * MA        = effort_arm / load_arm
 * F_effort  = load / MA  =  load × (load_arm / effort_arm)
 * F_fulcrum = load + F_effort   (reaction at pivot, Class 1/2)
 *
 * Both arm values must be in the same unit (ft, in, m).
 * MA > 1 when effort arm is longer than load arm.
 *
 * Syntax:  lever <effort_arm> <load_arm> <load>
 */
static void cmd_lever(void) {
    if (cur.k != TK_NUM) { fprintf(stderr, "lever: expected effort arm\n"); return; }
    double effort_arm = cur.v; advance(); accept(TK_IDENT);
    if (effort_arm <= 0) { fprintf(stderr, "lever: effort arm must be > 0\n"); return; }

    if (cur.k != TK_NUM) { fprintf(stderr, "lever: expected load arm\n"); return; }
    double load_arm = cur.v; advance(); accept(TK_IDENT);
    if (load_arm <= 0) { fprintf(stderr, "lever: load arm must be > 0\n"); return; }

    double load = parse_load();
    if (load <= 0) { fprintf(stderr, "lever: expected load\n"); return; }

    double ma        = effort_arm / load_arm;
    double f_effort  = load / ma;
    double f_fulcrum = load + f_effort;

    printf("\n  LEVER  effort_arm=%.3g  load_arm=%.3g  load=%.1f lbs\n",
           effort_arm, load_arm, load);
    printf("  ─────────────────────────────────────────────────────────\n");
    printf("  MA (effort / load arm)   : %.4f:1\n", ma);
    printf("  Effort required          : %8.1f lbs  (%6.1f kg)  ← you apply\n",
           f_effort, f_effort / 2.20462);
    printf("  Fulcrum reaction         : %8.1f lbs  (%6.1f kg)\n",
           f_fulcrum, f_fulcrum / 2.20462);
    printf("\n");
    if (ma >= 1.0)
        printf("  ✓  MA %.2f — apply %.1f lbs to move %.1f lbs\n",
               ma, f_effort, load);
    else
        printf("  ⚠  MA < 1 — load arm longer than effort arm (force amplifier, speed reducer)\n");
    printf("  ─────────────────────────────────────────────────────────\n\n");
}

/*
 * FOS  —  factor of safety / working load limit.
 *
 * FOS = breaking_strength / applied_load
 *
 * Reference minimums (conservative side):
 *   OSHA 1926.251 personnel hoisting  : 10:1
 *   OSHA 1926.251 materials rigging   :  5:1
 *   ASME B30.9 slings (general)       :  5:1
 *   Wire rope general rigging         :  5:1
 *   Chain slings                      :  4:1
 *
 * Syntax:  fos <breaking_strength> <applied_load>
 */
static void cmd_fos(void) {
    double bs = parse_load();
    if (bs <= 0) { fprintf(stderr, "fos: expected breaking strength\n"); return; }
    double applied = parse_load();
    if (applied <= 0) { fprintf(stderr, "fos: expected applied load\n"); return; }

    double fos  = bs / applied;
    double wll5 = bs / 5.0;
    double wll4 = bs / 4.0;

    printf("\n  FACTOR OF SAFETY\n");
    printf("  ─────────────────────────────────────────────────────\n");
    printf("  Breaking strength    : %8.1f lbs  (%6.1f kg)\n", bs, bs / 2.20462);
    printf("  Applied load         : %8.1f lbs  (%6.1f kg)\n", applied, applied / 2.20462);
    printf("  ─────────────────────────────────────────────────────\n");
    printf("  FOS                  : %8.2f:1\n", fos);
    printf("  WLL @ 5:1            : %8.1f lbs  (OSHA materials / ASME B30.9)\n", wll5);
    printf("  WLL @ 4:1            : %8.1f lbs  (chain sling minimum)\n", wll4);
    printf("\n");
    if      (fos >= 10.0) printf("  ✓  PASS  — ≥10:1  (safe for personnel hoisting)\n");
    else if (fos >=  5.0) printf("  ✓  PASS  — ≥5:1   (materials rigging, OSHA 1926.251)\n");
    else if (fos >=  4.0) printf("  ⚠  MARGINAL  — ≥4:1  (chain sling minimum only)\n");
    else                  printf("  ✗  FAIL  — below 4:1  DO NOT USE in life-safety rigging\n");
    printf("  ─────────────────────────────────────────────────────\n\n");
}

/*
 * BRIDLE  —  2-leg symmetric sling tension at included angle.
 *
 * For a 2-leg symmetric bridle, with θ = included angle between legs:
 *   T per leg = load / (2 × cos(θ/2))
 *
 *   θ=0°   → T = load/2     (× 1.000  — vertical, minimum)
 *   θ=60°  → T = load/1.732 (× 0.577  per leg)
 *   θ=90°  → T = load/1.414 (× 0.707  per leg)
 *   θ=120° → T = load        (× 1.000  per leg) ← ASME B30.9 max
 *   θ→180° → T → ∞
 *
 * Rule: never exceed 120° included angle for life-safety rigging.
 * At 120° each leg bears the full load — slings must be rated ≥ load.
 *
 * Syntax:  bridle <included_angle_deg> <load>
 */
static void cmd_bridle(void) {
    if (cur.k != TK_NUM) { fprintf(stderr, "bridle: expected included angle (deg)\n"); return; }
    double angle_deg = cur.v; advance();
    if (cur.k == TK_IDENT &&
        (!strcmp(cur.s,"deg") || !strcmp(cur.s,"degrees"))) advance();

    double load = parse_load();
    if (load <= 0) { fprintf(stderr, "bridle: expected load\n"); return; }

    if (angle_deg <= 0 || angle_deg >= 180.0) {
        fprintf(stderr, "bridle: angle must be 0°–179°  (180° = infinite tension)\n");
        return;
    }

    double half_rad  = (angle_deg / 2.0) * M_PI / 180.0;
    double cos_half  = cos(half_rad);
    double t_per_leg = load / (2.0 * cos_half);

    printf("\n  BRIDLE SLING  —  2-leg symmetric  θ=%.1f° included  load=%.1f lbs\n",
           angle_deg, load);
    printf("  ══════════════════════════════════════════════════════════\n");
    printf("  Half-angle from vertical  : %.2f°\n", angle_deg / 2.0);
    printf("  cos(θ/2)                  : %.4f\n", cos_half);
    printf("  ──────────────────────────────────────────────────────────\n");
    printf("  TENSION PER LEG  : %8.1f lbs  (%6.1f kg)  ← rate each leg ≥ this\n",
           t_per_leg, t_per_leg / 2.20462);
    printf("  Tension × 2 legs : %8.1f lbs  (%6.1f kg)\n",
           2.0 * t_per_leg, 2.0 * t_per_leg / 2.20462);
    printf("\n");

    if (angle_deg <= 60.0)
        printf("  ✓  GOOD  — ≤60°  (low sling stress, preferred)\n");
    else if (angle_deg <= 90.0)
        printf("  ✓  ACCEPTABLE  — ≤90°  (moderate tension increase)\n");
    else if (angle_deg <= 120.0)
        printf("  ⚠  CAUTION  — 90°–120°  (each leg approaching full load)\n");
    else
        printf("  ✗  DANGER  — >120° exceeds ASME B30.9 limit\n");

    printf("\n  Angle table for %.1f lbs:\n", load);
    static const int ANGLES[] = {0, 30, 45, 60, 90, 120, 150};
    for (int i = 0; i < 7; i++) {
        double a = ANGLES[i];
        double t = load / (2.0 * cos((a / 2.0) * M_PI / 180.0));
        printf("    %3.0f° → %8.1f lbs/leg  (×%.3f)%s\n",
               a, t, t / (load / 2.0),
               (fabs(a - angle_deg) < 0.5) ? "  ◄" : "");
    }
    printf("  ══════════════════════════════════════════════════════════\n\n");
}

/*
 * PIPE_SPAN  —  steel pipe dead weight + simply-supported span reaction.
 *
 * Steel pipe weight per foot  (ASME B36.10 standard formula):
 *   W_pipe = 10.68 × (OD − t) × t          [lb/ft]
 *
 * Fluid fill weight per foot  (if SG provided):
 *   ID = OD − 2t
 *   A_bore = π/4 × ID²                     [in²]
 *   W_fluid = A_bore × SG × 0.03613 × 12   [lb/ft]
 *   (0.03613 lb/in³ = density of water; SG scales it)
 *
 * Simply-supported span:
 *   Reaction per end = W_total/ft × L / 2
 *   Midspan moment   = W_total/ft × L² / 8   [ft·lb]
 *
 * Syntax:  pipe_span <od_in> <wall_in> <length_ft> [fluid_sg]
 *   e.g.   pipe_span 10.75 0.365 20 1.0    (10" std bore, 20 ft, water-filled)
 */
static void cmd_pipe_span(void) {
    if (cur.k != TK_NUM) { fprintf(stderr, "pipe_span: expected OD (in)\n"); return; }
    double od = cur.v; advance(); accept(TK_IDENT);

    if (od <= 0) { fprintf(stderr, "pipe_span: OD must be > 0\n"); return; }

    if (cur.k != TK_NUM) { fprintf(stderr, "pipe_span: expected wall thickness (in)\n"); return; }
    double wall = cur.v; advance(); accept(TK_IDENT);

    if (wall <= 0 || wall >= od / 2.0) {
        fprintf(stderr, "pipe_span: wall must be > 0 and < OD/2\n"); return;
    }

    if (cur.k != TK_NUM) { fprintf(stderr, "pipe_span: expected span length (ft)\n"); return; }
    double span = cur.v; advance(); accept(TK_IDENT);

    if (span <= 0) { fprintf(stderr, "pipe_span: span must be > 0\n"); return; }

    double sg = 0.0;
    if (cur.k == TK_NUM) { sg = cur.v; advance(); }

    double id       = od - 2.0 * wall;
    double w_pipe   = 10.68 * (od - wall) * wall;
    double a_bore   = (M_PI / 4.0) * id * id;
    double w_fluid  = a_bore * sg * 0.03613 * 12.0;
    double w_total  = w_pipe + w_fluid;
    double r_end    = w_total * span / 2.0;
    double moment   = w_total * span * span / 8.0;

    printf("\n  PIPE SPAN  OD=%.3f\"  wall=%.3f\"  span=%.1f ft%s\n",
           od, wall, span,
           sg > 0.0 ? "  (fluid-filled)" : "  (empty)");
    printf("  ══════════════════════════════════════════════════════════\n");
    printf("  ID (bore)              : %.3f in\n", id);
    printf("  t/OD ratio             : %.1f%%\n", 100.0 * wall / od);
    printf("\n");
    printf("  Weight per foot:\n");
    printf("    Pipe steel           : %7.2f lb/ft  (ASME B36.10 formula)\n", w_pipe);
    if (sg > 0.0)
        printf("    Fluid (SG %.3f)     : %7.2f lb/ft\n", sg, w_fluid);
    printf("    ─────────────────────────────────────────\n");
    printf("    TOTAL                : %7.2f lb/ft\n", w_total);
    printf("\n");
    printf("  Span loads (simply supported):\n");
    printf("    Total span weight    : %7.1f lbs  (%5.1f kg)\n",
           w_total * span, w_total * span / 2.20462);
    printf("    REACTION PER END     : %7.1f lbs  (%5.1f kg)  ← size each support\n",
           r_end, r_end / 2.20462);
    printf("    Midspan moment       : %7.0f ft·lb\n", moment);
    printf("  ══════════════════════════════════════════════════════════\n\n");
}

/*
 * BEARING  —  true bearing and distance between two GPS coordinates.
 *
 * Forward azimuth (from Haversine / spherical law of cosines):
 *   y = sin(Δλ) · cos(φ₂)
 *   x = cos(φ₁)·sin(φ₂) − sin(φ₁)·cos(φ₂)·cos(Δλ)
 *   θ = atan2(y, x)  → normalize to 0–360°
 *
 * Haversine distance:
 *   a = sin²(Δφ/2) + cos(φ₁)·cos(φ₂)·sin²(Δλ/2)
 *   d = 2 · R · atan2(√a, √(1−a))   R = 20,902,464 ft
 *
 * Syntax:  bearing <lat1> <lon1> : <lat2> <lon2>
 *   (decimal degrees; negative = South/West)
 *   e.g.   bearing 27.8 -97.583 : 27.801 -97.582
 */
static void cmd_bearing(void) {
    if (cur.k != TK_NUM) { fprintf(stderr, "bearing: expected lat1\n"); return; }
    double lat1 = cur.v; advance(); accept(TK_IDENT);

    if (cur.k != TK_NUM) { fprintf(stderr, "bearing: expected lon1\n"); return; }
    double lon1 = cur.v; advance(); accept(TK_IDENT);

    if (!accept(TK_COLON)) {
        fprintf(stderr, "bearing: use  bearing <lat1> <lon1> : <lat2> <lon2>\n");
        return;
    }

    if (cur.k != TK_NUM) { fprintf(stderr, "bearing: expected lat2\n"); return; }
    double lat2 = cur.v; advance(); accept(TK_IDENT);

    if (cur.k != TK_NUM) { fprintf(stderr, "bearing: expected lon2\n"); return; }
    double lon2 = cur.v; advance(); accept(TK_IDENT);

    double phi1 = lat1 * M_PI / 180.0;
    double phi2 = lat2 * M_PI / 180.0;
    double lam1 = lon1 * M_PI / 180.0;
    double lam2 = lon2 * M_PI / 180.0;
    double dphi = phi2 - phi1;
    double dlam = lam2 - lam1;

    double y       = sin(dlam) * cos(phi2);
    double x       = cos(phi1) * sin(phi2) - sin(phi1) * cos(phi2) * cos(dlam);
    double theta   = atan2(y, x) * 180.0 / M_PI;
    double fwd_brg = fmod(theta + 360.0, 360.0);
    double rev_brg = fmod(fwd_brg + 180.0, 360.0);

    double a      = sin(dphi/2)*sin(dphi/2)
                  + cos(phi1)*cos(phi2)*sin(dlam/2)*sin(dlam/2);
    double c      = 2.0 * atan2(sqrt(a), sqrt(1.0 - a));
    double dist_ft = 20902464.0 * c;

    const char *card;
    double b = fwd_brg;
    if      (b <  22.5 || b >= 337.5) card = "N";
    else if (b <  67.5)               card = "NE";
    else if (b < 112.5)               card = "E";
    else if (b < 157.5)               card = "SE";
    else if (b < 202.5)               card = "S";
    else if (b < 247.5)               card = "SW";
    else if (b < 292.5)               card = "W";
    else                              card = "NW";

    printf("\n  BEARING  P1=(%.5f, %.5f)  →  P2=(%.5f, %.5f)\n",
           lat1, lon1, lat2, lon2);
    printf("  ───────────────────────────────────────────────────────\n");
    printf("  Forward bearing     : %7.2f°  (%s)\n", fwd_brg, card);
    printf("  Reciprocal bearing  : %7.2f°\n", rev_brg);
    printf("  Distance            : %7.1f ft  (%.4f mi  /  %.1f m)\n",
           dist_ft, dist_ft / 5280.0, dist_ft * 0.3048);
    printf("  ───────────────────────────────────────────────────────\n\n");
}


static void cmd_help(void) {
    printf(
        "\n  SAGCO OmniCalculator v" VERSION "  ─  Mechanical Advantage + Field Rigging\n\n"
        "  ── Rope / Pulley ────────────────────────────────────────────────────────\n"
        "    zdrag    <load> [fric%%]                  3:1 Z-drag\n"
        "    crig     <load> [fric%%]                  3:1 C-rig\n"
        "    simple   <n>[:1] <load> [fric%%]          n:1 simple (any n≥2)\n"
        "    compound <m>[:1] [+] <n>[:1] <load> [f%%] m:1 piggybacked on n:1\n"
        "    cascade  <a>[:1] [+] <b>[:1] <load> [f%%] a:1 pulling on b:1 haul line\n"
        "    travel   <n>[:1] [dist_ft]                rope travel per load displacement\n"
        "    solve    <load> [max_input] [fric%%]       enumerate valid systems\n"
        "    anchor   <n>[:1] <load> [fric%%]           anchor load for n:1\n"
        "    list                                       show all templates\n\n"
        "  ── Geometry ─────────────────────────────────────────────────────────────\n"
        "    euclid   x1 [y1 [z1]] : x2 [y2 [z2]] [: x3 [y3 [z3]]]\n"
        "                                           Euclidean distance 1–4D\n"
        "    bearing  <lat1> <lon1> : <lat2> <lon2> GPS bearing + distance (ft/mi)\n\n"
        "  ── Rigging / Field ──────────────────────────────────────────────────────\n"
        "    lever    <effort_arm> <load_arm> <load>  lever/fulcrum MA\n"
        "    fos      <breaking_strength> <load>      factor of safety (OSHA ref)\n"
        "    bridle   <included_angle_deg> <load>     2-leg sling tension at angle\n"
        "    pipe_span <od_in> <wall_in> <len_ft> [sg] pipe weight + span reaction\n\n"
        "  Load units:   lbs  kg  kn  n    (default: lbs)\n"
        "  Friction:     %%    per sheave   (default: 9%%)\n\n"
        "  Physics:\n"
        "    η_sys     = (1 − f)^n_sheaves\n"
        "    MA_actual = MA_theoretical × η_sys\n"
        "    F_haul    = load / MA_actual\n"
        "    F_anchor  ≈ load + F_haul   (conservative in-line)\n\n"
        "  Examples:\n"
        "    zdrag 500lbs 10%%\n"
        "    cascade 6 4 1000lbs 9%%\n"
        "    bridle 90 2000lbs\n"
        "    pipe_span 10.75 0.365 20 1.0\n"
        "    fos 9600 1200\n"
        "    lever 6 2 500lbs\n"
        "    bearing 27.8 -97.583 : 27.801 -97.582\n\n"
    );
}

/* ════════════════════════════════════════════════════════════════════════════
   TOP-LEVEL PARSER  (dispatches to command handlers)
   ════════════════════════════════════════════════════════════════════════════ */

/* returns 0 = EOF/empty, 1 = ok, -1 = quit */
static int parse_command(void) {
    if (cur.k == TK_EOF) return 0;
    if (cur.k != TK_IDENT) {
        fprintf(stderr, "expected command keyword, got '%s'\n", cur.s);
        advance(); return 1;
    }

    char cmd[MAX_TLEN]; strncpy(cmd, cur.s, MAX_TLEN - 1); advance();

    if (!strcmp(cmd,"zdrag")    || !strcmp(cmd,"z_drag") ||
        !strcmp(cmd,"z-drag")   || !strcmp(cmd,"zd"))         cmd_zdrag();
    else if (!strcmp(cmd,"crig")|| !strcmp(cmd,"c_rig") ||
             !strcmp(cmd,"c-rig"))                            cmd_crig();
    else if (!strcmp(cmd,"simple")  || !strcmp(cmd,"s"))      cmd_simple();
    else if (!strcmp(cmd,"compound")|| !strcmp(cmd,"comp") ||
             !strcmp(cmd,"c"))                                cmd_compound();
    else if (!strcmp(cmd,"solve")   || !strcmp(cmd,"sl"))      cmd_solve();
    else if (!strcmp(cmd,"anchor")  || !strcmp(cmd,"a"))       cmd_anchor();
    else if (!strcmp(cmd,"cascade") || !strcmp(cmd,"cs"))      cmd_cascade();
    else if (!strcmp(cmd,"travel")  || !strcmp(cmd,"tr"))      cmd_travel();
    else if (!strcmp(cmd,"euclid")  || !strcmp(cmd,"dist") ||
             !strcmp(cmd,"d"))                                 cmd_euclid();
    else if (!strcmp(cmd,"lever")   || !strcmp(cmd,"lv"))      cmd_lever();
    else if (!strcmp(cmd,"fos"))                               cmd_fos();
    else if (!strcmp(cmd,"bridle")  || !strcmp(cmd,"br"))      cmd_bridle();
    else if (!strcmp(cmd,"pipe_span")|| !strcmp(cmd,"pipe") ||
             !strcmp(cmd,"ps"))                                cmd_pipe_span();
    else if (!strcmp(cmd,"bearing") || !strcmp(cmd,"brg"))     cmd_bearing();
    else if (!strcmp(cmd,"list")    || !strcmp(cmd,"ls"))      cmd_list();
    else if (!strcmp(cmd,"help")    || !strcmp(cmd,"?") ||
             !strcmp(cmd,"h"))                                cmd_help();
    else if (!strcmp(cmd,"quit")    || !strcmp(cmd,"exit") ||
             !strcmp(cmd,"q"))                                return -1;
    else {
        fprintf(stderr, "unknown command '%s' — type 'help'\n", cmd);
    }
    return 1;
}

static void run_line(const char *line) {
    lex_p = line;
    advance();
    parse_command();
}

/* ════════════════════════════════════════════════════════════════════════════
   MAIN
   ════════════════════════════════════════════════════════════════════════════ */

int main(int argc, char *argv[]) {
    if (argc > 1) {
        run_line(argv[1]);
        return 0;
    }

    int interactive = isatty(fileno(stdin));

    if (interactive) {
        printf("SAGCO OmniCalculator v%s  —  Mechanical Advantage\n", VERSION);
        printf("type 'help' for commands, 'quit' to exit\n\n");
    }

    char line[512];
    while (1) {
        if (interactive) { printf("omni> "); fflush(stdout); }
        if (!fgets(line, sizeof line, stdin)) break;
        char *nl = strchr(line, '\n'); if (nl) *nl = 0;
        if (!*line || line[0] == '#') continue;

        lex_p = line;
        advance();
        if (parse_command() == -1) break;
    }

    if (interactive) printf("\nomni_calc: done.\n");
    return 0;
}
