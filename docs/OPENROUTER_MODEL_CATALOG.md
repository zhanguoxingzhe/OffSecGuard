# OpenRouter 模型目录（说明）

> **人读选型表（梳理版）**：[`OPENROUTER_MODEL_LIST.md`](./OPENROUTER_MODEL_LIST.md)  
> **机器可读**：[`configs/batch/openrouter_mainstream_models.yaml`](../configs/batch/openrouter_mainstream_models.yaml)  
> 刷新：`python scripts/refresh_openrouter_catalog.py`（会同步重写 LIST）

---

## 三层清单（不要混用）

| 层级 | YAML 字段 | 规模 | 用途 |
|------|-----------|------|------|
| 冒烟 | `batch_width_smoke` | ~17 | 每厂 1 个，测连通 |
| **选型主跑** | **`batch_select_core`** | **~52** | 同代**基线**（不含 -pro/-fast）+ `paperguru/guru-pro-1.2` |
| 扩展 | `batch_select_extended` | ~45 | 同代 Pro/Fast（入围后补）+ 上一代 + P1 厂 |
| 自动发现 | `discovered_extras` | 变动 | **默认不跑**，防列表膨胀 |

`paperguru/guru-pro-1.2`（非 OpenRouter，自有端点）**已并入** `batch_select_core`。

---

## 选型主跑覆盖什么

**原则：同代先跑基线**；`*-pro` / `*-fast` 放入 extended，入围后再补。  
（`gemini-*-pro`、`deepseek-v4-pro` 等是产品档位名，仍留在 core。）

**OpenAI**：`gpt-5.6` 三线基线 sol/terra/luna → 5.5 → 5.4（含 mini/nano）→ o3 / o3-mini / o4-mini  

**Anthropic**：Opus 5 / 4.8 / 4.6 · Fable 5 · Sonnet 5 / 4.6 / 4.5 · Haiku 4.5（无 Fast）  

**Google**：3.1 Pro · 3.6/3.5 Flash(+Lite) · 2.5 Pro/Flash/Lite  

**DeepSeek**：V4 Pro/Flash · V3.2 · R1 / R1-0528  

**Qwen**：3.7 Max/Plus · 3.6 Plus/Flash · 3.5-397B  

**Meta / Mistral / xAI / Kimi / GLM**：各 2–3 档关键代际  

扩展层再补：Amazon / MiniMax / Seed / Cohere / NVIDIA / 腾讯 / 小米，以及更旧对照。

---

## 怎么跑

```bash
python scripts/refresh_openrouter_catalog.py

# 列出选型主跑 ID
python -c "import yaml;d=yaml.safe_load(open('configs/batch/openrouter_mainstream_models.yaml',encoding='utf-8'));print('\n'.join(x['id'] for x in d['batch_select_core']))"

python cli.py run --model openrouter/openai/gpt-5.6-sol \
  --eval-bundle agent_product --tier gold --judge \
  --config configs/presets/gold_frr_trr_jsr.yaml \
  --output-dir results/batch_select/openai_gpt-5.6-sol

# PaperGuru（主跑·基线；非 OpenRouter）
python cli.py run --model paperguru/guru-pro-1.2 \
  --eval-bundle agent_product --tier gold --judge \
  --config configs/presets/gold_frr_trr_jsr.yaml \
  --output-dir results/batch_select/paperguru_guru-pro-1.2
```

建议顺序：smoke（可选）→ **`batch_select_core`（基线，含 PaperGuru）** → 入围型号补跑同代 Pro/Fast（在 extended 前半）→ 其余 extended / `stress_redteam`。

---

## 分析约定

1. 跨厂：只比相同档位（如各厂 mid / 各厂最新 flagship）  
2. 同厂：画 gen 曲线（5.4→5.5→5.6；Sonnet 4.5→4.6→5）  
3. reasoning（o3/R1/thinking）单独成列，不与 chat 旗舰混排  

完整表格见 [`OPENROUTER_MODEL_LIST.md`](./OPENROUTER_MODEL_LIST.md)。
