/*
 * token_lexer.h — SAGCO token lexer interface
 *
 * Tokenizes input files, PDFs (via text extraction), and URLs (via curl).
 * Each token carries type, value, and source position.
 */

#ifndef SAGCO_TOKEN_LEXER_H
#define SAGCO_TOKEN_LEXER_H

#include <stddef.h>

typedef enum {
    TOK_NUMBER,
    TOK_IDENTIFIER,
    TOK_UNIT,        /* LNFT, SQFT, MEN, HOURS, PSI, OHMS, VOLTS, AMPS */
    TOK_OPERATOR,    /* + - * / = < > */
    TOK_KEYWORD,     /* eru, verdict, proven, antibody, brick */
    TOK_STRING,
    TOK_URL,
    TOK_PDF_TEXT,
    TOK_EOF,
    TOK_UNKNOWN,
} TokenType;

typedef struct {
    TokenType   type;
    char       *value;     /* heap-allocated, freed by token_stream_free */
    int         line;
    int         col;
    const char *source;    /* pointer to source filename, not owned */
} Token;

typedef struct {
    Token  *tokens;
    int     count;
    int     capacity;
} TokenStream;

/* Lex from file, PDF text, or URL body */
TokenStream *file_lex(const char *filepath);
TokenStream *pdf_lex(const char *filepath);
TokenStream *url_lex(const char *url);

void         token_stream_free(TokenStream *ts);
void         token_stream_print(const TokenStream *ts);

#endif /* SAGCO_TOKEN_LEXER_H */
