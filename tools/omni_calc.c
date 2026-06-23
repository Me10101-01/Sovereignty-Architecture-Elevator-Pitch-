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
 *   zdrag    <load> [friction%]             3:1 Z-drag
 *   crig     <load> [friction%]             3:1 C-rig
 *   simple   <n>[:1]  <load> [friction%]   n:1 simple (any n ≥ 2)
 *   compound <m>[:1] <n>[:1] <load> [f%]   m:1 piggybacked on n:1
 *   solve    <load> [max_input] [f%]        enumerate valid systems
 *   anchor   <n>[:1]  <load> [f%]          anchor load for n:1
 *   list                                    show all built-in systems
 *   help
 *
 * Load units:  lbs  kg  kn  n   (default: lbs)
 * Friction:    % per sheave      (default: 9%)
 *
 * Examples:
 *   zdrag 500lbs 10%
 *   simple 5:1 600lbs 9%
 *   compound 3 3 900lbs 10%
 *   solve 800lbs 150lbs 9%
 *   anchor 3 500lbs 10%
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <math.h>
#include <unistd.h>

#define VERSION          "0.1"
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

static void cmd_help(void) {
    printf(
        "\n  SAGCO OmniCalculator v" VERSION "  ─  Mechanical Advantage\n\n"
        "  Commands:\n"
        "    zdrag    <load> [fric%%]             3:1 Z-drag\n"
        "    crig     <load> [fric%%]             3:1 C-rig\n"
        "    simple   <n>[:1]  <load> [fric%%]   n:1 simple (any n≥2)\n"
        "    compound <m>[:1] [+] <n>[:1] <load> [fric%%]\n"
        "    solve    <load> [max_input] [fric%%] enumerate valid systems\n"
        "    anchor   <n>[:1]  <load> [fric%%]   anchor load for n:1\n"
        "    list                                 show all templates\n"
        "    help   quit\n\n"
        "  Load units:   lbs  kg  kn  n    (default: lbs)\n"
        "  Friction:     %%    per sheave   (default: 9%%)\n\n"
        "  Physics:\n"
        "    η_sys     = (1 − f)^n_sheaves\n"
        "    MA_actual = MA_theoretical × η_sys\n"
        "    F_haul    = load / MA_actual\n"
        "    F_anchor  ≈ load + F_haul   (conservative in-line)\n\n"
        "  Examples:\n"
        "    zdrag 500lbs 10%%\n"
        "    simple 5:1 600lbs 9%%\n"
        "    compound 3 3 900lbs 10%%\n"
        "    solve 800lbs 150lbs 9%%\n"
        "    anchor 3 500lbs 10%%\n\n"
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
    else if (!strcmp(cmd,"solve")   || !strcmp(cmd,"sl"))     cmd_solve();
    else if (!strcmp(cmd,"anchor")  || !strcmp(cmd,"a"))      cmd_anchor();
    else if (!strcmp(cmd,"list")    || !strcmp(cmd,"ls"))     cmd_list();
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
