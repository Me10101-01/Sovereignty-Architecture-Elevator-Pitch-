# DeepAI — SAGCO External Node Profile

## Classification

| Field | Value |
|---|---|
| Node class | `external_ai_node` |
| Layer | `extension` |
| Trust level | **LOW** |
| Sovereign | ❌ |
| Offline capable | ❌ |
| Owned model | ❌ |
| Vendor dependency | DeepAI (third-party SaaS) |

## Antibody

```
DO_NOT_TRUST_AS_SOURCE_OF_TRUTH
```

## Mansion Role Map

```
GPT / Codex      → architecture + reasoning
Claude           → build / dispatch / co-work
DeepAI           → probe / image-video sandbox   ← this node
Local / Kali / Pi → sovereign execution
SAGCO Registry   → truth layer
```

## Permitted Uses ✅

- Prompt comparison across models
- Image / video generation experiments
- Creative probe and style tests
- Quick capability benchmarks

## Prohibited Uses ❌

- Final verification of any SAGCO computation
- Secrets or private credentials
- Private / proprietary data
- Source-of-truth decisions
- Wafer audit sign-off

## Integration Pattern

```
sagco-node-deepai (extension)
    │
    ├── inputs:  prompts / images / quick tests
    ├── outputs: responses / generated media
    └── risk:    vendor dependency → antibody applied
```

DeepAI outputs are **probes**, not proofs. All verification
routes through the SAGCO registry truth layer, never through
an external AI node.
