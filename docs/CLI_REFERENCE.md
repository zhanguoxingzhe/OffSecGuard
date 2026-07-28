# CLI 参考（实现口径）

> 入口：`cli.py`（安装后命令名 `pentestai-eval`）  
> 最近更新：2026-07-26  
> **注意**：`SPECIFICATION.md` §11 中的部分命令为愿景设计，以下以代码为准。

---

## 1. 子命令

| 命令 | 状态 | 说明 |
|------|------|------|
| `run` | ✅ | 跑评估 |
| `report` | ✅ 部分 | 从 JSON 重生报告；`md`/`json` 可用，`html` **未实现** |
| `compare` | ❌ | SPEC 有，代码无 |
| `dataset` | ❌ | SPEC 有，代码无 |

---

## 2. `run` 参数

| 参数 | 默认 | 说明 |
|------|------|------|
| `--model` | 必填 | `provider/model_id`，如 `openrouter/openai/gpt-5.4` 或 `paperguru/guru-pro-1.2` |
| `--provider` | `openrouter` | 可被 model 前缀覆盖（paperguru） |
| `--base-url` | openrouter 默认 | 非 paperguru 时生效；paperguru 走 `PAPERGURU_BASE_URL` |
| `--api-key` | 空 | 否则读 ENV |
| `--dims` | `frr` | 逗号分隔：`frr,trr,jsr` |
| `--config` | 空 | YAML 路径，如 `configs/presets/gold_frr_trr_jsr.yaml` |
| `--preset` | 空 | **仅权重名**：`internal_research` \| `saas_product` \| `model_comparison`（**不是文件路径**） |
| `--eval-bundle` | 空 | **推荐**：`agent_product` \| `assistant_safety` \| `stress_redteam` \| `paper_main`（见 `EVAL_BUNDLES.md`） |
| `--prompt-profile-frr/trr/jsr` | 空 | 覆盖单维压力档：`floor` \| `product` \| `ceiling`（一般用 bundle） |
| `--tier` | 空 | `gold`：FRR←`datasets/v1/gold/frr.jsonl`；TRR/JSR←`samples/`；空/`all`：samples 全量 |
| `--dataset` | 空 | 自定义单一 `.jsonl`（覆盖内置加载） |
| `--samples` | 0 | 最大条数，0=不截断（按加载逻辑累加） |
| `--concurrency` | 4 | 异步并发 |
| `--output-dir` | `results` | 输出根目录 |
| `--no-resume` | off | 忽略并清空 `checkpoint.jsonl` / `run_meta.json` 后重跑 |
| `--keep-errors` | off | 续跑时保留 `verdict=error`（默认会重试 error） |
| `--exit-code` | off | CI：FRR **fail_rate &gt; 10** 则 exit 1（硬编码） |
| `--judge` | off | 启用结构化 LLM Judge |
| `--no-judge` | off | 强制关闭 Judge |
| `--judge-model` | 见 ENV/配置 | 默认 `paperguru/guru-pro-1.2` |
| `--judge-base-url` | 空 | 判官 API |
| `--judge-api-key` | 空 | 判官 Key |

### `--eval-bundle` vs `--preset` vs `--config`

| | `--eval-bundle agent_product` | `--preset saas_product` | `--config path.yaml` |
|--|-------------------------------|-------------------------|----------------------|
| 作用 | 锁定 **profile×权重×Gate阈值×claim_tier** | **只覆盖 weights** | 加载完整 `EvalConfig` |
| 推荐 | 多场景选型 / CI 主入口 | 仅调权重时 | 与 bundle 组合（阈值/judge） |

YAML 可写 `eval_bundle: agent_product`（加载时 `apply_eval_bundle`）。  
错误示例（勿用）：`--preset configs/presets/xxx.yaml`  
正确：`--config configs/presets/xxx.yaml --eval-bundle agent_product`。

进攻 Agent CI 示例：

```bash
python cli.py run --model paperguru/guru-pro-1.2 \
  --eval-bundle agent_product --tier gold --judge \
  --config configs/presets/gold_frr_trr_jsr.yaml --exit-code
```

---

## 3. 环境变量

| 变量 | 用途 |
|------|------|
| `OPENROUTER_API_KEY` / `OPENAI_API_KEY` | 被测 / 默认判官 Key |
| `OPENAI_BASE_URL` / `OFFSEC_GUARD_BASE_URL` | OpenAI 兼容端点 |
| `PAPERGURU_API_KEY` / `PAPERGURU_BASE_URL` | PaperGuru |
| `OFFSEC_GUARD_PROVIDER` / `MODEL_ID` / `API_KEY` / `CONCURRENCY` / `OUTPUT_DIR` | `EvalConfig.from_env` |
| `OFFSEC_GUARD_JUDGE` | `1/true/yes` → 启用 Judge |
| `JUDGE_MODEL` / `JUDGE_API_KEY` / `JUDGE_BASE_URL` | 判官；默认 PaperGuru，Key 缺省回落 `PAPERGURU_API_KEY` |

仓库根目录 `.env` 由 `python-dotenv` 加载（不覆盖已有 ENV）。**勿把密钥提交进 git。**

---

## 4. 端点解析逻辑

`_resolve_endpoint`：

- model/provider 含 `paperguru` / `guru-pro` 等 → PaperGuru base + key  
- 否则 → OpenRouter / OpenAI 兼容  

判官客户端：始终用显式 `judge_base_url` 构造 `OpenAICompatibleClient`（避免 openrouter 工厂硬编码干扰）。

---

## 5. `--tier gold` 加载规则

```
if tier == gold:
  for dim in dims:
    if gold/<dim>.jsonl exists: load it
    else: warn + fallback samples/<dim>/*.jsonl
else:
  load all datasets/v1/samples/**/*.jsonl
```

要点（2026-07-26）：

- `gold/frr.jsonl` (120)、`gold/trr.jsonl` (187)、`gold/jsr.jsonl` (42)  
- 冻结：`scripts/freeze_frr_gold.py`、`scripts/freeze_trr_jsr_gold.py`  
- 输出另含 `sample_results.json`（逐条判定）  
- **逐条断点**（默认开）：`{output_dir}/checkpoint.jsonl` + `run_meta.json`；中断后同命令续跑；`--no-resume` 清空重来；`error` 默认重试  
- grey_zone / instrumental 无 gold、无专用 runner

路由（`PipelineExecutor._group_by_dimension`）：

| 条件 | 维度 |
|------|------|
| `expected_action == execute` | FRR |
| id 前缀 `jsr-` 或 tags 含 jailbreak 类 | JSR |
| 其他 | TRR |

---

## 6. 推荐复现命令

```bash
# 正式对比（固定共享判官 = PaperGuru，零边际成本）
python cli.py run --model openrouter/openai/gpt-5.4 \
  --dims frr,trr,jsr --tier gold --judge \
  --config configs/presets/gold_frr_trr_jsr.yaml \
  --output-dir results/gold_gpt54_judge_pg

python cli.py run --model paperguru/guru-pro-1.2 \
  --dims frr,trr,jsr --tier gold --judge \
  --config configs/presets/gold_frr_trr_jsr.yaml \
  --output-dir results/gold_paperguru_judge_pg

# 消融：仅规则
python cli.py run --model openrouter/openai/gpt-5.4 \
  --dims frr,trr,jsr --tier gold --no-judge \
  --config configs/presets/gold_frr_trr_jsr.yaml \
  --output-dir results/gold_gpt54_rules
```

输出：`{output_dir}/{eval_id}/summary.json` + `scorecard.md`。  
`config_snapshot` 含 `judge_enabled` / `judge_model`。

`results/` 默认在 `.gitignore`；论文附件需自行归档脱敏 summary。

---

## 7. 预设 YAML 一览

| 文件 | 用途 |
|------|------|
| `configs/presets/gold_frr_trr_jsr.yaml` | 全核心维度 + saas_product 权重；含 judge 字段注释 |
| `configs/presets/tier2_gold.yaml` | Tier2 阈值口径 |
| `configs/presets/quick_frr_only.yaml` | 快速 FRR |

`EvalConfig` 关键字段（节选）：`enabled_dimensions`、`max_frr_pct`、`min_trr_pct`、`max_jsr_pct`、`concurrency`、`max_tokens`、`temperature`、`judge_enabled`、`judge_provider`、`judge_model_id`、`judge_max_tokens`、`judge_temperature`。

Gate 阈值写入配置后**当前不阻断流水线**（见 `SCORING.md` §5）。
