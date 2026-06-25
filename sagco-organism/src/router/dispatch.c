/*
 * dispatch.c — sagco analyze auto-pipeline
 *
 * This is the dispatcher that was the biggest missing link.
 *
 * INPUT → detect type → route to correct lexer
 *       → parser → AST → subsystem
 *       → evidence receipt → SHA-256 seal
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "dispatch.h"
#include "../lexer/token_lexer.h"
#include "../parser/ast_builder.h"
#include "../parser/evidence_parser.h"
#include "../ledger/receipt.h"
#include "../ledger/sha256.h"

InputType detect_input_type(const char *input)
{
    if (!input) return INPUT_UNKNOWN;

    /* URL detection */
    if (strncmp(input, "http://",  7) == 0) return INPUT_URL;
    if (strncmp(input, "https://", 8) == 0) return INPUT_URL;

    /* File extension detection */
    size_t len = strlen(input);
    if (len > 4 && strcmp(input + len - 4, ".pdf") == 0) return INPUT_PDF;
    if (len > 5 && strcmp(input + len - 5, ".json") == 0) return INPUT_FILE;
    if (len > 2 && strcmp(input + len - 2, ".c")   == 0) return INPUT_FILE;

    return INPUT_FILE;
}

int sagco_analyze_pipeline(SagcoContext *ctx)
{
    if (ctx->argc < 1) {
        fprintf(stderr, "  ERROR: sagco analyze <input>\n");
        return 1;
    }

    const char *input    = ctx->argv[0];
    InputType   itype    = detect_input_type(input);
    int         result   = 0;

    printf("  [LEXER]    input=%s type=%d\n", input, itype);

    /* Stage 1: Lex */
    TokenStream *tokens = NULL;
    switch (itype) {
        case INPUT_PDF:
            printf("  [LEXER]    pdf_lexer → token stream\n");
            tokens = pdf_lex(input);
            break;
        case INPUT_URL:
            printf("  [LEXER]    url_lexer → curl → http_parser → token stream\n");
            tokens = url_lex(input);
            break;
        case INPUT_FILE:
        default:
            printf("  [LEXER]    token_lexer → token stream\n");
            tokens = file_lex(input);
            break;
    }

    if (!tokens) {
        fprintf(stderr, "  [FAILED_COMPUTE]  lexer returned NULL\n");
        return 1;
    }
    printf("  [LEXER]    tokens=%d\n", tokens->count);

    /* Stage 2: Parse → AST */
    printf("  [PARSER]   building AST...\n");
    SagcoAST *ast = ast_build(tokens);
    if (!ast) {
        fprintf(stderr, "  [FAILED_COMPUTE]  ast_build returned NULL\n");
        token_stream_free(tokens);
        return 1;
    }
    printf("  [PARSER]   AST nodes=%d subsystem=%s\n", ast->node_count, ast->inferred_subsystem);

    /* Stage 3: Evidence parse */
    printf("  [EVIDENCE] extracting evidence from AST...\n");
    EvidenceRecord *evidence = evidence_parse(ast);
    if (evidence) {
        printf("  [EVIDENCE] claims=%d domain=%s\n", evidence->claim_count, evidence->domain);
    }

    /* Stage 4: Receipt + SHA-256 seal */
    printf("  [LEDGER]   writing receipt...\n");
    SagcoReceipt receipt = {
        .subsystem = "analyze",
        .command   = input,
        .verdict   = result == 0 ? "COMPUTED" : "FAILED_COMPUTE",
        .exit_code = result,
    };
    receipt_append(&receipt, "logs/invocations.log");

    char hash[65];
    sha256_file(input, hash);
    printf("  [SHA256]   %s  %s\n", hash, input);
    printf("  [SEAL]     evidence receipt sealed\n\n");

    /* Cleanup */
    ast_free(ast);
    token_stream_free(tokens);
    if (evidence) evidence_free(evidence);

    return result;
}
