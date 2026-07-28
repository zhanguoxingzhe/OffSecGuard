"""Pipeline 执行器 — 编排维度运行 + Gate 判定."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from offsec_guard.core.llm_client import LLMClient
from offsec_guard.core.models import (
    Dimension, Sample, EvalReport, SampleResult, DimensionSummary,
    ModelIdentity, classify_tier,
)
from offsec_guard.core.config import EvalConfig
from offsec_guard.dimensions.frr import FRRRunner
from offsec_guard.dimensions.trr import TRRRunner, JSRRunner
from offsec_guard.judges.llm_judge import StructuredLLMJudge
from .checkpoint import SampleCheckpoint, checkpoint_path
from .plan import RunPlan


@dataclass
class ExecutionContext:
    """评估执行上下文."""
    config: EvalConfig
    plan: RunPlan
    client: LLMClient
    model: ModelIdentity
    judge_client: LLMClient | None = None


class PipelineExecutor:
    """Pipeline 执行编排器."""

    def __init__(self, ctx: ExecutionContext):
        self.ctx = ctx

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def _open_checkpoint(self) -> SampleCheckpoint | None:
        cfg = self.ctx.config
        path = cfg.checkpoint_path or str(checkpoint_path(cfg.output_dir))
        # 始终写盘；resume=False 时不加载旧进度（调用方应已清空文件）
        return SampleCheckpoint(
            path,
            retry_errors=cfg.retry_checkpoint_errors,
            load=cfg.resume,
        )

    async def run(self, samples: list[Sample]) -> EvalReport:
        """执行完整评估流水线."""
        dim_results: dict[str, DimensionSummary] = {}
        dim_samples: dict[str, list[SampleResult]] = {}
        checkpoint = self._open_checkpoint()
        if checkpoint is not None:
            n_cached = len(checkpoint.cached())
            if n_cached:
                print(
                    f"Checkpoint: {checkpoint.path} "
                    f"(cached usable={n_cached}, retry_errors={checkpoint.retry_errors})"
                )

        # 按维度分发样本
        grouped = self._group_by_dimension(samples)

        for dim in self.ctx.plan.dimensions:
            runner = self._get_runner(dim)
            hsamples = grouped.get(dim, [])
            if not hsamples:
                continue

            sample_rows = await runner.run(
                self.ctx.client, hsamples, checkpoint=checkpoint
            )
            # runners 返回 list[SampleResult]；兼容旧版直接返回 DimensionSummary
            if isinstance(sample_rows, DimensionSummary):
                dim_results[dim.value] = sample_rows
            else:
                dim_samples[dim.value] = list(sample_rows)
                dim_results[dim.value] = runner.aggregate(sample_rows)

        # 综合评分 — 与 classify_tier / scorecard 对齐：
        #   frr = fail_rate（假拒答率，越低越好）
        #   trr = pass_rate（应拒答率，越高越好）
        #   jsr = fail_rate（越狱成功率近似，越低越好）
        scores: dict[str, float] = {}
        for dim in self.ctx.plan.tier_dimensions:
            key = dim.value
            if key not in dim_results:
                continue
            summary = dim_results[key]
            if dim == Dimension.FRR:
                scores[key] = summary.fail_rate
            elif dim == Dimension.JSR:
                scores[key] = summary.fail_rate
            else:
                scores[key] = summary.pass_rate

        tier = classify_tier(scores)
        # 压力包等非认证跑次：仍计算分数，但不宣称 Tier
        if not self.ctx.config.claim_tier:
            from offsec_guard.core.models import Tier

            tier = Tier.UNRATED

        # 加权综合分 (0-100)：FRR/JSR 用 (100-rate)，TRR 用 rate
        total = 0.0
        ws = self.ctx.plan.weights
        for key in self.ctx.plan.tier_dimensions:
            w = ws.get(key.value, 0)
            s = scores.get(key.value, 0.0)
            total += w * (100 - s if key in (Dimension.FRR, Dimension.JSR) else s)
        total = round(total, 2)

        return EvalReport(
            model=self.ctx.model,
            eval_id=self.ctx.config.eval_id,
            total_score=total,
            tier=tier,
            dimensions={k: v for k, v in dim_results.items()},
            sample_results=dim_samples,
            weights=ws,
            config_snapshot={
                "framework_version": "0.1.0",
                "preset": "",  # populated by cli
                "eval_bundle": self.ctx.config.eval_bundle or "",
                "claim_tier": self.ctx.config.claim_tier,
                "prompt_profiles": {
                    "frr": self.ctx.config.prompt_profile_frr,
                    "trr": self.ctx.config.prompt_profile_trr,
                    "jsr": self.ctx.config.prompt_profile_jsr,
                },
                "judge_enabled": self.ctx.config.judge_enabled,
                "judge_model": (
                    f"{self.ctx.config.judge_provider}/{self.ctx.config.judge_model_id}"
                    if self.ctx.config.judge_enabled
                    else ""
                ),
            },
            notes=self.ctx.config.notes,
        )

    def run_sync(self, samples: list[Sample]) -> EvalReport:
        """同步入口 — 内部使用 asyncio 并发执行."""
        return asyncio.run(self.run(samples))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_llm_judge(self) -> StructuredLLMJudge | None:
        if not self.ctx.config.judge_enabled or self.ctx.judge_client is None:
            return None
        return StructuredLLMJudge(
            self.ctx.judge_client,
            temperature=self.ctx.config.judge_temperature,
            max_tokens=self.ctx.config.judge_max_tokens,
        )

    def _get_runner(self, dim: Dimension):
        mode = self.ctx.config.taxonomy_mode_for(dim.value)
        common = dict(
            concurrency=self.ctx.config.concurrency,
            timeout_s=self.ctx.config.timeout_s,
            max_tokens=self.ctx.config.max_tokens,
            temperature=self.ctx.config.temperature,
            llm_judge=self._build_llm_judge(),
            system_prompt_mode=mode,
        )
        if dim == Dimension.FRR:
            return FRRRunner(**common)
        if dim == Dimension.TRR:
            return TRRRunner(**common)
        if dim == Dimension.JSR:
            return JSRRunner(**common)
        raise NotImplementedError(f"Runner for {dim} not yet implemented")

    @staticmethod
    def _group_by_dimension(samples: list[Sample]) -> dict[Dimension, list[Sample]]:
        """按 expected_action / id 前缀将样本路由到对应维度."""
        groups: dict[Dimension, list[Sample]] = {}
        for s in samples:
            if s.expected_action == "execute":
                dim = Dimension.FRR
            elif s.id.startswith("jsr-") or "jailbreak" in (s.tags or []) or any(
                t in (s.tags or [])
                for t in ("role-hijack", "dan", "developer-mode", "prompt-injection")
            ):
                dim = Dimension.JSR
            else:
                dim = Dimension.TRR
            groups.setdefault(dim, []).append(s)
        return groups
