"""DimensionRunner 抽象基类."""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from offsec_guard.core.models import Dimension, DimensionSummary, SampleResult, Sample
from offsec_guard.core.llm_client import LLMClient

if TYPE_CHECKING:
    from offsec_guard.pipeline.checkpoint import SampleCheckpoint


class FRRError(Exception):
    """FRR 评估过程中的异常."""
    pass


class DimensionRunner(ABC):
    """维度执行器基类."""

    dimension: Dimension
    concurrency: int = 4

    @abstractmethod
    async def run_sample(self, client: LLMClient, sample: Sample) -> SampleResult:
        """执行单个样本."""
        ...

    def run_sample_sync(self, client: LLMClient, sample: Sample) -> SampleResult:
        """同步版本."""
        raise NotImplementedError("sync run_sample not implemented")

    @abstractmethod
    def aggregate(self, results: list[SampleResult]) -> DimensionSummary:
        """聚合结果."""
        ...

    async def run_many(
        self,
        client: LLMClient,
        samples: list[Sample],
        *,
        checkpoint: "SampleCheckpoint | None" = None,
    ) -> list[SampleResult]:
        """并发跑样本；有 checkpoint 时跳过已完成题并逐条追加."""
        reused = checkpoint.reused_for(s.id for s in samples) if checkpoint else {}
        pending = [s for s in samples if s.id not in reused]
        total = len(samples)
        done_base = len(reused)
        print(
            f"  [{self.dimension.value}] start: reuse={done_base} "
            f"pending={len(pending)} / {total}",
            flush=True,
        )
        if not pending:
            return [reused[s.id] for s in samples if s.id in reused]

        semaphore = asyncio.Semaphore(self.concurrency)
        progress_lock = asyncio.Lock()
        finished = 0

        def _log(msg: str) -> None:
            # ASCII-only：避免 Windows 管道/控制台编码把进度行吞掉
            print(msg, flush=True)

        async def bounded(sample: Sample) -> SampleResult:
            nonlocal finished
            async with semaphore:
                _log(f"  [{self.dimension.value}] >> {sample.id}")
                result = await self.run_sample(client, sample)
                if checkpoint is not None:
                    await checkpoint.append(result)
                async with progress_lock:
                    finished += 1
                    n = done_base + finished
                    lat = f"{result.latency_ms:.0f}ms" if result.latency_ms else "-"
                    err = f" err={result.error_message[:80]}" if result.verdict == "error" and result.error_message else ""
                    _log(
                        f"  [{self.dimension.value}] {n}/{total} "
                        f"{result.sample_id} -> {result.verdict} ({lat}){err}"
                    )
                return result

        fresh = await asyncio.gather(*[bounded(s) for s in pending]) if pending else []
        by_id = {**reused, **{r.sample_id: r for r in fresh}}
        # 保持输入顺序
        return [by_id[s.id] for s in samples if s.id in by_id]