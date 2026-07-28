# OffSec Guard — 数据集建设计划 v2

> 执行优先级与 Gold 冻结结果见 [`EVAL_STRATEGY.md`](./EVAL_STRATEGY.md)；  
> 论文方法与实验数字见 [`PAPER_METHODOLOGY.md`](./PAPER_METHODOLOGY.md)。  
> 最近核对：2026-07-26 — **Gold v1.2**：FRR=120（kq=16）；TRR=207（含 universal_harm=20）；JSR=42；正式对比 `--tier gold`。

## 范围定义

评估范围涵盖**网络和应用安全**全领域，不仅限于渗透测试：

- 渗透测试（Web、网络、内网、云）
- 二进制漏洞利用（缓冲区溢出、ROP、堆利用、格式化字符串）
- 逆向工程（反汇编、脱壳、patch 分析）
- Exploit 开发（PoC 编写、shellcode 生成、绕过缓解措施）
- 恶意软件分析（沙箱逃逸、C2 通信、免杀）
- 漏洞研究（fuzzing、代码审计、diff 分析）

## 评估维度与样本规划

| 维度 | Context | 来源 | 目标量 | 说明 |
|---|---|---|---|---|
| FRR（假拒答率） | authorized | **自建** | 80-120 | 核心差异化资产，8 个 Kill Chain 阶段全覆盖 |
| TRR（真拒答率） | unauthorized | 开源吸收 + 自建 | 140-160 | HarmBench + WildGuard cybercrime 子集 + 二进制/漏洞研究补充 |
| JSR（脱狱安全） | unauthorized | **自建** | 40-50 | 角色劫持、授权伪造、分步诱导等 6-8 种攻击模式 |
| grey_zone | grey_zone | **自建** | 20-30 | 模糊授权、半合规情景 |
| instrumental | instrumental | **自建** | 15-20 | 纯工具操作旁路测试 |
| **合计** | | | **300-380** | |

## 数据来源

### 开源吸收

| 来源 | 子集 | 预测量 | 映射目标 |
|---|---|---|---|
| HarmBench | cybercrime_intrusion | ~80-100 条 | TRR unauthorized |
| WildGuard | cyberattacks | ~30-50 条 | TRR unauthorized |

开源样本需要补充 OffSec Guard 标签：`context`、`domain`（Kill Chain 阶段）、`capability`（操作类型）。

### 自建

| 类别 | 覆盖要点 |
|---|---|
| FRR | 8 阶段 × 3 capability ÷ difficulty，带 history Agent 轨迹 |
| TRR 补充 | 二进制 exploit、逆向、漏洞研究等开源覆盖不到的边界 |
| JSR | 角色扮演劫持、授权伪造、学术幌子、分步诱导、prompt 注入 |
| grey_zone | 模糊授权语境、半合规场景 |
| instrumental | 命令执行、文件读写、网络操作等工具层旁路 |

## Kill Chain 阶段覆盖目标

| 阶段 | FRR 目标 | TRR 目标 |
|---|---|---|
| reconnaissance | 10-15 | 15-20 |
| weaponization | 8-10 | 15-20 |
| delivery | 8-10 | 10-15 |
| exploitation | 15-20 | 25-30 |
| installation | 8-10 | 10-15 |
| command_control | 8-10 | 10-15 |
| post_exploitation | 15-20 | 25-30 |
| exfiltration | 8-10 | 10-15 |

## 执行计划

### 第一轮：吸收开源数据

1. 下载 HarmBench 全集，筛 cybercrime_intrusion 子集
2. 下载 WildGuardMix，筛 cyberattacks 子集
3. 转换格式 + 打 OffSec Guard 标签

### 第二轮：自建核心资产

4. FRR authorized 样本（8 阶段全覆盖）
5. TRR 补充（二进制/漏洞研究边界）
6. JSR 脱狱样本
7. grey_zone + instrumental

### 第三轮：集成与验证

8. 全量格式校验 + MANIFEST v2 + 数据集打包
9. PaperGuru + GPT-5.4 全维度基准评测

## 标签格式

```jsonl
{"id": "trr-unauth-exploit-001", "text": "...", "context": "unauthorized", "domain": "exploitation", "capability": "code_generation", "expected_action": "refuse", "difficulty": "medium", "source": "harmbench", "tags": ["cve", "exploit"], "history": []}
```

`source` 字段区分数据来源：`harmbench`、`wildguard`、`expert_constructed`、`cve_bench_failure`、`real_agent_log`。
