# OpenRouter 选型模型清单（梳理版）

> 生成自 `configs/batch/openrouter_mainstream_models.yaml` · `2026-07-26T14:42:24.402690+00:00`  
> 刷新：`python scripts/refresh_openrouter_catalog.py`

## 图例（表格「批次」列）

| 标注 | 含义 | 何时跑 |
|------|------|--------|
| **主跑·基线** | 同代默认款（无 -pro/-fast） | **现在就跑** |
| **延后·Pro/Fast** | 同代加速/高算力变体 | 基线入围后再补 |
| **扩展·代际** | 更旧代际对照 | 需要曲线时再跑 |
| **扩展·P1厂** | 第二批厂商 | core 之后 |

规模：主跑基线 **52** · 扩展合计 **47** · 冒烟 17 · 自动发现未入选 39

说明：`gemini-*-pro` / `deepseek-v4-pro` 等是**产品档位名**，标为主跑基线，不是同款 Pro 变体。

---

## 厂商梯队

### OpenAI (`openai`)

本厂：主跑基线 **10** · 延后 Pro/Fast **8** · 其余扩展 4

| 批次 | 代际 | 档位 | OpenRouter ID | $/M in | 说明 |
|------|------|------|---------------|--------|------|
| **主跑·基线** | 5.4 | flagship | **`openai/gpt-5.4`** | 2.5 | 基线旗舰 |
| **主跑·基线** | 5.4 | lite | **`openai/gpt-5.4-nano`** | 0.2 | 5.4 Nano |
| **主跑·基线** | 5.4 | mid | **`openai/gpt-5.4-mini`** | 0.75 | 5.4 Mini |
| **主跑·基线** | 5.5 | flagship | **`openai/gpt-5.5`** | 5.0 | 5.5 |
| **主跑·基线** | 5.6-luna | lite | **`openai/gpt-5.6-luna`** | 1.0 | 5.6 Luna |
| **主跑·基线** | 5.6-sol | flagship | **`openai/gpt-5.6-sol`** | 5.0 | 5.6 Sol |
| **主跑·基线** | 5.6-terra | mid | **`openai/gpt-5.6-terra`** | 2.5 | 5.6 Terra |
| **主跑·基线** | o3 | reasoning | **`openai/o3`** | 2.0 | o3 |
| **主跑·基线** | o3 | reasoning | **`openai/o3-mini`** | 1.1 | o3 Mini |
| **主跑·基线** | o4 | reasoning | **`openai/o4-mini`** | 1.1 | o4 Mini |
| 延后·Pro/Fast | 5.4 | flagship | `openai/gpt-5.4-pro` | 30.0 | 5.4 Pro |
| 延后·Pro/Fast | 5.5 | flagship | `openai/gpt-5.5-pro` | 30.0 | 5.5 Pro |
| 延后·Pro/Fast | 5.6-luna | lite | `openai/gpt-5.6-luna-pro` | 1.0 | 5.6 Luna Pro |
| 延后·Pro/Fast | 5.6-sol | flagship | `openai/gpt-5.6-sol-pro` | 5.0 | 5.6 Sol Pro |
| 延后·Pro/Fast | 5.6-terra | mid | `openai/gpt-5.6-terra-pro` | 2.5 | 5.6 Terra Pro |
| 延后·Pro/Fast | o3 | reasoning | `openai/o3-mini-high` | 1.1 | o3 Mini High |
| 延后·Pro/Fast | o3 | reasoning | `openai/o3-pro` | 20.0 | o3 Pro |
| 延后·Pro/Fast | o4 | reasoning | `openai/o4-mini-high` | 1.1 | o4 Mini High |
| 扩展·代际 | 4o | previous | `openai/gpt-4o` | 2.5 | GPT-4o 对照 |
| 扩展·代际 | 5.0 | previous | `openai/gpt-5` | 1.25 | GPT-5 |
| 扩展·代际 | 5.1 | previous | `openai/gpt-5.1` | 1.25 | 5.1 |
| 扩展·代际 | 5.2 | previous | `openai/gpt-5.2` | 1.75 | 5.2 |

### Anthropic (`anthropic`)

本厂：主跑基线 **8** · 延后 Pro/Fast **3** · 其余扩展 3

| 批次 | 代际 | 档位 | OpenRouter ID | $/M in | 说明 |
|------|------|------|---------------|--------|------|
| **主跑·基线** | fable-5 | flagship | **`anthropic/claude-fable-5`** | 10.0 | Fable 5 |
| **主跑·基线** | haiku-4.5 | lite | **`anthropic/claude-haiku-4.5`** | 1.0 | Haiku 4.5 |
| **主跑·基线** | opus-4.6 | flagship | **`anthropic/claude-opus-4.6`** | 5.0 | Opus 4.6 |
| **主跑·基线** | opus-4.8 | flagship | **`anthropic/claude-opus-4.8`** | 5.0 | Opus 4.8 |
| **主跑·基线** | opus-5 | flagship | **`anthropic/claude-opus-5`** | 5.0 | Opus 5 |
| **主跑·基线** | sonnet-4.5 | previous | **`anthropic/claude-sonnet-4.5`** | 3.0 | Sonnet 4.5 |
| **主跑·基线** | sonnet-4.6 | mid | **`anthropic/claude-sonnet-4.6`** | 3.0 | Sonnet 4.6 |
| **主跑·基线** | sonnet-5 | mid | **`anthropic/claude-sonnet-5`** | 2.0 | Sonnet 5 |
| 延后·Pro/Fast | opus-4.7 | flagship | `anthropic/claude-opus-4.7-fast` | 30.0 | Opus 4.7 Fast |
| 延后·Pro/Fast | opus-4.8 | flagship | `anthropic/claude-opus-4.8-fast` | 10.0 | Opus 4.8 Fast |
| 延后·Pro/Fast | opus-5 | flagship | `anthropic/claude-opus-5-fast` | 10.0 | Opus 5 Fast |
| 扩展·代际 | opus-4.5 | previous | `anthropic/claude-opus-4.5` | 5.0 | Opus 4.5 |
| 扩展·代际 | opus-4.7 | flagship | `anthropic/claude-opus-4.7` | 5.0 | Opus 4.7 |
| 扩展·代际 | sonnet-4 | previous | `anthropic/claude-sonnet-4` | 3.0 | Sonnet 4 |

### Google (`google`)

本厂：主跑基线 **7** · 延后 Pro/Fast **0** · 其余扩展 3

| 批次 | 代际 | 档位 | OpenRouter ID | $/M in | 说明 |
|------|------|------|---------------|--------|------|
| **主跑·基线** | 2.5 | flagship | **`google/gemini-2.5-pro`** | 1.25 | 2.5 Pro |
| **主跑·基线** | 2.5 | lite | **`google/gemini-2.5-flash-lite`** | 0.1 | 2.5 Lite |
| **主跑·基线** | 2.5 | mid | **`google/gemini-2.5-flash`** | 0.3 | 2.5 Flash |
| **主跑·基线** | 3.1 | flagship | **`google/gemini-3.1-pro-preview`** | 2.0 | 3.1 Pro |
| **主跑·基线** | 3.5 | lite | **`google/gemini-3.5-flash-lite`** | 0.3 | 3.5 Lite |
| **主跑·基线** | 3.5 | mid | **`google/gemini-3.5-flash`** | 1.5 | 3.5 Flash |
| **主跑·基线** | 3.6 | mid | **`google/gemini-3.6-flash`** | 1.5 | 3.6 Flash 最新 |
| 扩展·代际 | 3.0 | mid | `google/gemini-3-flash-preview` | 0.5 | 3 Flash Preview |
| 扩展·代际 | 3.1 | lite | `google/gemini-3.1-flash-lite` | 0.25 | 3.1 Lite |
| 扩展·代际 | gemma-4 | mid | `google/gemma-4-31b-it` | 0.14 | Gemma 4 31B |

### DeepSeek (`deepseek`)

本厂：主跑基线 **5** · 延后 Pro/Fast **0** · 其余扩展 1

| 批次 | 代际 | 档位 | OpenRouter ID | $/M in | 说明 |
|------|------|------|---------------|--------|------|
| **主跑·基线** | r1 | reasoning | **`deepseek/deepseek-r1`** | 0.7 | R1 |
| **主跑·基线** | r1 | reasoning | **`deepseek/deepseek-r1-0528`** | 0.5 | R1-0528 |
| **主跑·基线** | v3.2 | mid | **`deepseek/deepseek-v3.2`** | 0.269 | V3.2 |
| **主跑·基线** | v4 | flagship | **`deepseek/deepseek-v4-pro`** | 0.435 | V4 Pro |
| **主跑·基线** | v4 | lite | **`deepseek/deepseek-v4-flash`** | 0.14 | V4 Flash |
| 扩展·代际 | v3.1 | previous | `deepseek/deepseek-chat-v3.1` | 0.25 | V3.1 |

### Alibaba Qwen (`qwen`)

本厂：主跑基线 **5** · 延后 Pro/Fast **0** · 其余扩展 2

| 批次 | 代际 | 档位 | OpenRouter ID | $/M in | 说明 |
|------|------|------|---------------|--------|------|
| **主跑·基线** | 3.5-open | mid | **`qwen/qwen3.5-397b-a17b`** | 0.39 | 397B MoE |
| **主跑·基线** | 3.6 | lite | **`qwen/qwen3.6-flash`** | 0.1875 | 3.6 Flash |
| **主跑·基线** | 3.6 | mid | **`qwen/qwen3.6-plus`** | 0.325 | 3.6 Plus |
| **主跑·基线** | 3.7 | flagship | **`qwen/qwen3.7-max`** | 1.475 | 3.7 Max |
| **主跑·基线** | 3.7 | mid | **`qwen/qwen3.7-plus`** | 0.32 | 3.7 Plus |
| 扩展·代际 | 3-max | reasoning | `qwen/qwen3-max-thinking` | 0.78 | Max Thinking |
| 扩展·代际 | 3.6 | flagship | `qwen/qwen3.6-max-preview` | 1.04 | 3.6 Max Preview |

### Meta (`meta-llama`)

本厂：主跑基线 **3** · 延后 Pro/Fast **0** · 其余扩展 1

| 批次 | 代际 | 档位 | OpenRouter ID | $/M in | 说明 |
|------|------|------|---------------|--------|------|
| **主跑·基线** | 3.3 | previous | **`meta-llama/llama-3.3-70b-instruct`** | 0.13 | 3.3 70B |
| **主跑·基线** | 4 | flagship | **`meta-llama/llama-4-maverick`** | 0.2 | Maverick |
| **主跑·基线** | 4 | mid | **`meta-llama/llama-4-scout`** | 0.1 | Scout |
| 扩展·代际 | 3.1 | lite | `meta-llama/llama-3.1-8b-instruct` | 0.05 | 3.1 8B |

### Mistral (`mistralai`)

本厂：主跑基线 **3** · 延后 Pro/Fast **0** · 其余扩展 2

| 批次 | 代际 | 档位 | OpenRouter ID | $/M in | 说明 |
|------|------|------|---------------|--------|------|
| **主跑·基线** | large-3 | flagship | **`mistralai/mistral-large-2512`** | 0.5 | Large 2512 |
| **主跑·基线** | medium-3 | mid | **`mistralai/mistral-medium-3.1`** | 0.4 | Medium 3.1 |
| **主跑·基线** | small-4 | lite | **`mistralai/mistral-small-2603`** | 0.15 | Small 2603 |
| 扩展·代际 | devstral | mid | `mistralai/devstral-2512` | 0.4 | Devstral |
| 扩展·代际 | medium-3 | previous | `mistralai/mistral-medium-3` | 0.4 | Medium 3 |

### xAI (`x-ai`)

本厂：主跑基线 **3** · 延后 Pro/Fast **0** · 其余扩展 0

| 批次 | 代际 | 档位 | OpenRouter ID | $/M in | 说明 |
|------|------|------|---------------|--------|------|
| **主跑·基线** | 4.20 | previous | **`x-ai/grok-4.20`** | 1.25 | Grok 4.20 |
| **主跑·基线** | 4.3 | mid | **`x-ai/grok-4.3`** | 1.25 | Grok 4.3 |
| **主跑·基线** | 4.5 | flagship | **`x-ai/grok-4.5`** | 2.0 | Grok 4.5 |

### Moonshot (Kimi) (`moonshotai`)

本厂：主跑基线 **3** · 延后 Pro/Fast **0** · 其余扩展 1

| 批次 | 代际 | 档位 | OpenRouter ID | $/M in | 说明 |
|------|------|------|---------------|--------|------|
| **主跑·基线** | k2 | reasoning | **`moonshotai/kimi-k2-thinking`** | 0.6 | K2 Thinking |
| **主跑·基线** | k2.6 | mid | **`moonshotai/kimi-k2.6`** | 0.646 | K2.6 |
| **主跑·基线** | k3 | flagship | **`moonshotai/kimi-k3`** | 3.0 | K3 |
| 扩展·代际 | k2.5 | previous | `moonshotai/kimi-k2.5` | 0.57 | K2.5 |

### Zhipu / Z.ai (GLM) (`z-ai`)

本厂：主跑基线 **4** · 延后 Pro/Fast **0** · 其余扩展 1

| 批次 | 代际 | 档位 | OpenRouter ID | $/M in | 说明 |
|------|------|------|---------------|--------|------|
| **主跑·基线** | 4.7 | lite | **`z-ai/glm-4.7-flash`** | 0.06 | 4.7 Flash |
| **主跑·基线** | 5.0 | previous | **`z-ai/glm-5`** | 0.95 | GLM 5 |
| **主跑·基线** | 5.1 | mid | **`z-ai/glm-5.1`** | 0.966 | GLM 5.1 |
| **主跑·基线** | 5.2 | flagship | **`z-ai/glm-5.2`** | 0.6692 | GLM 5.2 |
| 扩展·代际 | 4.7 | previous | `z-ai/glm-4.7` | 0.4 | GLM 4.7 |

### Amazon (`amazon`)

本厂：主跑基线 **0** · 延后 Pro/Fast **0** · 其余扩展 3

| 批次 | 代际 | 档位 | OpenRouter ID | $/M in | 说明 |
|------|------|------|---------------|--------|------|
| 扩展·P1厂 | nova-1 | flagship | `amazon/nova-premier-v1` | 2.5 | Premier |
| 扩展·P1厂 | nova-1 | mid | `amazon/nova-pro-v1` | 0.8 | Pro |
| 扩展·P1厂 | nova-2 | lite | `amazon/nova-2-lite-v1` | 0.3 | 2 Lite |

### MiniMax (`minimax`)

本厂：主跑基线 **0** · 延后 Pro/Fast **0** · 其余扩展 3

| 批次 | 代际 | 档位 | OpenRouter ID | $/M in | 说明 |
|------|------|------|---------------|--------|------|
| 扩展·P1厂 | m2.5 | previous | `minimax/minimax-m2.5` | 0.15 | M2.5 |
| 扩展·P1厂 | m2.7 | mid | `minimax/minimax-m2.7` | 0.25 | M2.7 |
| 扩展·P1厂 | m3 | flagship | `minimax/minimax-m3` | 0.3 | M3 |

### ByteDance Seed (`bytedance-seed`)

本厂：主跑基线 **0** · 延后 Pro/Fast **0** · 其余扩展 3

| 批次 | 代际 | 档位 | OpenRouter ID | $/M in | 说明 |
|------|------|------|---------------|--------|------|
| 扩展·P1厂 | 1.6 | previous | `bytedance-seed/seed-1.6` | 0.25 | 1.6 |
| 扩展·P1厂 | 2.0 | lite | `bytedance-seed/seed-2.0-mini` | 0.1 | 2.0 Mini |
| 扩展·P1厂 | 2.0 | mid | `bytedance-seed/seed-2.0-lite` | 0.25 | 2.0 Lite |

### Cohere (`cohere`)

本厂：主跑基线 **0** · 延后 Pro/Fast **0** · 其余扩展 2

| 批次 | 代际 | 档位 | OpenRouter ID | $/M in | 说明 |
|------|------|------|---------------|--------|------|
| 扩展·P1厂 | command-a | flagship | `cohere/command-a` | 2.5 | Command A |
| 扩展·P1厂 | r+ | mid | `cohere/command-r-plus-08-2024` | 2.5 | R+ |

### NVIDIA (`nvidia`)

本厂：主跑基线 **0** · 延后 Pro/Fast **0** · 其余扩展 3

| 批次 | 代际 | 档位 | OpenRouter ID | $/M in | 说明 |
|------|------|------|---------------|--------|------|
| 扩展·P1厂 | 3 | flagship | `nvidia/nemotron-3-ultra-550b-a55b` | 0.6 | Ultra |
| 扩展·P1厂 | 3 | lite | `nvidia/nemotron-3-nano-30b-a3b` | 0.05 | Nano |
| 扩展·P1厂 | 3 | mid | `nvidia/nemotron-3-super-120b-a12b` | 0.085 | Super |

### Tencent (`tencent`)

本厂：主跑基线 **0** · 延后 Pro/Fast **0** · 其余扩展 2

| 批次 | 代际 | 档位 | OpenRouter ID | $/M in | 说明 |
|------|------|------|---------------|--------|------|
| 扩展·P1厂 | hy3 | flagship | `tencent/hy3` | 0.132 | Hy3 |
| 扩展·P1厂 | hy3 | mid | `tencent/hy3-preview` | 0.063 | Hy3 preview |

### Xiaomi (`xiaomi`)

本厂：主跑基线 **0** · 延后 Pro/Fast **0** · 其余扩展 2

| 批次 | 代际 | 档位 | OpenRouter ID | $/M in | 说明 |
|------|------|------|---------------|--------|------|
| 扩展·P1厂 | 2.5 | flagship | `xiaomi/mimo-v2.5-pro` | 0.435 | Pro |
| 扩展·P1厂 | 2.5 | mid | `xiaomi/mimo-v2.5` | 0.14 | 标准 |

---

## 宽度冒烟（每厂 1 个 · 连通性）

- `openai/gpt-5.6-sol`
- `anthropic/claude-sonnet-5`
- `google/gemini-3.6-flash`
- `deepseek/deepseek-v4-pro`
- `qwen/qwen3.7-plus`
- `meta-llama/llama-4-maverick`
- `mistralai/mistral-large-2512`
- `x-ai/grok-4.5`
- `moonshotai/kimi-k3`
- `z-ai/glm-5.2`
- `amazon/nova-pro-v1`
- `minimax/minimax-m3`
- `bytedance-seed/seed-2.0-lite`
- `cohere/command-a`
- `nvidia/nemotron-3-super-120b-a12b`
- `tencent/hy3`
- `xiaomi/mimo-v2.5-pro`

---

## 非 OpenRouter（已入主跑·基线）

- **主跑·基线** `paperguru/guru-pro-1.2` — own endpoint via PAPERGURU_*; 主跑·基线

## 跑法摘要

1. 只跑表格里 **主跑·基线**（=`batch_select_core`，含 PaperGuru）
2. 入围后补同一行代际的 **延后·Pro/Fast**
3. 需要代际曲线或更多厂商时再跑其余扩展
