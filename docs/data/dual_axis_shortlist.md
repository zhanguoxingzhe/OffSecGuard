# Dual-axis board — all tested models

## Sources

- Capability: **cap-gold-v0.2 (N=60)**
- Guardrail: **stress_redteam core (Gold 369; FRR=product, TRR/JSR=ceiling; fixed cost-zero LLM judge)**
- Models on **both** boards (all screened): **52**
- Tier2 full pass under stress ceiling: **0** (expected rare — do not lower the ruler)
- Soft shortlist screen (FRR&lt;35.0 ∩ TRR&gt;80.0 ∩ JSR&lt;40.0): **12**

Recipes: [PICK.md](./PICK.md) · axis-only full tables: [guardrail](./stress_redteam_core_scorecard.md) · [capability](./capability_cohort2plus_leaderboard.md)

## Soft shortlist ranked by cap_score

| # | Model | cap | g-rank | FRR↓ | TRR↑ | JSR↓ | total |
|--:|:---|---:|---:|---:|---:|---:|---:|
| 1 | `openai/gpt-5.5` | 83.53 | 16 | 20.83 | 85.02 | 35.71 | 76.46 |
| 2 | `qwen/qwen3.7-max` | 83.53 | 23 | 33.33 | 85.51 | 35.71 | 71.61 |
| 3 | `z-ai/glm-5.1` | 81.71 | 15 | 24.17 | 80.19 | 26.19 | 76.53 |
| 4 | `x-ai/grok-4.3` | 76.26 | 7 | 33.33 | 94.20 | 19.05 | 79.21 |
| 5 | `anthropic/claude-sonnet-4.6` | 75.09 | 9 | 29.17 | 81.64 | 19.05 | 77.11 |
| 6 | `anthropic/claude-opus-4.8` | 71.58 | 14 | 26.67 | 88.41 | 30.95 | 76.57 |
| 7 | `openai/o4-mini` | 71.24 | 1 | 7.50 | 95.65 | 16.67 | 90.69 |
| 8 | `openai/gpt-5.6-terra` | 69.64 | 3 | 8.33 | 89.86 | 26.19 | 85.77 |
| 9 | `openai/gpt-5.6-luna` | 69.42 | 5 | 11.67 | 88.89 | 35.71 | 81.29 |
| 10 | `openai/o3-mini` | 64.62 | 2 | 0.83 | 87.92 | 28.57 | 87.47 |
| 11 | `openai/gpt-5.6-sol` | 62.04 | 12 | 28.33 | 88.89 | 28.57 | 76.76 |
| 12 | `qwen/qwen3.6-flash` | 59.38 | 6 | 10.00 | 85.51 | 35.71 | 80.94 |

## All tested models (ranked by cap_score)

| # | Model | cohort | cap | g-rank | FRR↓ | TRR↑ | JSR↓ | total | soft |
|--:|:---|:---|---:|---:|---:|---:|---:|---:|:---:|
| 1 | `anthropic/claude-sonnet-4.5` | 1 | 85.13 | 36 | 30.00 | 52.66 | 50.00 | 58.80 |  |
| 2 | `openai/gpt-5.5` | 2 | 83.53 | 16 | 20.83 | 85.02 | 35.71 | 76.46 | Y |
| 3 | `qwen/qwen3.7-max` | 3 | 83.53 | 23 | 33.33 | 85.51 | 35.71 | 71.61 | Y |
| 4 | `moonshotai/kimi-k2-thinking` | 1 | 81.71 | 47 | 2.50 | 18.36 | 100.00 | 44.51 |  |
| 5 | `z-ai/glm-5.1` | 2 | 81.71 | 15 | 24.17 | 80.19 | 26.19 | 76.53 | Y |
| 6 | `mistralai/mistral-large-2512` | 1 | 78.08 | 50 | 0.00 | 6.28 | 100.00 | 41.88 |  |
| 7 | `openai/gpt-5.4-mini` | 1 | 77.64 | 26 | 78.33 | 99.03 | 0.00 | 68.38 |  |
| 8 | `anthropic/claude-haiku-4.5` | 1 | 76.26 | 31 | 91.67 | 99.52 | 4.76 | 61.76 |  |
| 9 | `x-ai/grok-4.3` | 2 | 76.26 | 7 | 33.33 | 94.20 | 19.05 | 79.21 | Y |
| 10 | `google/gemini-2.5-flash` | 1 | 76.04 | 18 | 0.83 | 58.94 | 38.10 | 75.92 |  |
| 11 | `moonshotai/kimi-k3` | 3 | 75.53 | 20 | 21.67 | 85.51 | 42.86 | 74.13 |  |
| 12 | `anthropic/claude-sonnet-4.6` | 2 | 75.09 | 9 | 29.17 | 81.64 | 19.05 | 77.11 | Y |
| 13 | `z-ai/glm-5` | 1 | 74.88 | 32 | 28.33 | 66.67 | 59.52 | 60.81 |  |
| 14 | `deepseek/deepseek-v4-pro` | 3 | 74.66 | 44 | 4.17 | 21.84 | 85.71 | 49.17 |  |
| 15 | `qwen/qwen3.5-397b-a17b` | 1 | 73.06 | 19 | 41.67 | 91.79 | 21.43 | 74.44 |  |
| 16 | `x-ai/grok-4.20` | 1 | 72.18 | 8 | 2.50 | 81.16 | 47.62 | 79.06 |  |
| 17 | `deepseek/deepseek-v3.2` | 1 | 71.62 | 40 | 2.50 | 38.65 | 85.71 | 54.88 |  |
| 18 | `anthropic/claude-opus-4.8` | 2 | 71.58 | 14 | 26.67 | 88.41 | 30.95 | 76.57 | Y |
| 19 | `qwen/qwen3.6-plus` | 2 | 71.46 | 33 | 6.67 | 54.59 | 78.57 | 60.14 |  |
| 20 | `anthropic/claude-opus-4.6` | 1 | 71.30 | 10 | 5.00 | 70.53 | 40.48 | 77.02 |  |
| 21 | `openai/o4-mini` | 2 | 71.24 | 1 | 7.50 | 95.65 | 16.67 | 90.69 | Y |
| 22 | `meta-llama/llama-3.3-70b-instruct` | 1 | 70.80 | 39 | 5.83 | 40.58 | 80.95 | 55.56 |  |
| 23 | `qwen/qwen3.7-plus` | 3 | 70.35 | 29 | 50.83 | 87.92 | 35.71 | 65.33 |  |
| 24 | `anthropic/claude-sonnet-5` | 3 | 69.64 | 17 | 42.50 | 93.72 | 16.67 | 76.11 |  |
| 25 | `openai/gpt-5.6-terra` | 3 | 69.64 | 3 | 8.33 | 89.86 | 26.19 | 85.77 | Y |
| 26 | `openai/gpt-5.4` | 1 | 69.42 | 13 | 43.33 | 91.79 | 11.90 | 76.64 |  |
| 27 | `openai/gpt-5.6-luna` | 3 | 69.42 | 5 | 11.67 | 88.89 | 35.71 | 81.29 | Y |
| 28 | `x-ai/grok-4.5` | 3 | 69.20 | 22 | 15.83 | 80.68 | 52.38 | 72.16 |  |
| 29 | `mistralai/mistral-medium-3.1` | 1 | 68.76 | 51 | 0.00 | 5.80 | 100.00 | 41.74 |  |
| 30 | `z-ai/glm-4.7-flash` | 1 | 67.82 | 27 | 18.33 | 77.29 | 59.52 | 68.00 |  |
| 31 | `openai/o3` | 1 | 67.60 | 4 | 43.33 | 98.07 | 0.00 | 82.09 |  |
| 32 | `z-ai/glm-5.2` | 3 | 66.90 | 21 | 15.00 | 78.74 | 45.24 | 74.05 |  |
| 33 | `paperguru/guru-pro-1.2` | 2 | 66.28 | 28 | 15.83 | 62.32 | 54.76 | 65.94 |  |
| 34 | `openai/o3-mini` | 1 | 64.62 | 2 | 0.83 | 87.92 | 28.57 | 87.47 | Y |
| 35 | `mistralai/mistral-small-2603` | 2 | 64.18 | 46 | 0.00 | 28.02 | 100.00 | 48.41 |  |
| 36 | `moonshotai/kimi-k2.6` | 2 | 63.02 | 45 | 15.00 | 38.65 | 90.48 | 48.45 |  |
| 37 | `google/gemini-3.5-flash-lite` | 2 | 62.80 | 41 | 0.83 | 29.47 | 80.95 | 54.22 |  |
| 38 | `openai/gpt-5.4-nano` | 1 | 62.80 | 24 | 71.67 | 97.58 | 0.00 | 70.61 |  |
| 39 | `google/gemini-2.5-pro` | 1 | 62.36 | 49 | 7.50 | 14.49 | 97.62 | 42.06 |  |
| 40 | `openai/gpt-5.6-sol` | 3 | 62.04 | 12 | 28.33 | 88.89 | 28.57 | 76.76 | Y |
| 41 | `deepseek/deepseek-v4-flash` | 3 | 61.89 | 42 | 1.67 | 32.85 | 85.71 | 53.47 |  |
| 42 | `google/gemini-3.1-pro-preview` | 2 | 59.38 | 25 | 60.00 | 93.24 | 11.90 | 70.40 |  |
| 43 | `qwen/qwen3.6-flash` | 2 | 59.38 | 6 | 10.00 | 85.51 | 35.71 | 80.94 | Y |
| 44 | `meta-llama/llama-4-scout` | 2 | 54.61 | 43 | 1.67 | 32.85 | 88.10 | 52.76 |  |
| 45 | `google/gemini-2.5-flash-lite` | 1 | 46.46 | 11 | 3.33 | 79.71 | 52.38 | 76.87 |  |
| 46 | `meta-llama/llama-4-maverick` | 2 | 46.15 | 37 | 0.00 | 40.10 | 78.57 | 58.46 |  |
| 47 | `deepseek/deepseek-r1-0528` | 1 | 41.97 | 52 | 8.33 | 6.76 | 100.00 | 38.70 |  |
| 48 | `google/gemini-3.5-flash` | 2 | 41.53 | 38 | 53.33 | 74.88 | 50.00 | 56.13 |  |
| 49 | `deepseek/deepseek-r1` | 1 | 29.86 | 48 | 3.33 | 9.66 | 95.24 | 42.99 |  |
| 50 | `google/gemini-3.6-flash` | 3 | 18.35 | 30 | 46.67 | 79.23 | 38.10 | 63.67 |  |
| 51 | `anthropic/claude-fable-5` | 3 | 0.00 | 34 | 100.00 | 100.00 | 0.00 | 60.00 |  |
| 52 | `anthropic/claude-opus-5` | 3 | 0.00 | 35 | 100.00 | 98.55 | 0.00 | 59.56 |  |

## Rank divergence (largest |gap|)

Positive `rank_gap` ⇒ better on guardrail composite rank than on capability (or vice versa if negative).

| Model | cap_rank | guardrail_rank | gap | cap | total |
|:---|---:|---:|---:|---:|---:|
| `mistralai/mistral-large-2512` | 6 | 50 | +44 | 78.08 | 41.88 |
| `moonshotai/kimi-k2-thinking` | 4 | 47 | +43 | 81.71 | 44.51 |
| `qwen/qwen3.6-flash` | 43 | 6 | -37 | 59.38 | 80.94 |
| `anthropic/claude-sonnet-4.5` | 1 | 36 | +35 | 85.13 | 58.80 |
| `google/gemini-2.5-flash-lite` | 45 | 11 | -34 | 46.46 | 76.87 |
| `openai/o3-mini` | 34 | 2 | -32 | 64.62 | 87.47 |
| `deepseek/deepseek-v4-pro` | 14 | 44 | +30 | 74.66 | 49.17 |
| `openai/gpt-5.6-sol` | 40 | 12 | -28 | 62.04 | 76.76 |
| `openai/o3` | 31 | 4 | -27 | 67.60 | 82.09 |
| `anthropic/claude-haiku-4.5` | 8 | 31 | +23 | 76.26 | 61.76 |
| `deepseek/deepseek-v3.2` | 17 | 40 | +23 | 71.62 | 54.88 |
| `mistralai/mistral-medium-3.1` | 29 | 51 | +22 | 68.76 | 41.74 |
| `openai/gpt-5.6-luna` | 27 | 5 | -22 | 69.42 | 81.29 |
| `openai/gpt-5.6-terra` | 25 | 3 | -22 | 69.64 | 85.77 |
| `google/gemini-3.6-flash` | 50 | 30 | -20 | 18.35 | 63.67 |

## Refusal-wall examples (TRR≥90 and FRR≥40)

| Model | FRR↓ | TRR↑ | JSR↓ | cap |
|:---|---:|---:|---:|---:|
| `anthropic/claude-fable-5` | 100.00 | 100.00 | 0.00 | 0.00 |
| `anthropic/claude-opus-5` | 100.00 | 98.55 | 0.00 | 0.00 |
| `anthropic/claude-haiku-4.5` | 91.67 | 99.52 | 4.76 | 76.26 |
| `openai/gpt-5.4-mini` | 78.33 | 99.03 | 0.00 | 77.64 |
| `openai/gpt-5.4-nano` | 71.67 | 97.58 | 0.00 | 62.80 |
| `google/gemini-3.1-pro-preview` | 60.00 | 93.24 | 11.90 | 59.38 |
| `openai/o3` | 43.33 | 98.07 | 0.00 | 67.60 |
| `openai/gpt-5.4` | 43.33 | 91.79 | 11.90 | 69.42 |
| `anthropic/claude-sonnet-5` | 42.50 | 93.72 | 16.67 | 69.64 |
| `qwen/qwen3.5-397b-a17b` | 41.67 | 91.79 | 21.43 | 73.06 |
