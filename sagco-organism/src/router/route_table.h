/*
 * route_table.h — Subsystem handler registry
 */

#ifndef SAGCO_ROUTE_TABLE_H
#define SAGCO_ROUTE_TABLE_H

#include "router.h"

/* Function pointer type for subsystem handlers */
typedef int (*SubsystemHandler)(SagcoContext *ctx);

/* Look up handler by subsystem name. Returns NULL if not found. */
SubsystemHandler route_lookup(const char *subsystem);

#endif /* SAGCO_ROUTE_TABLE_H */
