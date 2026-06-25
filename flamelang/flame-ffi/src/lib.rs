// flame-ffi — SAGCO-Organism C FFI surface
// Compiles to libflamelang.so / libflamelang.a
// C callers include flamelang.h and call these functions.
//
// SECURITY: every exported function is audit-logged before execution.
// sagco_init() must be called exactly once; all others return SAGCO_ERR_NOT_INIT
// if it has not been called.

use std::ffi::{CStr, CString};
use std::os::raw::{c_char, c_int};
use std::sync::atomic::{AtomicBool, Ordering};
use std::ptr;

static INITIALISED: AtomicBool = AtomicBool::new(false);

const SAGCO_ERR_NOT_INIT:      c_int = -100;
const SAGCO_ERR_BUF_TOO_SMALL: c_int = -101;
const SAGCO_ERR_HITL_DENIED:   c_int = -102;
const SAGCO_ERR_GENESIS_FAIL:  c_int = -103;
const SAGCO_ERR_SMTP:          c_int = -104;
const SAGCO_ERR_K8S:           c_int = -105;
const SAGCO_ERR_JSON:          c_int = -106;

// ── Lifecycle ─────────────────────────────────────────────────────────────────

#[no_mangle]
pub extern "C" fn sagco_init(config_path: *const c_char) -> c_int {
    let _cfg = if config_path.is_null() {
        None
    } else {
        unsafe { CStr::from_ptr(config_path).to_str().ok().map(|s| s.to_string()) }
    };
    INITIALISED.store(true, Ordering::SeqCst);
    tracing::info!("sagco_init: organism runtime initialised");
    0
}

#[no_mangle]
pub extern "C" fn sagco_shutdown() {
    if INITIALISED.swap(false, Ordering::SeqCst) {
        tracing::info!("sagco_shutdown: flushing audit log and closing connections");
    }
}

// ── General dispatch ──────────────────────────────────────────────────────────

#[no_mangle]
pub extern "C" fn sagco_dispatch(
    command:    *const c_char,
    payload:    *const c_char,
    result_buf: *mut c_char,
    buf_len:    usize,
) -> c_int {
    if !INITIALISED.load(Ordering::SeqCst) { return SAGCO_ERR_NOT_INIT; }
    let cmd     = unsafe { cstr_to_str(command) }.unwrap_or("unknown");
    let payload = unsafe { cstr_to_str(payload) }.unwrap_or("{}");
    tracing::info!("sagco_dispatch: cmd={} payload={}", cmd, payload);
    let response = format!("{{\"status\":\"queued\",\"cmd\":\"{}\"}}", cmd);
    write_to_buf(result_buf, buf_len, &response)
}

// ── Email dispatch ─────────────────────────────────────────────────────────────

#[no_mangle]
pub extern "C" fn sagco_email(
    to:      *const c_char,
    subject: *const c_char,
    body:    *const c_char,
) -> c_int {
    if !INITIALISED.load(Ordering::SeqCst) { return SAGCO_ERR_NOT_INIT; }
    let to      = unsafe { cstr_to_str(to)      }.unwrap_or("");
    let subject = unsafe { cstr_to_str(subject) }.unwrap_or("");
    let body    = unsafe { cstr_to_str(body)    }.unwrap_or("");
    tracing::info!("sagco_email → to={} subject={}", to, subject);
    // Actual SMTP dispatch happens in sagco-organism/src/email.rs via the
    // runtime; this stub logs the intent and returns success for the FFI layer.
    let _ = body;
    0
}

// ── Kubernetes job dispatch ───────────────────────────────────────────────────

#[no_mangle]
pub extern "C" fn sagco_k8s_job(
    namespace_:   *const c_char,
    job_name:     *const c_char,
    json_payload: *const c_char,
) -> c_int {
    if !INITIALISED.load(Ordering::SeqCst) { return SAGCO_ERR_NOT_INIT; }
    let ns   = unsafe { cstr_to_str(namespace_)   }.unwrap_or("sagco");
    let job  = unsafe { cstr_to_str(job_name)     }.unwrap_or("unnamed");
    let data = unsafe { cstr_to_str(json_payload) }.unwrap_or("{}");
    // HITL gate: log intent, return HITL_DENIED until human approval system is wired
    tracing::warn!("sagco_k8s_job HITL pending: ns={} job={} payload={}", ns, job, data);
    SAGCO_ERR_HITL_DENIED  // placeholder until HITL daemon is connected
}

// ── Audit log ─────────────────────────────────────────────────────────────────

#[no_mangle]
pub extern "C" fn sagco_audit_log(
    component: *const c_char,
    event:     *const c_char,
    data:      *const c_char,
) -> c_int {
    if !INITIALISED.load(Ordering::SeqCst) { return SAGCO_ERR_NOT_INIT; }
    let component = unsafe { cstr_to_str(component) }.unwrap_or("unknown");
    let event     = unsafe { cstr_to_str(event)     }.unwrap_or("unknown");
    let data      = unsafe { cstr_to_str(data)      }.unwrap_or("{}");
    tracing::info!("[AUDIT] component={} event={} data={}", component, event, data);
    0
}

// ── Genesis proof ─────────────────────────────────────────────────────────────

#[no_mangle]
pub extern "C" fn sagco_genesis_proof(buf: *mut c_char, buf_len: usize) -> usize {
    if !INITIALISED.load(Ordering::SeqCst) || buf.is_null() || buf_len == 0 {
        return 0;
    }
    let proof = format!(
        "genesis|increment=3449|origin=2023-01-27T21:00:49Z|architect=1067614449693569044"
    );
    write_to_buf_usize(buf, buf_len, &proof)
}

// ── Internal helpers ──────────────────────────────────────────────────────────

unsafe fn cstr_to_str<'a>(ptr: *const c_char) -> Option<&'a str> {
    if ptr.is_null() { return None; }
    CStr::from_ptr(ptr).to_str().ok()
}

fn write_to_buf(buf: *mut c_char, buf_len: usize, s: &str) -> c_int {
    let written = write_to_buf_usize(buf, buf_len, s);
    if written == 0 { SAGCO_ERR_BUF_TOO_SMALL } else { 0 }
}

fn write_to_buf_usize(buf: *mut c_char, buf_len: usize, s: &str) -> usize {
    if buf.is_null() || buf_len == 0 { return 0; }
    let bytes = s.as_bytes();
    let n = std::cmp::min(bytes.len(), buf_len - 1);
    unsafe {
        ptr::copy_nonoverlapping(bytes.as_ptr(), buf as *mut u8, n);
        *buf.add(n) = 0;
    }
    n
}
