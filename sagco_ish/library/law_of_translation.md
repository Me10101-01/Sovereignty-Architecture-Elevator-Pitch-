# SAGCO Law of Translation

> Supporting principle under Commandment XIII (Compute Before Claiming).
> Governs the boundary between symbolic/mythic names and engineering names.

---

## The Rule

Every SAGCO symbolic term must have three layers registered before it can appear
in any Canon artifact (capstone, DAO governance, legal packet, client report):

| Layer | Name | Register | Must Compute? |
|-------|------|----------|---------------|
| 1 | **Story Name** | Library of Alizandrea | No |
| 2 | **Engineering Name** | Canon / brick manifest | Yes — must describe what it actually is |
| 3 | **Compute Test** | compute_law.csv | Yes — must run and exit 0 |

If a term has only Layer 1, it is mythology. Beautiful and valid, but not Canon.
If a term has all three layers, it is a translated symbol: computable and poetic.

---

## Academic Foundation

This principle is grounded in **Cognitive Dimensions of Notations** (Green & Petre, 1996),
a framework for evaluating how symbolic/notational systems affect human cognition.

Relevant dimensions from CDN:

| CDN Dimension | SAGCO Application |
|---------------|-------------------|
| **Role-expressiveness** | Does the Story Name make the Engineering Name guessable? |
| **Viscosity** | How hard is it to update a symbol when the underlying brick changes? |
| **Hidden dependencies** | Does the Library term hide Canon complexity from non-engineers? |
| **Visibility** | Can an outsider see what the symbol means without reading the Library? |

The Law of Translation solves the **hidden dependencies** and **visibility** problems:
outsiders can query the translation registry and get the Engineering Name + Compute Test
for any Story Name they encounter.

Prior art registered as: `Cognitive_Dimensions_of_Notations_Green_Petre_1996`

---

## Registered Translations

*See `sagco_ish/lineage/translations/translation_registry.csv`*
*Or run: `sagco_ish/lineage/bin/sagco-translate --list`*

| Story Name | Engineering Name | Compute Test | Status |
|------------|-----------------|--------------|--------|
| Purple Node | Evidence_Reconciliation_and_Hallucheck_Layer | sagco-hallucheck returns GREEN | REGISTERED |
| The Mansion | SAGCO_OS_Full_Stack_58_bricks | sagco-run-alpha C1602_CASE_001 exits 0 | REGISTERED |
| Theater | SAGCO_EVO_Dashboard_MIDI_Ledger | sagco-evo + sagco-midi produce output | REGISTERED |
| Distinguished Engineer | SAGCO_Operator_Human_in_the_Loop | test -x sagco_ish/registry/bin/sagco-where | REGISTERED |
| Legions of Minds | Multi_Node_State_Mesh_iPad_ZFold_Pi | sagco-state-read C1602_CASE_001 | REGISTERED |
| The Score | Evolution_Ledger_CREATION_ADAPTATION_ERROR_RESOLUTION | sagco-evo CURRENT_KEY | REGISTERED |
| Red strikes | OPCODE_TOPOFUZZ_Fuzz_Coverage_Scan | sagco-fleet-eru log exits 0 | REGISTERED |
| Blue holds | OPCODE_FORECAST_TOPOLOGY_ERU_Baseline | sagco-health exits 0 | REGISTERED |
| Purple resolves | ERU_GREEN_Claims_PROVEN_Constitution_UPHELD | sagco-commandments EXEMPLARY | REGISTERED |
| Antibody | Failure_Pattern_Archived_with_Patch_Verification | antibody_archive.csv count >= 11 | REGISTERED |
| The Key | CURRENT_KEY_from_sagco-evo_CAER_ratio | sagco-evo outputs CURRENT_KEY | REGISTERED |

---

## How to Use It

**When writing Library (Chapter Two, marketing, fan content):**
Use the Story Name freely. No compute test required.

**When writing Canon (capstone, DAO filing, client packet, legal exhibit):**
You must use the Engineering Name and reference the Compute Test.
Do not use Story Names in Canon artifacts without the translation footnote.

**When someone asks "Is this real?":**
Run: `sagco_ish/lineage/bin/sagco-translate --lookup "Purple Node"`
Returns: Engineering Name + Compute Test + COMPUTABLE/MYTHOLOGY status.

---

## Why This Matters for SNHU Capstone

The CDN framework (Green & Petre, 1996) is well-established in ACM/IEEE literature
and has been cited 1,889+ times (Green, 1989 usability analysis). It gives the
capstone committee a recognized academic framework for evaluating SAGCO's
notational system.

The SAGCO Law of Translation is a direct engineering response to the CDN
**visibility** and **role-expressiveness** problems: rather than forcing poetic names
to compute, we maintain a queryable registry that translates any Library term into
its Canon counterpart on demand.

This is novel because most systems either:
(a) use only technical names (no cultural layer), or
(b) use only poetic names (no audit layer).

SAGCO does both, with a formal translation layer between them.

---

*This document is Library register — it describes the rule, not the implementation.*
*The implementation is `sagco_ish/lineage/bin/sagco-translate` — Canon, computable.*
