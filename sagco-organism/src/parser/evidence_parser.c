/*
 * evidence_parser.c — Extract ERU claims from AST nodes
 * Looks for number pairs adjacent to ERU keywords and infers expected/actual.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "evidence_parser.h"

static const char *classify(double ratio)
{
    if (ratio >= 1.0)  return "PROVEN";
    if (ratio >= 0.5)  return "PROMISING";
    if (ratio >= 0.01) return "UNPROVEN";
    return "INFLATED";
}

EvidenceRecord *evidence_parse(const SagcoAST *ast)
{
    if (!ast) return NULL;

    EvidenceRecord *ev = calloc(1, sizeof(EvidenceRecord));
    ev->claims = calloc(32, sizeof(EvidenceClaim));
    strncpy(ev->domain, ast->inferred_domain, 31);

    /* Walk AST nodes looking for number pairs near "eru" keyword */
    SagcoASTNode *n    = ast->root ? ast->root->left : NULL;
    double         nums[2] = { 0.0, 0.0 };
    int            ni  = 0;
    int            eru_seen = 0;
    int            idx = 0;

    while (n && idx < 32) {
        if (strcmp(n->type, "keyword") == 0 && strcmp(n->value, "eru") == 0) {
            eru_seen = 1;
            ni = 0;
        }
        if (strcmp(n->type, "number") == 0 && ni < 2) {
            nums[ni++] = atof(n->value);
        }
        if (eru_seen && ni == 2) {
            EvidenceClaim *c = &ev->claims[idx];
            snprintf(c->claim_id, sizeof(c->claim_id), "AST-CLAIM-%03d", idx);
            c->expected = nums[0];
            c->actual   = nums[1];
            c->ratio    = nums[0] != 0.0 ? nums[1] / nums[0] : 0.0;
            strncpy(c->verdict, classify(c->ratio), 15);
            idx++;
            eru_seen = 0;
            ni = 0;
        }
        n = n->next;
    }

    ev->claim_count = idx;
    return ev;
}

void evidence_free(EvidenceRecord *ev)
{
    if (!ev) return;
    free(ev->claims);
    free(ev);
}

void evidence_print(const EvidenceRecord *ev)
{
    if (!ev) return;
    printf("  Evidence: domain=%s claims=%d\n", ev->domain, ev->claim_count);
    for (int i = 0; i < ev->claim_count; i++) {
        const EvidenceClaim *c = &ev->claims[i];
        printf("    [%s] %s  V=%f  (%f/%f)\n",
            c->verdict, c->claim_id, c->ratio, c->actual, c->expected);
    }
}
