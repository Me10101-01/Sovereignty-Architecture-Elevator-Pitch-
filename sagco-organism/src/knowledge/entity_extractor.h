#ifndef ENTITY_EXTRACTOR_H
#define ENTITY_EXTRACTOR_H

#include <stddef.h>

#define MAX_ENTITIES 512
#define CHUNK        4096

typedef struct {
    char entity[64];
    char entity_class[16];
    long offset;
} EntityHit;

/* Scan a buffer for known domain entities; appends to hits[]. */
int scan_chunk(const char *buf, size_t len, const char *source,
               EntityHit *hits, int *n_hits, long base_offset);

#endif /* ENTITY_EXTRACTOR_H */
