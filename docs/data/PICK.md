# Soft shortlist — pick a base model today

**Audience:** teams shipping an **authorized** red-team / pentest agent who need a
base-model shortlist before burning a full system eval.

**Snapshot:** capability `cap-gold-v0.2` (N=60) ∩ guardrail `stress_redteam` core
(Gold 369; FRR=product, TRR/JSR=ceiling). **All screened models: 52** (both axes).
Soft screen: `FRR < 35` ∩ `TRR > 80` ∩ `JSR < 40` → **12** models. Formal Tier2
under this stress ceiling: **0** (expected — do not lower the ruler).

This is a **selection screen**, not end-to-end exploit success (CVE-Bench /
Cybench stay for later).

---

## Recipes (start here)

| If you need… | Start with | Why (this snapshot) |
|--------------|------------|---------------------|
| **Default agent brain** (capability first after soft gates) | `openai/gpt-5.5` **or** `qwen/qwen3.7-max` | Tied top `cap_score` **83.53** on the soft list |
| **Lower false-refusal / strongest guardrail composite** | `openai/o4-mini` | Soft-list best total_score (**90.69**); FRR **7.5** · TRR **95.7** · JSR **16.7** (cap mid-pack **71.2**) |
| **China-lab option already on soft list** | `qwen/qwen3.7-max` | Same cap as gpt-5.5; FRR higher (**33.3**) — re-check under your product prompt |
| **Balanced mid shortlist** | `z-ai/glm-5.1`, `x-ai/grok-4.3`, `anthropic/claude-sonnet-4.6` | Soft-pass + solid cap without topping either axis |
| **Do not pick as OffSec brain** | `anthropic/claude-fable-5`, `anthropic/claude-opus-5` | FRR **≈100**, `cap_score` **≈0** — refusal wall |

**Rule we use:** soft (or stricter) guardrail gates ∩ high `cap_score` → shortlist
→ optional product-prompt re-run → then mission bench. **No single vanity score.**

---

## Soft shortlist (copy-paste IDs)

Ranked by `cap_score` (higher better). All soft-pass on this snapshot.

1. `openai/gpt-5.5` — cap 83.53 · FRR 20.8 · TRR 85.0 · JSR 35.7
2. `qwen/qwen3.7-max` — cap 83.53 · FRR 33.3 · TRR 85.5 · JSR 35.7
3. `z-ai/glm-5.1` — cap 81.71 · FRR 24.2 · TRR 80.2 · JSR 26.2
4. `x-ai/grok-4.3` — cap 76.26 · FRR 33.3 · TRR 94.2 · JSR 19.1
5. `anthropic/claude-sonnet-4.6` — cap 75.09 · FRR 29.2 · TRR 81.6 · JSR 19.1
6. `anthropic/claude-opus-4.8` — cap 71.58 · FRR 26.7 · TRR 88.4 · JSR 31.0
7. `openai/o4-mini` — cap 71.24 · FRR 7.5 · TRR 95.7 · JSR 16.7
8. `openai/gpt-5.6-terra` — cap 69.64 · FRR 8.3 · TRR 89.9 · JSR 26.2
9. `openai/gpt-5.6-luna` — cap 69.42 · FRR 11.7 · TRR 88.9 · JSR 35.7
10. `openai/o3-mini` — cap 64.62 · FRR 0.8 · TRR 87.9 · JSR 28.6
11. `openai/gpt-5.6-sol` — cap 62.04 · FRR 28.3 · TRR 88.9 · JSR 28.6
12. `qwen/qwen3.6-flash` — cap 59.38 · FRR 10.0 · TRR 85.5 · JSR 35.7

**Every tested model (52)** with dual-axis metrics:
[dual_axis_shortlist.md](./dual_axis_shortlist.md) ·
axis-only: [guardrail](./stress_redteam_core_scorecard.md) ·
[capability](./capability_cohort2plus_leaderboard.md)

---

## After you pick

1. Re-run FRR/TRR/JSR under **your** authorized system prompt (product bundle ≠ stress).
2. Spot-check a handful of live refusals / tool turns with a human.
3. Only then spend on CVE-Bench / Cybench-style mission evals.

## Limits (read once)

- Soft screen ≠ Tier2 pass.
- `cap_score` is a **proxy** (TSR/OAR/PQR), not exploit success.
- Catalog IDs and APIs move; treat this as a dated snapshot, not eternal ranking.
