/*
 * receipt.h — Invocation receipt
 */

#ifndef SAGCO_RECEIPT_H
#define SAGCO_RECEIPT_H

typedef struct {
    const char *subsystem;
    const char *command;
    const char *verdict;    /* COMPUTED | FAILED_COMPUTE | UNCOMPUTED */
    int         exit_code;
} SagcoReceipt;

int receipt_append(const SagcoReceipt *r, const char *log_path);

#endif /* SAGCO_RECEIPT_H */
