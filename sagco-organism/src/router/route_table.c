/*
 * route_table.c — Dispatch table: subsystem name → handler
 *
 * Adding a new subsystem: add one row to sagco_routes[].
 * No other file changes needed.
 */

#include <string.h>
#include <stddef.h>
#include "route_table.h"

/* Forward declarations — one per subsystem */
int physics_handle(SagcoContext *ctx);
int gps_handle(SagcoContext *ctx);
int field_handle(SagcoContext *ctx);
int network_handle(SagcoContext *ctx);
int ninja_handle(SagcoContext *ctx);
int ledger_handle(SagcoContext *ctx);

typedef struct {
    const char       *name;
    SubsystemHandler  handler;
} RouteEntry;

static const RouteEntry sagco_routes[] = {
    { "physics",  physics_handle  },
    { "gps",      gps_handle      },
    { "field",    field_handle    },
    { "network",  network_handle  },
    { "ninja",    ninja_handle    },
    { "ledger",   ledger_handle   },
    { NULL,       NULL            },  /* sentinel */
};

SubsystemHandler route_lookup(const char *subsystem)
{
    for (int i = 0; sagco_routes[i].name != NULL; i++) {
        if (strcmp(sagco_routes[i].name, subsystem) == 0)
            return sagco_routes[i].handler;
    }
    return NULL;
}
