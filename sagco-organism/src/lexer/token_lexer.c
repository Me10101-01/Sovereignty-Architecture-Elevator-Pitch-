/*
 * token_lexer.c — SAGCO token lexer
 *
 * Reads input, classifies tokens, builds TokenStream.
 * Recognizes SAGCO domain keywords: eru, verdict, proven, antibody, brick.
 * Recognizes engineering units: LNFT, SQFT, MEN, HOURS, PSI, OHMS, VOLTS, AMPS.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "token_lexer.h"

#define INITIAL_CAPACITY 64

static const char *SAGCO_KEYWORDS[] = {
    "eru", "verdict", "proven", "promising", "unproven", "inflated",
    "antibody", "brick", "burnrate", "claim", "missing_link",
    NULL
};

static const char *SAGCO_UNITS[] = {
    "LNFT", "SQFT", "MEN", "HOURS", "PSI", "OHMS", "VOLTS", "AMPS",
    "BTU", "GPM", "RPM", "KW", "HP", "FT", "IN",
    NULL
};

static TokenStream *ts_new(void)
{
    TokenStream *ts = malloc(sizeof(TokenStream));
    ts->tokens   = malloc(sizeof(Token) * INITIAL_CAPACITY);
    ts->count    = 0;
    ts->capacity = INITIAL_CAPACITY;
    return ts;
}

static void ts_push(TokenStream *ts, TokenType type, const char *val, int line, const char *src)
{
    if (ts->count >= ts->capacity) {
        ts->capacity *= 2;
        ts->tokens = realloc(ts->tokens, sizeof(Token) * ts->capacity);
    }
    Token *t = &ts->tokens[ts->count++];
    t->type   = type;
    t->value  = val ? strdup(val) : NULL;
    t->line   = line;
    t->col    = 0;
    t->source = src;
}

static int is_keyword(const char *s)
{
    for (int i = 0; SAGCO_KEYWORDS[i]; i++)
        if (strcmp(s, SAGCO_KEYWORDS[i]) == 0) return 1;
    return 0;
}

static int is_unit(const char *s)
{
    for (int i = 0; SAGCO_UNITS[i]; i++)
        if (strcmp(s, SAGCO_UNITS[i]) == 0) return 1;
    return 0;
}

static void lex_text(TokenStream *ts, const char *text, const char *source)
{
    int   line = 1;
    char  buf[256];
    int   bi   = 0;
    const char *p = text;

    while (*p) {
        if (*p == '\n') { line++; p++; continue; }

        /* Number */
        if (isdigit(*p) || (*p == '-' && isdigit(*(p+1)))) {
            bi = 0;
            while (isdigit(*p) || *p == '.' || *p == '-') buf[bi++] = *p++;
            buf[bi] = '\0';
            ts_push(ts, TOK_NUMBER, buf, line, source);
            continue;
        }

        /* Word */
        if (isalpha(*p) || *p == '_') {
            bi = 0;
            while (isalnum(*p) || *p == '_') buf[bi++] = *p++;
            buf[bi] = '\0';
            if (is_keyword(buf))     ts_push(ts, TOK_KEYWORD,    buf, line, source);
            else if (is_unit(buf))   ts_push(ts, TOK_UNIT,       buf, line, source);
            else                     ts_push(ts, TOK_IDENTIFIER,  buf, line, source);
            continue;
        }

        /* Operator */
        if (strchr("+-*/=<>", *p)) {
            char op[2] = { *p, '\0' };
            ts_push(ts, TOK_OPERATOR, op, line, source);
            p++;
            continue;
        }

        p++;
    }

    ts_push(ts, TOK_EOF, NULL, line, source);
}

TokenStream *file_lex(const char *filepath)
{
    FILE *f = fopen(filepath, "r");
    if (!f) {
        fprintf(stderr, "  [LEXER] cannot open: %s\n", filepath);
        return ts_new();
    }
    fseek(f, 0, SEEK_END);
    long size = ftell(f);
    rewind(f);
    char *buf = malloc(size + 1);
    fread(buf, 1, size, f);
    buf[size] = '\0';
    fclose(f);

    TokenStream *ts = ts_new();
    lex_text(ts, buf, filepath);
    free(buf);
    return ts;
}

TokenStream *pdf_lex(const char *filepath)
{
    /* PDF text extraction via pdftotext (poppler) — pipes stdout into lexer */
    char cmd[512];
    snprintf(cmd, sizeof(cmd), "pdftotext \"%s\" - 2>/dev/null", filepath);
    FILE *pipe = popen(cmd, "r");
    if (!pipe) {
        fprintf(stderr, "  [LEXER] pdftotext not found — install poppler-utils\n");
        return ts_new();
    }
    char   *text = NULL;
    size_t  total = 0, cap = 4096;
    text = malloc(cap);
    char   line[1024];
    while (fgets(line, sizeof(line), pipe)) {
        size_t len = strlen(line);
        if (total + len + 1 > cap) { cap *= 2; text = realloc(text, cap); }
        memcpy(text + total, line, len);
        total += len;
    }
    text[total] = '\0';
    pclose(pipe);

    TokenStream *ts = ts_new();
    lex_text(ts, text, filepath);
    free(text);
    return ts;
}

TokenStream *url_lex(const char *url)
{
    /* Fetch URL body via curl, then lex as text */
    char cmd[1024];
    snprintf(cmd, sizeof(cmd), "curl -sL --max-time 10 \"%s\" 2>/dev/null", url);
    FILE *pipe = popen(cmd, "r");
    if (!pipe) {
        fprintf(stderr, "  [LEXER] curl not found\n");
        return ts_new();
    }
    char   *body = NULL;
    size_t  total = 0, cap = 8192;
    body = malloc(cap);
    char   buf[2048];
    size_t n;
    while ((n = fread(buf, 1, sizeof(buf), pipe)) > 0) {
        if (total + n + 1 > cap) { cap *= 2; body = realloc(body, cap); }
        memcpy(body + total, buf, n);
        total += n;
    }
    body[total] = '\0';
    pclose(pipe);

    TokenStream *ts = ts_new();
    lex_text(ts, body, url);
    free(body);
    return ts;
}

void token_stream_free(TokenStream *ts)
{
    if (!ts) return;
    for (int i = 0; i < ts->count; i++) free(ts->tokens[i].value);
    free(ts->tokens);
    free(ts);
}

void token_stream_print(const TokenStream *ts)
{
    for (int i = 0; i < ts->count; i++) {
        const Token *t = &ts->tokens[i];
        printf("  [L%3d] type=%-12d  %s\n", t->line, t->type, t->value ? t->value : "(null)");
    }
}
