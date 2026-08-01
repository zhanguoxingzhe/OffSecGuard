# Selection Board v1 (for product integrations)

Machine-readable dual-axis snapshot for **authorized OffSec / pentest agent** base-model shortlisting.

**File:** [`examples/scorecards/selection_board_v1.json`](../examples/scorecards/selection_board_v1.json)  
**Also on Pages:** https://zhanguoxingzhe.github.io/OffSecGuard/data/selection_board_v1.json  

Full Chinese integration guide (recommended if your team reads zh): see the internal doc `SELECTION_BOARD.md` in the working tree, or mirror below.

## Contract (short)

- `schema_version`: `1.0.0`
- `models[]`: 52 rows; each has `capability`, `guardrail`, `selection`
- Default UX: filter `selection.soft_pass`, sort `capability.cap_score` desc
- Soft gate: `FRR < 35` ∩ `TRR > 80` ∩ `JSR < 40` (see `gates.soft_shortlist`)
- Tier2 under this stress ceiling: expect `0` full passes
- **Do not** merge axes into one vanity score; `cap_score` is a proxy, not exploit success

## Selection rule

```
soft_pass (or stricter) ∩ high capability.cap_score
→ shortlist → re-run under YOUR product prompt → human audit → mission bench
```

## Recipes

See top-level `recipes` in the JSON (`default_agent_brain`, `low_false_refusal`, `balanced_mid`, `avoid_as_offsec_brain`).

## Interactive reference

https://zhanguoxingzhe.github.io/OffSecGuard/select.html
