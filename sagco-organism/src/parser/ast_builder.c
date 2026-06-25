/*
 * ast_builder.c — SAGCO AST builder
 *
 * Pass 1: scan tokens for domain signals (units, keywords)
 * Pass 2: infer subsystem from dominant signal
 * Pass 3: build node tree
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ast_builder.h"

static SagcoASTNode *node_new(const char *type, const char *value)
{
    SagcoASTNode *n = calloc(1, sizeof(SagcoASTNode));
    n->type  = type  ? strdup(type)  : NULL;
    n->value = value ? strdup(value) : NULL;
    return n;
}

static void node_free(SagcoASTNode *n)
{
    if (!n) return;
    node_free(n->left);
    node_free(n->right);
    node_free(n->next);
    free(n->type);
    free(n->value);
    free(n);
}

/* Subsystem inference from unit/keyword frequency */
static void infer_subsystem(const TokenStream *ts, char *subsystem, char *domain)
{
    int physics = 0, gps = 0, trading = 0, eru = 0, field = 0;

    for (int i = 0; i < ts->count; i++) {
        const Token *t = &ts->tokens[i];
        if (t->type == TOK_UNIT) {
            if (strcmp(t->value,"OHMS")==0||strcmp(t->value,"VOLTS")==0||strcmp(t->value,"AMPS")==0) physics++;
            if (strcmp(t->value,"PSI")==0||strcmp(t->value,"GPM")==0) physics++, field++;
            if (strcmp(t->value,"LNFT")==0||strcmp(t->value,"SQFT")==0||strcmp(t->value,"MEN")==0||strcmp(t->value,"HOURS")==0) field++, eru++;
        }
        if (t->type == TOK_KEYWORD) {
            if (strcmp(t->value,"eru")==0||strcmp(t->value,"verdict")==0||strcmp(t->value,"burnrate")==0) eru++;
            if (strcmp(t->value,"proven")==0) eru++;
        }
        if (t->type == TOK_IDENTIFIER) {
            if (strcmp(t->value,"lat")==0||strcmp(t->value,"lon")==0||strcmp(t->value,"bearing")==0) gps++;
            if (strcmp(t->value,"CPI")==0||strcmp(t->value,"PO")==0) trading++, eru++;
        }
    }

    int max = 0;
    const char *sub = "unknown", *dom = "sagco";
    if (physics > max) { max = physics; sub = "physics"; dom = "field"; }
    if (gps     > max) { max = gps;     sub = "gps";     dom = "gps"; }
    if (trading > max) { max = trading; sub = "ninja";   dom = "trading"; }
    if (eru     > max) { max = eru;     sub = "analyze"; dom = "eru"; }
    if (field   > max) { max = field;   sub = "field";   dom = "field"; }

    strncpy(subsystem, sub, 31);
    strncpy(domain,    dom, 31);
}

SagcoAST *ast_build(const TokenStream *ts)
{
    if (!ts || ts->count == 0) return NULL;

    SagcoAST *ast = calloc(1, sizeof(SagcoAST));
    infer_subsystem(ts, ast->inferred_subsystem, ast->inferred_domain);

    SagcoASTNode *root = node_new("program", ast->inferred_subsystem);
    SagcoASTNode *tail = NULL;

    for (int i = 0; i < ts->count; i++) {
        const Token *t = &ts->tokens[i];
        if (t->type == TOK_EOF) break;

        const char *ntype = "token";
        if      (t->type == TOK_KEYWORD)    ntype = "keyword";
        else if (t->type == TOK_NUMBER)     ntype = "number";
        else if (t->type == TOK_UNIT)       ntype = "unit";
        else if (t->type == TOK_IDENTIFIER) ntype = "identifier";

        SagcoASTNode *n = node_new(ntype, t->value);
        ast->node_count++;

        if (!root->left) root->left = n;
        else             tail->next = n;
        tail = n;
    }

    ast->root = root;
    return ast;
}

void ast_free(SagcoAST *ast)
{
    if (!ast) return;
    node_free(ast->root);
    free(ast);
}

void ast_print(const SagcoAST *ast)
{
    if (!ast) return;
    printf("  AST: subsystem=%s domain=%s nodes=%d\n",
        ast->inferred_subsystem, ast->inferred_domain, ast->node_count);
}
