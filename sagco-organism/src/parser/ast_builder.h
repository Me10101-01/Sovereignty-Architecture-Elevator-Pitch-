/*
 * ast_builder.h — SAGCO AST builder
 *
 * Consumes a TokenStream, produces a SagcoAST.
 * The AST carries: inferred subsystem, ERU fields, evidence nodes.
 */

#ifndef SAGCO_AST_BUILDER_H
#define SAGCO_AST_BUILDER_H

#include "../lexer/token_lexer.h"

typedef struct SagcoASTNode {
    char                *type;     /* "eru_claim", "number", "unit", "keyword" */
    char                *value;
    struct SagcoASTNode *left;
    struct SagcoASTNode *right;
    struct SagcoASTNode *next;     /* sibling list */
} SagcoASTNode;

typedef struct {
    SagcoASTNode *root;
    int           node_count;
    char          inferred_subsystem[32]; /* "physics", "gps", "trading", ... */
    char          inferred_domain[32];    /* "eru", "flamelang", "trading", ... */
} SagcoAST;

SagcoAST    *ast_build(const TokenStream *ts);
void         ast_free(SagcoAST *ast);
void         ast_print(const SagcoAST *ast);

#endif /* SAGCO_AST_BUILDER_H */
