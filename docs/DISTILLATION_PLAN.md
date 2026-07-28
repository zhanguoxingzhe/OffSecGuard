# 数据集蒸馏方案 v1

> **评估优先**：正式评测口径与 Gold 配比见 [`EVAL_STRATEGY.md`](./EVAL_STRATEGY.md)。  
> 蒸馏仅服务 FRR **校准**（建议精筛 20–30 条入 Gold），不做评估主粮、不追求从 24 万 LLM 调用扩量。  
> 论文复现 / 实验过程：[`PAPER_METHODOLOGY.md`](./PAPER_METHODOLOGY.md)。  
> 冻结算法与脚本索引：[`DATASET_FREEZE.md`](./DATASET_FREEZE.md)。  
> 状态（2026-07-26）：首批 50 条已蒸馏；其中精筛入 Gold 校准 25 条（见 freeze report），其余 Extended/Research。  
> **安全**：下文若含本地 DB 连接示例，仅供内网运维；勿写入论文、勿提交密钥。

## 目标

从真实 Agent-LLM 交互数据蒸馏 OffSec Guard **校准用** FRR（authorized）样本。

## 权威主源（2026-07-26 起）

| 源 | 路径 / 说明 | 角色 |
|---|---|---|
| LangSmith DuckDB | `E:\wanzhen\scantist\github\langsmith\analytics\langsmith.duckdb` | **主源** |
| 蒸馏脚本 | `scripts/distill_from_duckdb.py` | 分批抽取 / 脱敏 / 分层采样 |
| 产物 | `datasets/v1/samples/frr/trace_samples.jsonl` | 首批高质量 50 条 |
| 报告 | `datasets/distilled/duckdb_frr_report.json` | 验收与溯源 meta |

详见 `docs/LANGSMITH_DATA_HANDOFF.md` 与 `docs/ALIGNMENT.md`。

## 辅助数据源（可选）

### agent_trace_steps（Engine DB，细粒度但常缺 chat roles）

| 字段 | 可蒸馏内容 |
|---|---|
| input (JSONB) | 发给 LLM 的完整消息上下文 — 含 system prompt + history + 当前指令 |
| output (JSONB) | 模型的完整响应 — content + tool_calls |
| stepType | THOUGHT / TOOL_CALL / TOOL_RESULT |
| finishReason | stop / tool_calls / length |
| modelName | 本条记录用的模型 |
| toolName | 工具名 → 推断 domain（nmap→recon，sqlmap→exploit） |
| sequenceIndex | 重建对话链顺序 |

### agent_executions

| 字段 | 可蒸馏内容 |
|---|---|
| systemPrompt | Agent 实际使用的 system prompt 原文 — 精确对齐 Engine 用语 |
| agentName | user_story / coordination / report |
| inputData / outputData | 高层输入输出上下文 |

### agent_jobs

| 字段 | 用途 |
|---|---|
| status | 筛选 COMPLETED 任务 |
| target | 目标信息（需脱敏） |
| runKind | initial / verification |
| runtimeTierLabel | AI 运行时类型 |

## 蒸馏策略

### FRR（authorized 样本）— 主要目标

1. 从 input JSONB 提取最后一条 user 消息作为 text
2. 从 input JSONB 提取前面消息作为 history（对话轨迹）
3. 根据 toolName 推断 domain
4. 根据 input 内容推断 capability
5. source = real_agent_log, context = authorized, expected_action = execute

### TRR（拒绝样本）— 辅助

1. 筛选 finish_reason=stop 且 output 含拒绝关键词的步骤
2. 用 RefusalDetector 对 output 做批量拒绝检测
3. 标记为 FRR 失败案例（模型拒绝了 Engine 合法指令）

### JSR — 主要自己构造

- 从拒绝边界找出模型犹豫的场景做参考

## 量级预估

| 来源 | 预估可蒸馏 FRR 样本 |
|---|---|
| PROD | 50-150 条 |
| DEV | 30-80 条 |

## DB 连接参数

DEV: postgresql://paistrike_dev:...@localhost:15432/paistrike_dev?sslmode=require
PROD: postgresql://dbadmin:...@127.0.0.1:25432/appdb?sslmode=require

## 执行步骤

1. 连接验证 — 确认两环境连通性
2. 统计摸底 — 查任务总量/trace总量/模型分布
3. 批量提取 — SQL 导出原始 JSON
4. 解析清洗 — 从 JSONB 提取 prompt/response/history
5. 分类打标 — 推断 domain/capability + 人工审核
6. 集成入库 — 合并到 datasets/v1/samples/frr/trace_samples.jsonl
