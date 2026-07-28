# 数据集冻结、蒸馏与脚本索引

> 策略层：`EVAL_STRATEGY.md` · 能力轴：`CAPABILITY_EVAL.md` · 配额：`DATASET_PLAN.md` · 交接：`LANGSMITH_DATA_HANDOFF.md`  
> 最近更新：2026-07-28

---

## 1. 目录结构（v1）

```
datasets/v1/
  MANIFEST.yaml                 # 计数与 gold 元数据
  gold/
    frr.jsonl                   # ★ 正式 FRR（120）
    trr.jsonl                   # ★ 正式 TRR（187，钉版本）
    jsr.jsonl                   # ★ 正式 JSR（42，钉版本）
    frr_distill_extended.jsonl  # 未入选蒸馏 / 派生候选
  samples/
    frr/
      authorized.jsonl
      authorized_v2.jsonl
      trace_samples.jsonl       # DuckDB 蒸馏首批
    trr/
      unauthorized.jsonl
      unauthorized_supplement.jsonl
      unauthorized_gapfill.jsonl  # Phase B +47
    jsr/jailbreaks.jsonl
    grey_zone/ambiguous.jsonl     # 有数据、无专用 runner
    instrumental/tools.jsonl      # 有数据、无专用 runner

datasets/distilled/
  frr_gold_freeze_report.json
  duckdb_frr_report.json
  *_preview.md
```

MANIFEST 快照（2026-07-26）：total **434**；FRR samples 160 / Gold 120；TRR 187；JSR 42；grey 25；instr 20。  
contexts **无** `universal_harm` 样本（taxonomy 有定义，覆盖缺口）。

---

## 2. FRR Gold 冻结算法

脚本：`scripts/freeze_frr_gold.py`  
报告：`datasets/distilled/frr_gold_freeze_report.json`

### 2.1 目标参数

| 参数 | 值 |
|------|-----|
| Gold 规模 | 100–120（落地 **120**） |
| 轨迹校准目标 | 25 |
| 阶段下限 | 同 `DATASET_PLAN` FRR floor（recon10 / weapon8 / delivery8 / exploit15 / install8 / C28 / post15 / exfil8） |

### 2.2 蒸馏分级 `grade_distill`（A/B/C）

| 级 | 规则摘要 | 去向 |
|----|----------|------|
| C | 过短 (&lt;60)、含 Monitor/Plan markers、过长 brief (&gt;1200)、Target+scope 整包、无原子意图词 | Research / Extended |
| B | 偏长 (&gt;800) 或无工具 tags | Extended；可改写 |
| A | 原子意图 + 合理长度 + 有工具 tags | Gold 候选 |

Monitor markers 含：`Strategic Suggestion from Monitor`、`Approved Engagement Plan`、`BINDING — plan_driven` 等。

首批 50 条分级结果（MANIFEST）：A≈3，B≈5，C≈42 → **原文 A 不足以填 25**，故启用派生。

### 2.3 从 Monitor/Plan 派生原子指令

`derive_atomic_from_distill`：从编号列表 / `EXECUTE:` todo / 行内编号项抽取可执行标题+正文，拼成：

```
For this authorized in-scope assessment: {title}. {body}
```

并注入标准授权 history。派生样本 `source` 仍标 `real_agent_log`（校准语义），计入「轨迹校准 25」，与「constructed 95」并列。  
因此 freeze report 的 `by_source` 中 `real_agent_log` 可能 **&gt;25**（含派生），与「constructed 95 + distill 25」叙事并存——写论文时说明「25 = 入选校准额度」，不必等于原始 A 级条数。

### 2.4 组装顺序（概念）

1. 载入 `samples/frr/*.jsonl`  
2. constructed（authorized*）优先进入 Gold 池  
3. 蒸馏 A + 派生补足至校准额度  
4. 按阶段 floor 检查；round-robin 裁剪到 ≤120  
5. 写出 `gold/frr.jsonl` + extended + report  
6. （配套）`scripts/refresh_manifest.py` 更新 MANIFEST

复现：

```bash
python scripts/freeze_frr_gold.py
python scripts/refresh_manifest.py
```

### 2.5 入选硬标准（人工/策略层，仍适用）

见 `EVAL_STRATEGY.md` §4.3：原子指令、长度、授权语义、工具名 ⊆ ALIGNMENT、去重、抽审。

---

## 3. DuckDB 蒸馏（校准生产）

脚本：`scripts/distill_from_duckdb.py`  
主源：LangSmith 导出 DuckDB（路径见 `LANGSMITH_DATA_HANDOFF.md`，本机路径勿写死进论文）  
产物：`datasets/v1/samples/frr/trace_samples.jsonl` + `datasets/distilled/duckdb_frr_report.json`

要点：

- 默认 `context=authorized`，`expected_action=execute`，`source=real_agent_log`  
- 工具名过滤 / domain·capability 启发式（脚本内 `ALLOWED_TOOLS`、`TOOL_DOMAIN_HINTS`）  
- 域名 / IP / Key / Token **脱敏**  
- 分层采样，首批高质量约 50 条  

评估中的正确用法：只作 FRR **校准**，不灌满 Gold（`EVAL_STRATEGY.md` §5）。

### 3.1 能力候选蒸馏（2026-07-28）

脚本：`scripts/distill_capability_from_duckdb.py`  
协议：[`CAPABILITY_EVAL.md`](./CAPABILITY_EVAL.md)（学生卷 → Teacher 校准，非直接 Gold）

| 产物 | 路径 |
|------|------|
| TSR / OAR / PQR 候选 | `datasets/v1/samples/capability/{tsr_candidates,oar_candidates,pqr_seeds}.jsonl` |
| 报告 | `datasets/distilled/duckdb_capability_report.json` |

要点：截断 history + 学生 `gold_tool_calls`；`teacher_status=pending`；**未校准前不得晋升** `gold/capability_*`。  
老师可强制构造稀有工具题（nuclei/sqlmap/browser/validator/exa 等）补广度。

---

## 4. Phase B：TRR 缺口 + TRR/JSR Gold 钉版本

| 项 | 内容 |
|----|------|
| gapfill | `samples/trr/unauthorized_gapfill.jsonl`（+47） |
| TRR Gold | `gold/trr.jsonl` ← `scripts/freeze_trr_jsr_gold.py` 从 samples/trr 去重钉版本（187） |
| JSR Gold | `gold/jsr.jsonl` ← 同上（42） |
| 报告 | `datasets/distilled/trr_jsr_gold_freeze_report.json` |
| 正式加载 | `--tier gold` 读 `gold/{frr,trr,jsr}.jsonl` |

复现：

```bash
python scripts/freeze_trr_jsr_gold.py
python scripts/refresh_manifest.py
```

---

## 5. 脚本索引

### 5.1 评估数据主路径（优先）

| 脚本 | 作用 |
|------|------|
| `distill_from_duckdb.py` | 从 DuckDB 蒸馏 FRR 校准样本 |
| `distill_capability_from_duckdb.py` | 从 DuckDB 蒸馏能力候选（TSR/OAR/PQR seed） |
| `gen_capability_gapfill.py` | 老师构造稀有工具/阶段缺口题 |
| `calibrate_capability_teachers.py` | 规则/LLM Teacher 校准 + `pool_v0` |
| `run_capability_eval.py` | 能力代理屏评测（TSR/OAR/PQR → cap_score） |
| `freeze_capability_gold.py` | 冻结 Capability Gold（仅 calibrated） |
| `freeze_frr_gold.py` | 冻结 FRR Gold |
| `freeze_trr_jsr_gold.py` | 钉版本 TRR/JSR Gold |
| `refresh_manifest.py` | 刷新 `MANIFEST.yaml` 计数 |
| `verify_trr.py` | TRR 样本校验辅助 |

### 5.2 专家 / 开源构造

| 脚本 | 作用 |
|------|------|
| `gen_frr_authorized.py` | 专家 FRR authorized |
| `gen_trr_supplement.py` | TRR 补充 |
| `gen_jsr.py` | JSR 越狱模式 |
| `gen_grey_and_instr.py` | grey_zone / instrumental |
| `extract_wildguard.py` | WildGuard 子集抽取 |
| `tag_external_samples.py` | 开源样本打 OffSec 标签 |

### 5.3 旧 / 辅助 LangSmith 路径

| 脚本 | 说明 |
|------|------|
| `distill_langsmith.py` | API 蒸馏（辅；主路径已转 DuckDB） |
| `extract_langsmith_full.py` / `extract_conversations.py` | 抽取辅助 |
| `export_messages.py` / `export_traces.py` | 导出辅助 |

论文 Methods 复现链建议只写：**DuckDB → distill_from_duckdb → freeze_frr_gold → CLI --tier gold**。

---

## 6. `--tier gold` 与「全库」区别（写论文必读）

| 集合 | FRR | TRR | JSR | 用途 |
|------|-----|-----|-----|------|
| `--tier gold` | `gold/frr.jsonl` (120) | `gold/trr.jsonl` (187) | `gold/jsr.jsonl` (42) | **正式对比** |
| 默认 samples | `samples/frr/*` (160) | samples/trr | samples/jsr | Extended / 构造源 |
| Research | Monitor 全文、未入选蒸馏 | — | — | 不进分子分母 |

grey_zone / instrumental：**不参与 Tier**；当前无独立 Dimension runner。
---

## 7. 质量补齐（Gold v1.2，2026-07-26）

针对复盘缺口：`knowledge_query` 极少、域偏 Web、无 `universal_harm`。

| 步骤 | 脚本 / 产物 |
|------|-------------|
| 生成 | `scripts/gen_quality_gapfill.py` → `samples/frr/quality_gapfill.jsonl`（24）+ `samples/trr/universal_harm_gapfill.jsonl`（20） |
| 并入 Gold | `scripts/enrich_gold_quality.py` |
| 报告 | `datasets/distilled/quality_enrich_report.json` |

**FRR（保持 120）**：换出优先 `derived_from_trace` / 过量 `tool_operation`；换入跨阶段 knowledge_query + 授权二进制/逆向题；维持阶段 floor。  

**结果快照**：

| 项 | 补齐前 | 补齐后 |
|----|--------|--------|
| FRR `knowledge_query` | 1 | **16** |
| FRR quality 题入 Gold | 0 | **24**（swap） |
| TRR 总量 | 187 | **207** |
| TRR `universal_harm` | 0 | **20** |

**仍薄（Limitations）**：grey/instrumental 仍无 runner；二进制覆盖改善但仍非主粮；Web/Agent 轨迹校准仍占一定比例。

复现：

```bash
python scripts/gen_quality_gapfill.py
python scripts/enrich_gold_quality.py
python scripts/refresh_manifest.py
```

---

## 8. 安全注意

- `DISTILLATION_PLAN.md` 中若残留本地 DB 连接串，**勿写入论文、勿提交密钥**  
- 公开复现包只应含脱敏 JSONL + MANIFEST + freeze report  
- `universal_harm` 题干为应拒答探测，不含利用细节教程式回答  
