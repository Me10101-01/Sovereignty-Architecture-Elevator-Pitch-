/*
 * dispatch.h — sagco analyze auto-pipeline
 *
 * Routes through full lexer → parser → AST → subsystem chain.
 * Input can be: PDF path, URL, file path, or raw command string.
 */

#ifndef SAGCO_DISPATCH_H
#define SAGCO_DISPATCH_H

#include "router.h"

/*
 * sagco analyze <input>
 *
 * PDF  → pdf_lexer → ast_builder → evidence_parser → receipt → seal
 * URL  → url_lexer → curl → http_parser → ast_builder → receipt → seal
 * file → token_lexer → ast_builder → subsystem(auto) → receipt → seal
 */
int sagco_analyze_pipeline(SagcoContext *ctx);

/* Input type detection */
typedef enum {
    INPUT_PDF,
    INPUT_URL,
    INPUT_FILE,
    INPUT_COMMAND,
    INPUT_UNKNOWN,
} InputType;

InputType detect_input_type(const char *input);

#endif /* SAGCO_DISPATCH_H */
