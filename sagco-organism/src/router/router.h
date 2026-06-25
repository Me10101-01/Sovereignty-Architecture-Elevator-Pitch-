/*
 * router.h — SAGCO dispatch context + router interface
 */

#ifndef SAGCO_ROUTER_H
#define SAGCO_ROUTER_H

typedef struct {
    const char  *subsystem;
    const char  *command;
    int          argc;
    char       **argv;
} SagcoContext;

/* Main dispatcher — routes ctx to the correct subsystem handler */
int sagco_dispatch(SagcoContext *ctx);

#endif /* SAGCO_ROUTER_H */
