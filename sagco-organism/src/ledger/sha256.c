/*
 * sha256.c — SHA-256 implementation for SAGCO organism
 *
 * Pure C, no external dependencies.
 * FIPS 180-4 compliant.
 */

#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include "sha256.h"

#define ROTR(x, n) (((x) >> (n)) | ((x) << (32 - (n))))
#define CH(x,y,z)  (((x) & (y)) ^ (~(x) & (z)))
#define MAJ(x,y,z) (((x) & (y)) ^ ((x) & (z)) ^ ((y) & (z)))
#define S0(x)      (ROTR(x, 2)  ^ ROTR(x, 13) ^ ROTR(x, 22))
#define S1(x)      (ROTR(x, 6)  ^ ROTR(x, 11) ^ ROTR(x, 25))
#define G0(x)      (ROTR(x, 7)  ^ ROTR(x, 18) ^ ((x) >> 3))
#define G1(x)      (ROTR(x, 17) ^ ROTR(x, 19) ^ ((x) >> 10))

static const uint32_t K[64] = {
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
    0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
    0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
    0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
    0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
    0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
};

typedef struct { uint8_t data[64]; uint32_t h[8]; uint64_t bits; uint32_t len; } Sha256;

static void sha256_init(Sha256 *s)
{
    s->h[0]=0x6a09e667; s->h[1]=0xbb67ae85; s->h[2]=0x3c6ef372; s->h[3]=0xa54ff53a;
    s->h[4]=0x510e527f; s->h[5]=0x9b05688c; s->h[6]=0x1f83d9ab; s->h[7]=0x5be0cd19;
    s->bits = s->len = 0;
}

static void sha256_transform(Sha256 *s)
{
    uint32_t w[64], a,b,c,d,e,f,g,h,t1,t2;
    for (int i=0; i<16; i++) {
        w[i]  = (uint32_t)s->data[i*4]   << 24;
        w[i] |= (uint32_t)s->data[i*4+1] << 16;
        w[i] |= (uint32_t)s->data[i*4+2] <<  8;
        w[i] |= (uint32_t)s->data[i*4+3];
    }
    for (int i=16; i<64; i++) w[i] = G1(w[i-2]) + w[i-7] + G0(w[i-15]) + w[i-16];
    a=s->h[0];b=s->h[1];c=s->h[2];d=s->h[3];
    e=s->h[4];f=s->h[5];g=s->h[6];h=s->h[7];
    for (int i=0; i<64; i++) {
        t1 = h + S1(e) + CH(e,f,g) + K[i] + w[i];
        t2 = S0(a) + MAJ(a,b,c);
        h=g; g=f; f=e; e=d+t1;
        d=c; c=b; b=a; a=t1+t2;
    }
    s->h[0]+=a; s->h[1]+=b; s->h[2]+=c; s->h[3]+=d;
    s->h[4]+=e; s->h[5]+=f; s->h[6]+=g; s->h[7]+=h;
}

static void sha256_update(Sha256 *s, const uint8_t *d, size_t len)
{
    for (size_t i=0; i<len; i++) {
        s->data[s->len++] = d[i];
        if (s->len == 64) { sha256_transform(s); s->bits += 512; s->len = 0; }
    }
}

static void sha256_final(Sha256 *s, uint8_t hash[32])
{
    uint32_t i = s->len;
    s->data[i++] = 0x80;
    if (i > 56) { while (i<64) s->data[i++]=0; sha256_transform(s); i=0; }
    while (i<56) s->data[i++]=0;
    s->bits += s->len * 8;
    for (int j=7; j>=0; j--) { s->data[56+(7-j)] = (uint8_t)(s->bits >> (j*8)); }
    sha256_transform(s);
    for (i=0; i<4; i++)
        for (int j=0; j<8; j++)
            hash[i+(j*4)] = (s->h[j] >> (24 - i*8)) & 0xff;
}

static void bytes_to_hex(const uint8_t *b, char *out)
{
    for (int i=0; i<32; i++) snprintf(out+i*2, 3, "%02x", b[i]);
    out[64] = '\0';
}

int sha256_buf(const void *data, size_t len, char out[65])
{
    Sha256  s; uint8_t h[32];
    sha256_init(&s);
    sha256_update(&s, (const uint8_t*)data, len);
    sha256_final(&s, h);
    bytes_to_hex(h, out);
    return 0;
}

int sha256_file(const char *path, char out[65])
{
    FILE *f = fopen(path, "rb");
    if (!f) { snprintf(out, 65, "(file not found)"); return 1; }
    Sha256  s; uint8_t buf[4096], h[32];
    sha256_init(&s);
    size_t n;
    while ((n = fread(buf, 1, sizeof(buf), f)) > 0) sha256_update(&s, buf, n);
    fclose(f);
    sha256_final(&s, h);
    bytes_to_hex(h, out);
    return 0;
}
