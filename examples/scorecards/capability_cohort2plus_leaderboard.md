# Capability board — cap-gold-v0.2 (all tested)

- Gold: **cap-gold-v0.2** (N=60)
- Models: **52**
- `cap_score = 0.4·TSR + 0.4·OAR + 0.2·PQR` (proxy — not exploit success)
- Dual-axis (all models): [dual_axis_shortlist.md](./dual_axis_shortlist.md)

| # | cap_score | TSR | OAR | PQR | Model | Cohort |
|--:|--:|--:|--:|--:|:---|:---|
| 1 | 85.13 | 88.0 | 86.36 | 76.92 | `anthropic/claude-sonnet-4.5` | cohort-1 |
| 2 | 83.53 | 84.0 | 86.36 | 76.92 | `openai/gpt-5.5` | cohort-2 |
| 3 | 83.53 | 84.0 | 86.36 | 76.92 | `qwen/qwen3.7-max` | cohort-3 |
| 4 | 81.71 | 84.0 | 81.82 | 76.92 | `moonshotai/kimi-k2-thinking` | cohort-1 |
| 5 | 81.71 | 84.0 | 81.82 | 76.92 | `z-ai/glm-5.1` | cohort-2 |
| 6 | 78.08 | 84.0 | 72.73 | 76.92 | `mistralai/mistral-large-2512` | cohort-1 |
| 7 | 77.64 | 92.0 | 63.64 | 76.92 | `openai/gpt-5.4-mini` | cohort-1 |
| 8 | 76.26 | 84.0 | 68.18 | 76.92 | `anthropic/claude-haiku-4.5` | cohort-1 |
| 9 | 76.26 | 84.0 | 68.18 | 76.92 | `x-ai/grok-4.3` | cohort-2 |
| 10 | 76.04 | 88.0 | 63.64 | 76.92 | `google/gemini-2.5-flash` | cohort-1 |
| 11 | 75.53 | 64.0 | 86.36 | 76.92 | `moonshotai/kimi-k3` | cohort-3 |
| 12 | 75.09 | 72.0 | 77.27 | 76.92 | `anthropic/claude-sonnet-4.6` | cohort-2 |
| 13 | 74.88 | 76.0 | 72.73 | 76.92 | `z-ai/glm-5` | cohort-1 |
| 14 | 74.66 | 80.0 | 68.18 | 76.92 | `deepseek/deepseek-v4-pro` | cohort-3 |
| 15 | 73.06 | 76.0 | 68.18 | 76.92 | `qwen/qwen3.5-397b-a17b` | cohort-1 |
| 16 | 72.18 | 92.0 | 50.0 | 76.92 | `x-ai/grok-4.20` | cohort-1 |
| 17 | 71.62 | 73.91 | 66.67 | 76.92 | `deepseek/deepseek-v3.2` | cohort-1 |
| 18 | 71.58 | 80.0 | 68.18 | 61.54 | `anthropic/claude-opus-4.8` | cohort-2 |
| 19 | 71.46 | 72.0 | 68.18 | 76.92 | `qwen/qwen3.6-plus` | cohort-2 |
| 20 | 71.3 | 80.0 | 63.64 | 69.23 | `anthropic/claude-opus-4.6` | cohort-1 |
| 21 | 71.24 | 76.0 | 63.64 | 76.92 | `openai/o4-mini` | cohort-2 |
| 22 | 70.8 | 84.0 | 54.55 | 76.92 | `meta-llama/llama-3.3-70b-instruct` | cohort-1 |
| 23 | 70.35 | 64.0 | 77.27 | 69.23 | `qwen/qwen3.7-plus` | cohort-3 |
| 24 | 69.64 | 72.0 | 63.64 | 76.92 | `anthropic/claude-sonnet-5` | cohort-3 |
| 25 | 69.64 | 72.0 | 63.64 | 76.92 | `openai/gpt-5.6-terra` | cohort-3 |
| 26 | 69.42 | 76.0 | 59.09 | 76.92 | `openai/gpt-5.4` | cohort-1 |
| 27 | 69.42 | 76.0 | 59.09 | 76.92 | `openai/gpt-5.6-luna` | cohort-3 |
| 28 | 69.2 | 80.0 | 54.55 | 76.92 | `x-ai/grok-4.5` | cohort-3 |
| 29 | 68.76 | 88.0 | 45.45 | 76.92 | `mistralai/mistral-medium-3.1` | cohort-1 |
| 30 | 67.82 | 72.0 | 59.09 | 76.92 | `z-ai/glm-4.7-flash` | cohort-1 |
| 31 | 67.6 | 76.0 | 54.55 | 76.92 | `openai/o3` | cohort-1 |
| 32 | 66.9 | 76.0 | 68.18 | 46.15 | `z-ai/glm-5.2` | cohort-3 |
| 33 | 66.28 | 72.0 | 59.09 | 69.23 | `paperguru/guru-pro-1.2` | cohort-2 |
| 34 | 64.62 | 64.0 | 59.09 | 76.92 | `openai/o3-mini` | cohort-1 |
| 35 | 64.18 | 72.0 | 50.0 | 76.92 | `mistralai/mistral-small-2603` | cohort-2 |
| 36 | 63.02 | 60.0 | 59.09 | 76.92 | `moonshotai/kimi-k2.6` | cohort-2 |
| 37 | 62.8 | 64.0 | 54.55 | 76.92 | `google/gemini-3.5-flash-lite` | cohort-2 |
| 38 | 62.8 | 64.0 | 54.55 | 76.92 | `openai/gpt-5.4-nano` | cohort-1 |
| 39 | 62.36 | 72.0 | 45.45 | 76.92 | `google/gemini-2.5-pro` | cohort-1 |
| 40 | 62.04 | 60.0 | 68.18 | 53.85 | `openai/gpt-5.6-sol` | cohort-3 |
| 41 | 61.89 | 68.0 | 63.64 | 46.15 | `deepseek/deepseek-v4-flash` | cohort-3 |
| 42 | 59.38 | 60.0 | 50.0 | 76.92 | `google/gemini-3.1-pro-preview` | cohort-2 |
| 43 | 59.38 | 60.0 | 50.0 | 76.92 | `qwen/qwen3.6-flash` | cohort-2 |
| 44 | 54.61 | 68.0 | 45.45 | 46.15 | `meta-llama/llama-4-scout` | cohort-2 |
| 45 | 46.46 | 56.0 | 40.91 | 38.46 | `google/gemini-2.5-flash-lite` | cohort-1 |
| 46 | 46.15 | 36.0 | 40.91 | 76.92 | `meta-llama/llama-4-maverick` | cohort-2 |
| 47 | 41.97 | 41.67 | 59.09 | 8.33 | `deepseek/deepseek-r1-0528` | cohort-1 |
| 48 | 41.53 | 36.0 | 40.91 | 53.85 | `google/gemini-3.5-flash` | cohort-2 |
| 49 | 29.86 | 32.0 | 27.27 | 30.77 | `deepseek/deepseek-r1` | cohort-1 |
| 50 | 18.35 | 20.0 | 18.18 | 15.38 | `google/gemini-3.6-flash` | cohort-3 |
| 51 | 0.0 | 0.0 | 0.0 | 0.0 | `anthropic/claude-fable-5` | cohort-3 |
| 52 | 0.0 | 0.0 | 0.0 | 0.0 | `anthropic/claude-opus-5` | cohort-3 |
