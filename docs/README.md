# OffSec Guard 文档索引

> 维护约定：改评测口径 / 判定器 / Gold / 评分公式 / CLI / **能力轴**时，同步更新对应文档，并在 [`PAPER_METHODOLOGY.md`](./PAPER_METHODOLOGY.md) §7 时间线记一笔。  
> 最近梳理：2026-07-28

---

## 产品主目标从哪读

| 优先级 | 文档 | 用途 |
|:---:|------|------|
| 0 | [`PRODUCT_DECISIONS.md`](./PRODUCT_DECISIONS.md) | **主目标决策**：Gate / Tier / 判官 / 范围 / 评测包 / **双轴选型** |
| 1 | [`CAPABILITY_EVAL.md`](./CAPABILITY_EVAL.md) | **能力代理屏** TSR/OAR/PQR、造题协议、与结果型 GT 分工 |
| 2 | [`EVAL_BUNDLES.md`](./EVAL_BUNDLES.md) | **多消费者评测包**与 prompt 压力档（floor/product/ceiling） |
| 3 | [`EVAL_STRATEGY.md`](./EVAL_STRATEGY.md) | Eval-First 与护栏 Gold |
| 4 | [`CLI_REFERENCE.md`](./CLI_REFERENCE.md) | 复现与门禁命令 |

## 写论文 / 白皮书从哪读

| 优先级 | 文档 | 用途 |
|:---:|------|------|
| 1 | [`PAPER_METHODOLOGY.md`](./PAPER_METHODOLOGY.md) | Methods / Experiments / Limitations 主参考 |
| 2 | [`JUDGE_DESIGN.md`](./JUDGE_DESIGN.md) | 两阶段拒答判定完整设计 |
| 3 | [`SCORING.md`](./SCORING.md) | FRR/TRR/JSR 计分、加权、Tier、`misuse_risk` |
| 4 | [`CAPABILITY_EVAL.md`](./CAPABILITY_EVAL.md) | 第二轴能力评估口径与 Limitations |
| 5 | [`EVAL_STRATEGY.md`](./EVAL_STRATEGY.md) | Eval-First 与 Gold 策略 |
| 6 | [`DATASET_FREEZE.md`](./DATASET_FREEZE.md) | Gold 冻结算法、蒸馏、脚本索引 |
| 7 | [`ALIGNMENT.md`](./ALIGNMENT.md) | 与生产 Engine（PAIStrike）对齐 |
| 8 | [`CLI_REFERENCE.md`](./CLI_REFERENCE.md) | 复现实验命令与 ENV |
| 9 | 根目录 [`SPECIFICATION.md`](../SPECIFICATION.md) | 愿景规范；**实现现状以本文档簇为准** |

---

## 按主题

| 主题 | 文档 |
|------|------|
| **产品决策 / Gate / Tier / 双轴选型** | `PRODUCT_DECISIONS.md` |
| **能力代理屏 TSR/OAR/PQR** | `CAPABILITY_EVAL.md` |
| **评测包 / 多场景消费** | `EVAL_BUNDLES.md` |
| **OpenRouter 选型清单** | `OPENROUTER_MODEL_LIST.md`（表）· `OPENROUTER_MODEL_CATALOG.md`（说明）· `configs/batch/` |
| 指标定义 / Tier 阈值（规范） | `SPECIFICATION.md` §2–5 |
| 指标二元化与实验协议 | `PAPER_METHODOLOGY.md` §1、§3 |
| 评分实现与 bug | `SCORING.md` |
| 拒答五级 + 规则/Judge | `JUDGE_DESIGN.md`、`SPECIFICATION.md` §4 |
| 数据配额与范围 | `DATASET_PLAN.md` |
| Gold / Extended / Research | `EVAL_STRATEGY.md` |
| 冻结与蒸馏复现 | `DATASET_FREEZE.md`、`DISTILLATION_PLAN.md` |
| LangSmith DuckDB 交接 | `LANGSMITH_DATA_HANDOFF.md` |
| System prompt / 工具名 | `ALIGNMENT.md`、`offsec_guard/core/taxonomy.py` |
| CLI | `CLI_REFERENCE.md` |
| 外部 exporter 草稿（非本框架） | `plan.md`（勿当 OffSecGuard 实现文档引用） |

---

## 代码 ↔ 文档映射

| 代码 | 文档 |
|------|------|
| `judges/refusal_detector.py` | `JUDGE_DESIGN.md` §2 |
| `judges/llm_judge.py` + `composite.py` | `JUDGE_DESIGN.md` §3–4 |
| `dimensions/frr.py` / `trr.py` | `PAPER_METHODOLOGY.md` §1、`ALIGNMENT.md` §5 |
| `pipeline/executor.py` + `models.classify_tier` | `SCORING.md` |
| `core/taxonomy.py` | `ALIGNMENT.md`、`EVAL_BUNDLES.md`、`JUDGE_DESIGN.md` §5 |
| `core/eval_bundles.py` | `EVAL_BUNDLES.md`、`PRODUCT_DECISIONS.md` D9 |
| `cli.py` | `CLI_REFERENCE.md` |
| `scripts/freeze_frr_gold.py` | `DATASET_FREEZE.md` |
| `scripts/distill_from_duckdb.py` | `DATASET_FREEZE.md`、`DISTILLATION_PLAN.md` |
| `scripts/distill_capability_from_duckdb.py` | `CAPABILITY_EVAL.md`、`DATASET_FREEZE.md` |
| `scripts/gen_capability_gapfill.py` / `calibrate_capability_teachers.py` / `run_capability_eval.py` | `CAPABILITY_EVAL.md` |
| `offsec_guard/scoring/capability_match.py` | `CAPABILITY_EVAL.md`、`SCORING.md` §6 |
| `configs/presets/*.yaml` | `CLI_REFERENCE.md` §配置 |
| `tests/test_refusal_detector.py` 等 | `JUDGE_DESIGN.md` §6 |
