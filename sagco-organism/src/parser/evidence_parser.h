/*
 * evidence_parser.h — Extract ERU evidence records from AST
 */

#ifndef SAGCO_EVIDENCE_PARSER_H
#define SAGCO_EVIDENCE_PARSER_H

#include "ast_builder.h"

typedef struct {
    char   claim_id[64];
    double expected;
    double actual;
    double ratio;
    char   verdict[16];
} EvidenceClaim;

typedef struct {
    EvidenceClaim *claims;
    int            claim_count;
    char           domain[32];
} EvidenceRecord;

EvidenceRecord *evidence_parse(const SagcoAST *ast);
void            evidence_free(EvidenceRecord *ev);
void            evidence_print(const EvidenceRecord *ev);

#endif /* SAGCO_EVIDENCE_PARSER_H */
