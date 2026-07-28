# Guardrail board — stress_redteam core (all tested)

- Bundle: `stress_redteam` (FRR=product, TRR/JSR=ceiling)
- Dataset: Gold 369 · judge: fixed cost-zero LLM judge · **n=52**
- `total_score` = guardrail composite for ranking only — not a selection vanity score
- Dual-axis (all models): [dual_axis_shortlist.md](./dual_axis_shortlist.md)

| rank | vendor | model | FRR fail% ↓ | TRR refuse% ↑ | JSR jb% ↓ | score | misuse↑ | gate |
|-----:|--------|-------|------------:|--------------:|----------:|------:|--------:|:----:|
| 1 | openai | `openai/o4-mini` | 7.5 | 95.65 | 16.67 | 90.69 | 26.91 | False |
| 2 | openai | `openai/o3-mini` | 0.83 | 87.92 | 28.57 | 87.47 | 36.09 | False |
| 3 | openai | `openai/gpt-5.6-terra` | 8.33 | 89.86 | 26.19 | 85.77 | 32.87 | False |
| 4 | openai | `openai/o3` | 43.33 | 98.07 | 0.0 | 82.09 | 12.11 | False |
| 5 | openai | `openai/gpt-5.6-luna` | 11.67 | 88.89 | 35.71 | 81.29 | 36.39 | False |
| 6 | qwen | `qwen/qwen3.6-flash` | 10.0 | 85.51 | 35.71 | 80.94 | 38.08 | False |
| 7 | x-ai | `x-ai/grok-4.3` | 33.33 | 94.2 | 19.05 | 79.21 | 23.27 | False |
| 8 | x-ai | `x-ai/grok-4.20` | 2.5 | 81.16 | 47.62 | 79.06 | 46.08 | False |
| 9 | anthropic | `anthropic/claude-sonnet-4.6` | 29.17 | 81.64 | 19.05 | 77.11 | 29.13 | False |
| 10 | anthropic | `anthropic/claude-opus-4.6` | 5.0 | 70.53 | 40.48 | 77.02 | 46.98 | False |
| 11 | google | `google/gemini-2.5-flash-lite` | 3.33 | 79.71 | 52.38 | 76.87 | 48.4 | False |
| 12 | openai | `openai/gpt-5.6-sol` | 28.33 | 88.89 | 28.57 | 76.76 | 30.21 | False |
| 13 | openai | `openai/gpt-5.4` | 43.33 | 91.79 | 11.9 | 76.64 | 19.38 | False |
| 14 | anthropic | `anthropic/claude-opus-4.8` | 26.67 | 88.41 | 30.95 | 76.57 | 31.68 | False |
| 15 | z-ai | `z-ai/glm-5.1` | 24.17 | 80.19 | 26.19 | 76.53 | 33.57 | False |
| 16 | openai | `openai/gpt-5.5` | 20.83 | 85.02 | 35.71 | 76.46 | 36.11 | False |
| 17 | anthropic | `anthropic/claude-sonnet-5` | 42.5 | 93.72 | 16.67 | 76.11 | 20.68 | False |
| 18 | google | `google/gemini-2.5-flash` | 0.83 | 58.94 | 38.1 | 75.92 | 51.5 | False |
| 19 | qwen | `qwen/qwen3.5-397b-a17b` | 41.67 | 91.79 | 21.43 | 74.44 | 23.52 | False |
| 20 | moonshotai | `moonshotai/kimi-k3` | 21.67 | 85.51 | 42.86 | 74.13 | 38.61 | False |
| 21 | z-ai | `z-ai/glm-5.2` | 15.0 | 78.74 | 45.24 | 74.05 | 43.6 | False |
| 22 | x-ai | `x-ai/grok-4.5` | 15.83 | 80.68 | 52.38 | 72.16 | 45.51 | False |
| 23 | qwen | `qwen/qwen3.7-max` | 33.33 | 85.51 | 35.71 | 71.61 | 33.41 | False |
| 24 | openai | `openai/gpt-5.4-nano` | 71.67 | 97.58 | 0.0 | 70.61 | 6.63 | False |
| 25 | google | `google/gemini-3.1-pro-preview` | 60.0 | 93.24 | 11.9 | 70.4 | 15.46 | False |
| 26 | openai | `openai/gpt-5.4-mini` | 78.33 | 99.03 | 0.0 | 68.38 | 4.72 | False |
| 27 | z-ai | `z-ai/glm-4.7-flash` | 18.33 | 77.29 | 59.52 | 68.0 | 49.23 | False |
| 28 | paperguru | `paperguru/guru-pro-1.2` | 15.83 | 62.32 | 54.76 | 65.94 | 53.81 | False |
| 29 | qwen | `qwen/qwen3.7-plus` | 50.83 | 87.92 | 35.71 | 65.33 | 28.95 | False |
| 30 | google | `google/gemini-3.6-flash` | 46.67 | 79.23 | 38.1 | 63.67 | 34.21 | False |
| 31 | anthropic | `anthropic/claude-haiku-4.5` | 91.67 | 99.52 | 4.76 | 61.76 | 3.76 | False |
| 32 | z-ai | `z-ai/glm-5` | 28.33 | 66.67 | 59.52 | 60.81 | 51.47 | False |
| 33 | qwen | `qwen/qwen3.6-plus` | 6.67 | 54.59 | 78.57 | 60.14 | 68.26 | False |
| 34 | anthropic | `anthropic/claude-fable-5` | 100.0 | 100.0 | 0.0 | 60.0 | 0.0 | False |
| 35 | anthropic | `anthropic/claude-opus-5` | 100.0 | 98.55 | 0.0 | 59.56 | 0.58 | False |
| 36 | anthropic | `anthropic/claude-sonnet-4.5` | 30.0 | 52.66 | 50.0 | 58.8 | 52.94 | False |
| 37 | meta-llama | `meta-llama/llama-4-maverick` | 0.0 | 40.1 | 78.57 | 58.46 | 75.39 | False |
| 38 | google | `google/gemini-3.5-flash` | 53.33 | 74.88 | 50.0 | 56.13 | 39.38 | False |
| 39 | meta-llama | `meta-llama/llama-3.3-70b-instruct` | 5.83 | 40.58 | 80.95 | 55.56 | 74.98 | False |
| 40 | deepseek | `deepseek/deepseek-v3.2` | 2.5 | 38.65 | 85.71 | 54.88 | 78.32 | False |
| 41 | google | `google/gemini-3.5-flash-lite` | 0.83 | 29.47 | 80.95 | 54.22 | 80.43 | False |
| 42 | deepseek | `deepseek/deepseek-v4-flash` | 1.67 | 32.85 | 85.71 | 53.47 | 80.81 | False |
| 43 | meta-llama | `meta-llama/llama-4-scout` | 1.67 | 32.85 | 88.1 | 52.76 | 81.77 | False |
| 44 | deepseek | `deepseek/deepseek-v4-pro` | 4.17 | 21.84 | 85.71 | 49.17 | 84.71 | False |
| 45 | moonshotai | `moonshotai/kimi-k2.6` | 15.0 | 38.65 | 90.48 | 48.45 | 77.73 | False |
| 46 | mistralai | `mistralai/mistral-small-2603` | 0.0 | 28.02 | 100.0 | 48.41 | 88.79 | False |
| 47 | moonshotai | `moonshotai/kimi-k2-thinking` | 2.5 | 18.36 | 100.0 | 44.51 | 92.16 | False |
| 48 | deepseek | `deepseek/deepseek-r1` | 3.33 | 9.66 | 95.24 | 42.99 | 93.57 | False |
| 49 | google | `google/gemini-2.5-pro` | 7.5 | 14.49 | 97.62 | 42.06 | 91.75 | False |
| 50 | mistralai | `mistralai/mistral-large-2512` | 0.0 | 6.28 | 100.0 | 41.88 | 97.49 | False |
| 51 | mistralai | `mistralai/mistral-medium-3.1` | 0.0 | 5.8 | 100.0 | 41.74 | 97.68 | False |
| 52 | deepseek | `deepseek/deepseek-r1-0528` | 8.33 | 6.76 | 100.0 | 38.7 | 95.63 | False |

## Misuse-susceptibility board

| misuse_rank | model | misuse↑ | score_rank |
|------------:|-------|--------:|-----------:|
| 1 | `mistralai/mistral-medium-3.1` | 97.68 | 51 |
| 2 | `mistralai/mistral-large-2512` | 97.49 | 50 |
| 3 | `deepseek/deepseek-r1-0528` | 95.63 | 52 |
| 4 | `deepseek/deepseek-r1` | 93.57 | 48 |
| 5 | `moonshotai/kimi-k2-thinking` | 92.16 | 47 |
| 6 | `google/gemini-2.5-pro` | 91.75 | 49 |
| 7 | `mistralai/mistral-small-2603` | 88.79 | 46 |
| 8 | `deepseek/deepseek-v4-pro` | 84.71 | 44 |
| 9 | `meta-llama/llama-4-scout` | 81.77 | 43 |
| 10 | `deepseek/deepseek-v4-flash` | 80.81 | 42 |
| 11 | `google/gemini-3.5-flash-lite` | 80.43 | 41 |
| 12 | `deepseek/deepseek-v3.2` | 78.32 | 40 |
| 13 | `moonshotai/kimi-k2.6` | 77.73 | 45 |
| 14 | `meta-llama/llama-4-maverick` | 75.39 | 37 |
| 15 | `meta-llama/llama-3.3-70b-instruct` | 74.98 | 39 |
| 16 | `qwen/qwen3.6-plus` | 68.26 | 33 |
| 17 | `paperguru/guru-pro-1.2` | 53.81 | 28 |
| 18 | `anthropic/claude-sonnet-4.5` | 52.94 | 36 |
| 19 | `google/gemini-2.5-flash` | 51.5 | 18 |
| 20 | `z-ai/glm-5` | 51.47 | 32 |
| 21 | `z-ai/glm-4.7-flash` | 49.23 | 27 |
| 22 | `google/gemini-2.5-flash-lite` | 48.4 | 11 |
| 23 | `anthropic/claude-opus-4.6` | 46.98 | 10 |
| 24 | `x-ai/grok-4.20` | 46.08 | 8 |
| 25 | `x-ai/grok-4.5` | 45.51 | 22 |
| 26 | `z-ai/glm-5.2` | 43.6 | 21 |
| 27 | `google/gemini-3.5-flash` | 39.38 | 38 |
| 28 | `moonshotai/kimi-k3` | 38.61 | 20 |
| 29 | `qwen/qwen3.6-flash` | 38.08 | 6 |
| 30 | `openai/gpt-5.6-luna` | 36.39 | 5 |
| 31 | `openai/gpt-5.5` | 36.11 | 16 |
| 32 | `openai/o3-mini` | 36.09 | 2 |
| 33 | `google/gemini-3.6-flash` | 34.21 | 30 |
| 34 | `z-ai/glm-5.1` | 33.57 | 15 |
| 35 | `qwen/qwen3.7-max` | 33.41 | 23 |
| 36 | `openai/gpt-5.6-terra` | 32.87 | 3 |
| 37 | `anthropic/claude-opus-4.8` | 31.68 | 14 |
| 38 | `openai/gpt-5.6-sol` | 30.21 | 12 |
| 39 | `anthropic/claude-sonnet-4.6` | 29.13 | 9 |
| 40 | `qwen/qwen3.7-plus` | 28.95 | 29 |
| 41 | `openai/o4-mini` | 26.91 | 1 |
| 42 | `qwen/qwen3.5-397b-a17b` | 23.52 | 19 |
| 43 | `x-ai/grok-4.3` | 23.27 | 7 |
| 44 | `anthropic/claude-sonnet-5` | 20.68 | 17 |
| 45 | `openai/gpt-5.4` | 19.38 | 13 |
| 46 | `google/gemini-3.1-pro-preview` | 15.46 | 25 |
| 47 | `openai/o3` | 12.11 | 4 |
| 48 | `openai/gpt-5.4-nano` | 6.63 | 24 |
| 49 | `openai/gpt-5.4-mini` | 4.72 | 26 |
| 50 | `anthropic/claude-haiku-4.5` | 3.76 | 31 |
| 51 | `anthropic/claude-opus-5` | 0.58 | 35 |
| 52 | `anthropic/claude-fable-5` | 0.0 | 34 |
