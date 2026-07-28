# OffSec Guard 评估数据策略（Eval-First）

> 制定日期：2026-07-26 · 最近更新：2026-07-28  
> 前提：v1 已有 387 条；LangSmith DuckDB 可挖数千候选，但评估目标 ≠ 最大化蒸馏量。  
> 对齐：`ALIGNMENT.md` · 配额：`DATASET_PLAN.md` · 数据源：`LANGSMITH_DATA_HANDOFF.md`  
> **产品决策（主目标）**：[`PRODUCT_DECISIONS.md`](./PRODUCT_DECISIONS.md)  
> **论文方法 / 实验过程**：[`PAPER_METHODOLOGY.md`](./PAPER_METHODOLOGY.md)  
> **能力第二轴**：[`CAPABILITY_EVAL.md`](./CAPABILITY_EVAL.md)（TSR/OAR/PQR；与本文护栏 Gold 并行）

---

## 1. 一句话策略

**用专家构造保证 Kill Chain / 能力面覆盖与可比性；用少量精筛真实轨迹校准「像不像生产 Agent」；用开源集撑 TRR；蒸馏不做主粮。**

护栏评估要回答的是：在 **PAIStrike 授权前缀** 下，模型的 FRR / TRR / JSR 是否达标——不是「我们从 LangSmith 抽了多少条」。  
**选型**另需能力代理屏（见 `CAPABILITY_EVAL.md`）：护栏过线 ∩ `cap_score`；结果型靶场不进本策略日常路径。

---

## 2. 目标优先级

| 优先级 | 目标 | 成功标准 |
|:---:|------|----------|
| P0 | 评测口径对齐 Engine | FRR=`product`（PAIStrike）；多场景用 `--eval-bundle`（见 `EVAL_BUNDLES.md`）；`content_filter`→HARD_REFUSAL |
| P0 | 维度配额可用且可复现 | 落在 DATASET_PLAN 区间；MANIFEST 与打包一致 |
| P1 | FRR 覆盖 8 阶段 × 主要 capability | 每阶段达到 FRR 下限；题干原子、可判拒答 |
| P1 | 出第一版基准分 | PaperGuru + GPT-5.4（或等价）全维度报告 |
| P2 | 真实轨迹校准 | FRR 中 `real_agent_log` 占 **15–30%**，且经人工过审 |
| P3 | 扩大蒸馏语料 | 仅在评估稳定后，另建 research/SFT 池，不进 gold |

---

## 3. 现状判断（基于现库）

| 维度 | 目标 | 现状 | 判断 |
|------|------|------|------|
| 合计 | 300–380 | **387** | 量已够 |
| FRR | 80–120 | **160** | 偏多；应用 **gold 精简**，不是继续加 |
| TRR | 140–160 | **140** | 触线下限，二进制/逆向边界可小补 |
| JSR / grey / instrumental | 达标区间内 | 42 / 25 / 20 | 维持，抽检即可 |
| LangSmith | — | ~181 scan 线程；Monitor 去重数千 | **够做校准，不够替代专家集** |

结论：评估侧进入 **「冻结 gold → 补缺口 → 跑基准」**，而不是「继续从 24 万 LLM 调用里扩量」。

---

## 4. 推荐集合结构（Gold）

### 4.1 分层

| 层 | 用途 | 规模建议 | 变更频率 |
|----|------|----------|----------|
| **Gold** | 发版 / 论文 / 模型对比唯一口径 | 总量 **320–360**；FRR **100–120** | 严格变更，打版本号 |
| **Extended** | 回归加严、错误分析 | Gold 之外的合格样本（含未入选蒸馏） | 可增，不影响 Gold 分数解读 |
| **Research pool** | 蒸馏原始候选、Monitor 全文等 | 可达数千 | 不进正式 FRR 分子分母 |

### 4.2 FRR Gold 配比（核心）

| 来源 | 建议条数 | 角色 |
|------|----------|------|
| `expert_constructed`（+少量 cve_bench） | **80–95** | 主干：阶段均衡、题干干净、history 可控 |
| `real_agent_log`（精筛） | **20–30** | 校准：证明「生产授权任务」上也不乱拒 |
| 合计 FRR Gold | **100–120** | 落回 DATASET_PLAN，避免 160 稀释阶段配额可读性 |

当前 50 条蒸馏：**不可整包进 Gold**。多数是 Monitor 建议 / Engagement Plan，适合 research，不适合直接当拒答判定题。

### 4.3 蒸馏入 Gold 的硬标准（必须同时满足）

1. `text` 是 **一条可执行的用户指令**（像人下的任务），不是 Monitor 套话、不是整包 Plan。  
2. 长度建议 **80–800 字**（脱敏后）；过长 brief 须改写成单目标指令后再入库。  
3. 含授权语义，或 `history` 含 sanctioned / in-scope / pre-authorized。  
4. 对应步骤工具名 ⊆ `ALIGNMENT.md` §3。  
5. 同 host + 同意图去重；跨线程模板重复只留 1 条。  
6. 人工抽审通过（每条 30 秒能判断 expected=execute 是否合理）。

不满足的 → 留在 Extended / Research，**不算 FRR Gold**。

---

## 5. LangSmith 在评估中的正确用法

| 用途 | 做不做 | 说明 |
|------|--------|------|
| FRR 校准样本（精筛 20–30） | **做** | 从 module_task / 清晰 human 指令抽，优先非 Monitor |
| `content_filter` 失败案例库 | **做** | 服务错误分析与模型选型，不计入 TRR |
| 用数千 Monitor 灌满 FRR | **不做** | 抬高样本相关、压低题干清晰度，伤害可比性 |
| 追平 UI 1578 runs / 全量 LLM | **不做** | 口径不是任务，也不是评估题 |
| 补 TRR/JSR | **基本不做** | 生产轨迹默认 authorized；JSR 必须自建 |

`paitrike` 大杂烩线程：评估 Gold **默认排除**；仅 research 需要时再拆。

---

## 6. 缺口补齐策略（只补评估缺口）

按 DATASET_PLAN 的 FRR/TRR 阶段下限，优先 **expert_constructed**，不靠蒸馏碰运气：

| 缺口类型 | 策略 |
|----------|------|
| delivery / installation / exfiltration / C2 偏薄 | 专家补 5–10 条/阶段（若 Gold 精简后仍低于下限） |
| 二进制 / 逆向 / 恶意软件（范围定义内） | TRR + 少量 FRR 专家题；LangSmith Web 渗透轨迹覆盖不到 |
| TRR 触底 | 保持 140；若基准显示某域过易，再补 10–20 难例 |
| 蒸馏 50 条质量 | 人工分级：A 入 Gold候选 / B 改写后入 / C 仅 research |

---

## 7. 执行路线（评估闭环）

### Phase A — 冻结 Gold（1–2 天） — ✅ 2026-07-26 完成

1. ✅ `datasets/v1/gold/frr.jsonl`：**120** 条（constructed 95 + 轨迹校准 25）  
2. ✅ 蒸馏原文分级 A/B/C；Monitor/Plan 派生原子指令入校准集  
3. ✅ Extended：`gold/frr_distill_extended.jsonl`；报告：`datasets/distilled/frr_gold_freeze_report.json`  
4. ✅ CLI：`--tier gold`；脚本：`scripts/freeze_frr_gold.py` 可复现  
5. 对齐清单保持全绿（抽检即可）

### Phase B — 缺口微补（按需，≤1 天） — ✅ 2026-07-26 完成

5. ✅ FRR Gold 8 阶段均已达下限（无需再补）。  
6. ✅ TRR 缺口补齐：`samples/trr/unauthorized_gapfill.jsonl`（+47，覆盖 recon/delivery/install/C2/post/exfil）。  
7. ✅ 实现 `TRRRunner` / `JSRRunner`（`assistant` system prompt，不用 PAIStrike 授权前缀）。  
8. 不新增批量蒸馏。

### Phase C — 基准评测（1–2 天） — 🔄 部分完成（2026-07-26）

9. ✅ 固定：FRR = PAIStrike + `--tier gold`；TRR/JSR = `assistant` prompt。  
10. ✅ 规则判定缺陷修复（弯引号漏检）后，跑通 GPT-5.4 / PaperGuru 全维度（规则-only）。  
11. ✅ RefusalDetector **v3** + 结构化 LLM Judge（`--judge`）。  
12. ✅ Tier FRR 语义修复；`sample_results` 落盘；TRR/JSR Gold 钉版本。  
13. ✅ **Gold v1.2 质量补齐**：FRR knowledge_query 1→16；TRR +20 `universal_harm`；换入授权二进制/逆向题。  
14. ⏳ **待做**：按 Gold v1.2（369）+ PaperGuru 判官复跑两模型；消融；分 domain 表。  
15. 数字、目录、故事线 → 见 [`PAPER_METHODOLOGY.md`](./PAPER_METHODOLOGY.md) §5；质量细节 → `DATASET_FREEZE.md` §7。
```bash
# 正式对比（推荐：Gold + 固定共享 Judge）
python cli.py run --model openrouter/openai/gpt-5.4 \
  --dims frr,trr,jsr --tier gold --judge \
  --config configs/presets/gold_frr_trr_jsr.yaml
  # 默认判官 paperguru/guru-pro-1.2（可用 --judge-model 覆盖）

# 消融：仅规则
python cli.py run --model openrouter/openai/gpt-5.4 \
  --dims frr,trr,jsr --tier gold --no-judge
```

规则-only 快照（弯引号修复后，**非正式终稿**）：

| Metric | Target | GPT-5.4 | PaperGuru 1.2 |
|--------|--------|---------|---------------|
| FRR fail | &lt;5% | 51.7% | 6.7%† |
| TRR refuse | &gt;90% | 98.9% | 74.7% |
| JSR jailbreak | &lt;15% | 4.8% | 54.8% |

† 含部分 API error；终稿以 `--judge` 复跑为准。

### Phase D — 迭代规则

14. 模型对比只报 **Gold** 分数，并写明判官型号与 `judge_enabled`。  
15. 蒸馏扩量只进 Research；想进 Gold 必须走 §4.3 + 人工审核 + 版本 bump。  
16. 每次实验后更新 `PAPER_METHODOLOGY.md` §5 / §7。

---

## 8. 明确不做的事

- 不为「用上 24 万 LLM 调用」而扩大 FRR Gold。  
- 不把 Monitor/Plan 原文批量当 FRR 题。  
- 不用 LangSmith 替代 JSR/grey/instrumental 自建。  
- 不在评估未冻结前并行大改抽题脚本冲 1000 条入库。

---

## 9. 成功指标

- Gold 集：总量与 FRR 回到计划区间，8 阶段均 ≥ 下限。  
- 同一模型两次跑 Gold，FRR 波动在约定噪声内（如 ±1–2pp）。  
- 真实轨迹子集 FRR 与专家子集趋势同向（校准有效）。  
- 发版报告只引用 Gold + ALIGNMENT 口径。

---

## 10. 与旧文档关系

| 文档 | 关系 |
|------|------|
| `DATASET_PLAN.md` | 配额与维度定义仍有效；执行顺序改为本策略的 A→C |
| `DISTILLATION_PLAN.md` | 降级为 **校准样本生产** 说明；主路径服从本策略 |
| `ALIGNMENT.md` | 评测注入与拒答定义，本策略不覆盖 |
| `LANGSMITH_DATA_HANDOFF.md` | 数据源说明书；抽多少由本策略约束 |
| `PAPER_METHODOLOGY.md` | **论文**：方法、判定器、实验协议、结果日志、局限 |
| `JUDGE_DESIGN.md` | 两阶段判定完整设计 |
| `SCORING.md` | 计分 / Tier / 权重 / `cap_score` 指针 |
| `CAPABILITY_EVAL.md` | 能力代理屏与造题协议（选型第二轴） |
| `CLI_REFERENCE.md` | CLI 实现口径 |
| `DATASET_FREEZE.md` | Gold 冻结算法与脚本索引 |
| `docs/README.md` | 文档总索引 |
