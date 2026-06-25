/*
 * sha256.h — SHA-256 for the C organism
 */

#ifndef SAGCO_SHA256_H
#define SAGCO_SHA256_H

#include <stddef.h>
#include <stdint.h>

/* Compute SHA-256 of a file, write 65-char hex string to `out` */
int sha256_file(const char *filepath, char out[65]);

/* Compute SHA-256 of a buffer */
int sha256_buf(const void *data, size_t len, char out[65]);

#endif /* SAGCO_SHA256_H */
