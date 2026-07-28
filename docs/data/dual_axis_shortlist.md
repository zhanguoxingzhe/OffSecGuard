# Dual-axis shortlist (capability ∩ guardrail)

**Need a ready shortlist?** Start with [PICK.md](./PICK.md).  
**Want every screened model?** [Guardrail full board](./stress_redteam_core_scorecard.md) · [Capability full board](./capability_cohort2plus_leaderboard.md).

## Sources

- Capability: **cap-gold-v0.2 (N=60)**
- Guardrail: **stress_redteam core (Gold 369; FRR=product, TRR/JSR=ceiling; fixed cost-zero LLM judge)**
- Models overlapping both boards: **30**
- Tier2 full pass under stress ceiling: **0** (expected rare — do not lower the ruler)
- Soft shortlist screen (FRR&lt;35.0 ∩ TRR&gt;80.0 ∩ JSR&lt;40.0): **11**

Judge is plumbing only (cost-zero + human audit 23/25). Soft shortlist tables for
external writeups omit house-model target rows if present.

## Soft shortlist ranked by cap_score

| # | Model | cap | g-rank | FRR↓ | TRR↑ | JSR↓ | total |
|--:|:---|---:|---:|---:|---:|---:|---:|
| 1 | `openai/gpt-5.5` | 83.53 | 10 | 20.83 | 85.02 | 35.71 | 76.46 |
| 2 | `qwen/qwen3.7-max` | 83.53 | 15 | 33.33 | 85.51 | 35.71 | 71.61 |
| 3 | `z-ai/glm-5.1` | 81.71 | 9 | 24.17 | 80.19 | 26.19 | 76.53 |
| 4 | `x-ai/grok-4.3` | 76.26 | 5 | 33.33 | 94.20 | 19.05 | 79.21 |
| 5 | `anthropic/claude-sonnet-4.6` | 75.09 | 6 | 29.17 | 81.64 | 19.05 | 77.11 |
| 6 | `anthropic/claude-opus-4.8` | 71.58 | 8 | 26.67 | 88.41 | 30.95 | 76.57 |
| 7 | `openai/o4-mini` | 71.24 | 1 | 7.50 | 95.65 | 16.67 | 90.69 |
| 8 | `openai/gpt-5.6-terra` | 69.64 | 2 | 8.33 | 89.86 | 26.19 | 85.77 |
| 9 | `openai/gpt-5.6-luna` | 69.42 | 3 | 11.67 | 88.89 | 35.71 | 81.29 |
| 10 | `openai/gpt-5.6-sol` | 62.04 | 7 | 28.33 | 88.89 | 28.57 | 76.76 |
| 11 | `qwen/qwen3.6-flash` | 59.38 | 4 | 10.00 | 85.51 | 35.71 | 80.94 |

## Rank divergence (guardrail total_score rank vs cap_score rank)

Positive `rank_gap` ⇒ looks better on guardrail composite than on capability (or vice versa if negative).

| Model | cap_rank | guardrail_rank | gap | cap | total |
|:---|---:|---:|---:|---:|---:|
| `deepseek/deepseek-v4-pro` | 7 | 28 | +21 | 74.66 | 49.17 |
| `qwen/qwen3.6-flash` | 24 | 4 | -20 | 59.38 | 80.94 |
| `openai/gpt-5.6-sol` | 21 | 7 | -14 | 62.04 | 76.76 |
| `qwen/qwen3.7-max` | 2 | 15 | +13 | 83.53 | 71.61 |
| `mistralai/mistral-small-2603` | 18 | 30 | +12 | 64.18 | 48.41 |
| `qwen/qwen3.6-plus` | 9 | 20 | +11 | 71.46 | 60.14 |
| `openai/gpt-5.6-terra` | 13 | 2 | -11 | 69.64 | 85.77 |
| `openai/gpt-5.6-luna` | 14 | 3 | -11 | 69.42 | 81.29 |
| `moonshotai/kimi-k2.6` | 19 | 29 | +10 | 63.02 | 48.45 |
| `openai/gpt-5.5` | 1 | 10 | +9 | 83.53 | 76.46 |
| `openai/o4-mini` | 10 | 1 | -9 | 71.24 | 90.69 |
| `google/gemini-3.6-flash` | 28 | 19 | -9 | 18.35 | 63.67 |

## Refusal-wall examples (TRR≥90 and FRR≥40)

Strong unauthorized refusal, but painful false refusal on authorized work.

| Model | FRR↓ | TRR↑ | JSR↓ | cap |
|:---|---:|---:|---:|---:|
| `anthropic/claude-fable-5` | 100.00 | 100.00 | 0.00 | 0.00 |
| `anthropic/claude-opus-5` | 100.00 | 98.55 | 0.00 | 0.00 |
| `google/gemini-3.1-pro-preview` | 60.00 | 93.24 | 11.90 | 59.38 |
| `anthropic/claude-sonnet-5` | 42.50 | 93.72 | 16.67 | 69.64 |
