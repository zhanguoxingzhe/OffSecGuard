# Guardrail board — stress_redteam core (full)

- Bundle: stress_redteam (FRR=product, TRR/JSR=ceiling)
- Dataset: Gold 369 · judge: fixed cost-zero LLM judge · **n=51** (house-model targets omitted)
- 	otal_score = guardrail composite for ranking only — **not** a selection vanity score
- Soft shortlist / recipes: [PICK.md](./PICK.md) · dual-axis: [dual_axis_shortlist.md](./dual_axis_shortlist.md)
- Machine-readable: [CSV](./stress_redteam_core_scorecard.csv) · [JSON](./stress_redteam_core_scorecard.json)

| rank | vendor | model | FRR fail% ↓ | TRR refuse% ↑ | JSR jb% ↓ | score | misuse↑ | gate |
|-----:|--------|-------|------------:|--------------:|----------:|------:|--------:|:----:|
| 1 | openai | openai/o4-mini | 7.5 | 95.65 | 16.67 | 90.69 | 26.91 | False |
| 2 | openai | openai/o3-mini | 0.83 | 87.92 | 28.57 | 87.47 | 36.09 | False |
| 3 | openai | openai/gpt-5.6-terra | 8.33 | 89.86 | 26.19 | 85.77 | 32.87 | False |
| 4 | openai | openai/o3 | 43.33 | 98.07 | 0.0 | 82.09 | 12.11 | False |
| 5 | openai | openai/gpt-5.6-luna | 11.67 | 88.89 | 35.71 | 81.29 | 36.39 | False |
| 6 | qwen | qwen/qwen3.6-flash | 10.0 | 85.51 | 35.71 | 80.94 | 38.08 | False |
| 7 | x-ai | x-ai/grok-4.3 | 33.33 | 94.2 | 19.05 | 79.21 | 23.27 | False |
| 8 | x-ai | x-ai/grok-4.20 | 2.5 | 81.16 | 47.62 | 79.06 | 46.08 | False |
| 9 | anthropic | anthropic/claude-sonnet-4.6 | 29.17 | 81.64 | 19.05 | 77.11 | 29.13 | False |
| 10 | anthropic | anthropic/claude-opus-4.6 | 5.0 | 70.53 | 40.48 | 77.02 | 46.98 | False |
| 11 | google | google/gemini-2.5-flash-lite | 3.33 | 79.71 | 52.38 | 76.87 | 48.4 | False |
| 12 | openai | openai/gpt-5.6-sol | 28.33 | 88.89 | 28.57 | 76.76 | 30.21 | False |
| 13 | openai | openai/gpt-5.4 | 43.33 | 91.79 | 11.9 | 76.64 | 19.38 | False |
| 14 | anthropic | anthropic/claude-opus-4.8 | 26.67 | 88.41 | 30.95 | 76.57 | 31.68 | False |
| 15 | z-ai | z-ai/glm-5.1 | 24.17 | 80.19 | 26.19 | 76.53 | 33.57 | False |
| 16 | openai | openai/gpt-5.5 | 20.83 | 85.02 | 35.71 | 76.46 | 36.11 | False |
| 17 | anthropic | anthropic/claude-sonnet-5 | 42.5 | 93.72 | 16.67 | 76.11 | 20.68 | False |
| 18 | google | google/gemini-2.5-flash | 0.83 | 58.94 | 38.1 | 75.92 | 51.5 | False |
| 19 | qwen | qwen/qwen3.5-397b-a17b | 41.67 | 91.79 | 21.43 | 74.44 | 23.52 | False |
| 20 | moonshotai | moonshotai/kimi-k3 | 21.67 | 85.51 | 42.86 | 74.13 | 38.61 | False |
| 21 | z-ai | z-ai/glm-5.2 | 15.0 | 78.74 | 45.24 | 74.05 | 43.6 | False |
| 22 | x-ai | x-ai/grok-4.5 | 15.83 | 80.68 | 52.38 | 72.16 | 45.51 | False |
| 23 | qwen | qwen/qwen3.7-max | 33.33 | 85.51 | 35.71 | 71.61 | 33.41 | False |
| 24 | openai | openai/gpt-5.4-nano | 71.67 | 97.58 | 0.0 | 70.61 | 6.63 | False |
| 25 | google | google/gemini-3.1-pro-preview | 60.0 | 93.24 | 11.9 | 70.4 | 15.46 | False |
| 26 | openai | openai/gpt-5.4-mini | 78.33 | 99.03 | 0.0 | 68.38 | 4.72 | False |
| 27 | z-ai | z-ai/glm-4.7-flash | 18.33 | 77.29 | 59.52 | 68.0 | 49.23 | False |
| 28 | qwen | qwen/qwen3.7-plus | 50.83 | 87.92 | 35.71 | 65.33 | 28.95 | False |
| 29 | google | google/gemini-3.6-flash | 46.67 | 79.23 | 38.1 | 63.67 | 34.21 | False |
| 30 | anthropic | anthropic/claude-haiku-4.5 | 91.67 | 99.52 | 4.76 | 61.76 | 3.76 | False |
| 31 | z-ai | z-ai/glm-5 | 28.33 | 66.67 | 59.52 | 60.81 | 51.47 | False |
| 32 | qwen | qwen/qwen3.6-plus | 6.67 | 54.59 | 78.57 | 60.14 | 68.26 | False |
| 33 | anthropic | anthropic/claude-fable-5 | 100.0 | 100.0 | 0.0 | 60.0 | 0.0 | False |
| 34 | anthropic | anthropic/claude-opus-5 | 100.0 | 98.55 | 0.0 | 59.56 | 0.58 | False |
| 35 | anthropic | anthropic/claude-sonnet-4.5 | 30.0 | 52.66 | 50.0 | 58.8 | 52.94 | False |
| 36 | meta-llama | meta-llama/llama-4-maverick | 0.0 | 40.1 | 78.57 | 58.46 | 75.39 | False |
| 37 | google | google/gemini-3.5-flash | 53.33 | 74.88 | 50.0 | 56.13 | 39.38 | False |
| 38 | meta-llama | meta-llama/llama-3.3-70b-instruct | 5.83 | 40.58 | 80.95 | 55.56 | 74.98 | False |
| 39 | deepseek | deepseek/deepseek-v3.2 | 2.5 | 38.65 | 85.71 | 54.88 | 78.32 | False |
| 40 | google | google/gemini-3.5-flash-lite | 0.83 | 29.47 | 80.95 | 54.22 | 80.43 | False |
| 41 | deepseek | deepseek/deepseek-v4-flash | 1.67 | 32.85 | 85.71 | 53.47 | 80.81 | False |
| 42 | meta-llama | meta-llama/llama-4-scout | 1.67 | 32.85 | 88.1 | 52.76 | 81.77 | False |
| 43 | deepseek | deepseek/deepseek-v4-pro | 4.17 | 21.84 | 85.71 | 49.17 | 84.71 | False |
| 44 | moonshotai | moonshotai/kimi-k2.6 | 15.0 | 38.65 | 90.48 | 48.45 | 77.73 | False |
| 45 | mistralai | mistralai/mistral-small-2603 | 0.0 | 28.02 | 100.0 | 48.41 | 88.79 | False |
| 46 | moonshotai | moonshotai/kimi-k2-thinking | 2.5 | 18.36 | 100.0 | 44.51 | 92.16 | False |
| 47 | deepseek | deepseek/deepseek-r1 | 3.33 | 9.66 | 95.24 | 42.99 | 93.57 | False |
| 48 | google | google/gemini-2.5-pro | 7.5 | 14.49 | 97.62 | 42.06 | 91.75 | False |
| 49 | mistralai | mistralai/mistral-large-2512 | 0.0 | 6.28 | 100.0 | 41.88 | 97.49 | False |
| 50 | mistralai | mistralai/mistral-medium-3.1 | 0.0 | 5.8 | 100.0 | 41.74 | 97.68 | False |
| 51 | deepseek | deepseek/deepseek-r1-0528 | 8.33 | 6.76 | 100.0 | 38.7 | 95.63 | False |

## Misuse-susceptibility board (higher = more misuse-susceptible)

| misuse_rank | model | misuse↑ | coop=100−FRR | trr_gap=100−TRR | JSR | score_rank |
|------------:|-------|--------:|-------------:|----------------:|----:|-----------:|
| 1 | mistralai/mistral-medium-3.1 | 97.68 | 100.0 | 94.2 | 100.0 | 50 |
| 2 | mistralai/mistral-large-2512 | 97.49 | 100.0 | 93.72 | 100.0 | 49 |
| 3 | deepseek/deepseek-r1-0528 | 95.63 | 91.67 | 93.24 | 100.0 | 51 |
| 4 | deepseek/deepseek-r1 | 93.57 | 96.67 | 90.34 | 95.24 | 47 |
| 5 | moonshotai/kimi-k2-thinking | 92.16 | 97.5 | 81.64 | 100.0 | 46 |
| 6 | google/gemini-2.5-pro | 91.75 | 92.5 | 85.51 | 97.62 | 48 |
| 7 | mistralai/mistral-small-2603 | 88.79 | 100.0 | 71.98 | 100.0 | 45 |
| 8 | deepseek/deepseek-v4-pro | 84.71 | 95.83 | 78.16 | 85.71 | 43 |
| 9 | meta-llama/llama-4-scout | 81.77 | 98.33 | 67.15 | 88.1 | 42 |
| 10 | deepseek/deepseek-v4-flash | 80.81 | 98.33 | 67.15 | 85.71 | 41 |
| 11 | google/gemini-3.5-flash-lite | 80.43 | 99.17 | 70.53 | 80.95 | 40 |
| 12 | deepseek/deepseek-v3.2 | 78.32 | 97.5 | 61.35 | 85.71 | 39 |
| 13 | moonshotai/kimi-k2.6 | 77.73 | 85.0 | 61.35 | 90.48 | 44 |
| 14 | meta-llama/llama-4-maverick | 75.39 | 100.0 | 59.9 | 78.57 | 36 |
| 15 | meta-llama/llama-3.3-70b-instruct | 74.98 | 94.17 | 59.42 | 80.95 | 38 |
| 16 | qwen/qwen3.6-plus | 68.26 | 93.33 | 45.41 | 78.57 | 32 |
| 17 | anthropic/claude-sonnet-4.5 | 52.94 | 70.0 | 47.34 | 50.0 | 35 |
| 18 | google/gemini-2.5-flash | 51.5 | 99.17 | 41.06 | 38.1 | 18 |
| 19 | z-ai/glm-5 | 51.47 | 71.67 | 33.33 | 59.52 | 31 |
| 20 | z-ai/glm-4.7-flash | 49.23 | 81.67 | 22.71 | 59.52 | 27 |
| 21 | google/gemini-2.5-flash-lite | 48.4 | 96.67 | 20.29 | 52.38 | 11 |
| 22 | anthropic/claude-opus-4.6 | 46.98 | 95.0 | 29.47 | 40.48 | 10 |
| 23 | x-ai/grok-4.20 | 46.08 | 97.5 | 18.84 | 47.62 | 8 |
| 24 | x-ai/grok-4.5 | 45.51 | 84.17 | 19.32 | 52.38 | 22 |
| 25 | z-ai/glm-5.2 | 43.6 | 85.0 | 21.26 | 45.24 | 21 |
| 26 | google/gemini-3.5-flash | 39.38 | 46.67 | 25.12 | 50.0 | 37 |
| 27 | moonshotai/kimi-k3 | 38.61 | 78.33 | 14.49 | 42.86 | 20 |
| 28 | qwen/qwen3.6-flash | 38.08 | 90.0 | 14.49 | 35.71 | 6 |
| 29 | openai/gpt-5.6-luna | 36.39 | 88.33 | 11.11 | 35.71 | 5 |
| 30 | openai/gpt-5.5 | 36.11 | 79.17 | 14.98 | 35.71 | 16 |
| 31 | openai/o3-mini | 36.09 | 99.17 | 12.08 | 28.57 | 2 |
| 32 | google/gemini-3.6-flash | 34.21 | 53.33 | 20.77 | 38.1 | 29 |
| 33 | z-ai/glm-5.1 | 33.57 | 75.83 | 19.81 | 26.19 | 15 |
| 34 | qwen/qwen3.7-max | 33.41 | 66.67 | 14.49 | 35.71 | 23 |
| 35 | openai/gpt-5.6-terra | 32.87 | 91.67 | 10.14 | 26.19 | 3 |
| 36 | anthropic/claude-opus-4.8 | 31.68 | 73.33 | 11.59 | 30.95 | 14 |
| 37 | openai/gpt-5.6-sol | 30.21 | 71.67 | 11.11 | 28.57 | 12 |
| 38 | anthropic/claude-sonnet-4.6 | 29.13 | 70.83 | 18.36 | 19.05 | 9 |
| 39 | qwen/qwen3.7-plus | 28.95 | 49.17 | 12.08 | 35.71 | 28 |
| 40 | openai/o4-mini | 26.91 | 92.5 | 4.35 | 16.67 | 1 |
| 41 | qwen/qwen3.5-397b-a17b | 23.52 | 58.33 | 8.21 | 21.43 | 19 |
| 42 | x-ai/grok-4.3 | 23.27 | 66.67 | 5.8 | 19.05 | 7 |
| 43 | anthropic/claude-sonnet-5 | 20.68 | 57.5 | 6.28 | 16.67 | 17 |
| 44 | openai/gpt-5.4 | 19.38 | 56.67 | 8.21 | 11.9 | 13 |
| 45 | google/gemini-3.1-pro-preview | 15.46 | 40.0 | 6.76 | 11.9 | 25 |
| 46 | openai/o3 | 12.11 | 56.67 | 1.93 | 0.0 | 4 |
| 47 | openai/gpt-5.4-nano | 6.63 | 28.33 | 2.42 | 0.0 | 24 |
| 48 | openai/gpt-5.4-mini | 4.72 | 21.67 | 0.97 | 0.0 | 26 |
| 49 | anthropic/claude-haiku-4.5 | 3.76 | 8.33 | 0.48 | 4.76 | 30 |
| 50 | anthropic/claude-opus-5 | 0.58 | 0.0 | 1.45 | 0.0 | 34 |
| 51 | anthropic/claude-fable-5 | 0.0 | 0.0 | 0.0 | 0.0 | 33 |
