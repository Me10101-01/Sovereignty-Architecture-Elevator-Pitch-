/**
 * flamelang.h — SAGCO-Organism C FFI surface
 *
 * C callers (omni_calc.c, drivers, external tooling) include this header
 * and link against libflamelang.so (or libflamelang.a for static builds).
 *
 * Build note: compile with -I../flame-ffi/include -L<lib-path> -lflamelang
 *
 * SAGCO security gate: all calls are audit-logged via the genesis chain.
 * sagco_init() MUST be called once before any other function.
 * sagco_shutdown() MUST be called on process exit to flush the audit trail.
 */

#ifndef FLAMELANG_H
#define FLAMELANG_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ── Lifecycle ──────────────────────────────────────────────────────────────── */

/**
 * sagco_init — initialise the organism runtime.
 * @config_path  path to sagco-organism.toml  (NULL → use built-in defaults)
 * @return       0 on success, negative errno on failure
 */
int sagco_init(const char *config_path);

/**
 * sagco_shutdown — flush audit log, close connections, free resources.
 * Safe to call multiple times; idempotent after the first.
 */
void sagco_shutdown(void);

/* ── General dispatch ────────────────────────────────────────────────────────
 * Low-level gateway: send any JSON payload to a named SAGCO command.
 *
 * @command     null-terminated command name (e.g. "email", "k8s_job")
 * @payload     JSON string (UTF-8, null-terminated)
 * @result_buf  caller-allocated buffer that receives the JSON response
 * @buf_len     size of result_buf in bytes
 * @return      0 on success; negative errno; SAGCO_ERR_BUF_TOO_SMALL if
 *              the response was truncated (buf_len too small)
 */
int sagco_dispatch(const char *command,
                   const char *payload,
                   char       *result_buf,
                   size_t      buf_len);

/* ── Email dispatch ──────────────────────────────────────────────────────────
 * Sends an email via the organism's configured SMTP relay.
 * Audit-logged automatically with a genesis-proof timestamp.
 *
 * @to       recipient address (null-terminated, UTF-8)
 * @subject  email subject line
 * @body     plain-text or HTML body (organism auto-detects HTML by "<html")
 * @return   0 on success; negative errno on SMTP or auth failure
 */
int sagco_email(const char *to,
                const char *subject,
                const char *body);

/* ── Kubernetes job dispatch ─────────────────────────────────────────────────
 * Creates or triggers a Kubernetes Job in the SAGCO namespace.
 * HITL (Human-In-The-Loop) gate is enforced: the organism emits a
 * notification and blocks until human approval is received.
 *
 * @namespace_    K8s namespace (NULL → "sagco")
 * @job_name      job metadata.name
 * @json_payload  job spec as JSON string (merged with organism defaults)
 * @return        0 on success (human approved + job created);
 *                SAGCO_ERR_HITL_DENIED  if the operator rejected;
 *                negative errno on API error
 */
int sagco_k8s_job(const char *namespace_,
                  const char *job_name,
                  const char *json_payload);

/* ── Audit log ───────────────────────────────────────────────────────────────
 * Append a genesis-signed audit entry to the immutable organism log.
 *
 * @component  originating component (e.g. "omni_calc", "flame-lexer")
 * @event      short event label   (e.g. "overload_alert", "calc_complete")
 * @data       arbitrary JSON data (NULL → "{}")
 * @return     0 on success
 */
int sagco_audit_log(const char *component,
                    const char *event,
                    const char *data);

/* ── Genesis proof ───────────────────────────────────────────────────────────
 * Write the current genesis proof (SHA-256 chain hash) into buf.
 * Format: "<hex_hash>|increment=<N>|ts=<unix_ms>"
 *
 * @buf      caller-allocated output buffer
 * @buf_len  size of buf in bytes (recommend >= 128)
 * @return   number of bytes written (0 on error)
 */
size_t sagco_genesis_proof(char  *buf,
                            size_t buf_len);

/* ── Error codes ─────────────────────────────────────────────────────────────
 * SAGCO-specific codes are negative to avoid collision with POSIX errno.
 */
#define SAGCO_ERR_NOT_INIT        (-100)  /* sagco_init() not called */
#define SAGCO_ERR_BUF_TOO_SMALL   (-101)  /* result_buf too small for response */
#define SAGCO_ERR_HITL_DENIED     (-102)  /* human operator rejected the action */
#define SAGCO_ERR_GENESIS_FAIL    (-103)  /* genesis proof chain integrity error */
#define SAGCO_ERR_SMTP             (-104)  /* SMTP relay error */
#define SAGCO_ERR_K8S              (-105)  /* Kubernetes API error */
#define SAGCO_ERR_JSON             (-106)  /* JSON parse/serialize error */

#ifdef __cplusplus
}
#endif

#endif /* FLAMELANG_H */
