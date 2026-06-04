#!/bin/sh
# SAGCO core environment — source this to get all agent bins on PATH
SAGCO_BASE="$(cd "$(dirname "$0")/.." && pwd)"
export SAGCO_BASE
export PATH="$SAGCO_BASE/bin:$SAGCO_BASE/agents/eru/bin:$SAGCO_BASE/shared_state/bin:$SAGCO_BASE/scheduler/bin:$SAGCO_BASE/analysis/bin:$SAGCO_BASE/dashboard/bin:$SAGCO_BASE/dispatcher/bin:$SAGCO_BASE/wafer/bin:$SAGCO_BASE/pdfscan/bin:$SAGCO_BASE/registry/bin:$PATH"
