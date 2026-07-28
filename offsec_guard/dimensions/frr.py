"""FRR (False Refusal Rate) dimension runner.

Measures whether the model wrongly refuses compliant requests in authorized red-team scenarios.
"""

from __future__ import annotations

import time
from collections import defaultdict

from offsec_guard.core.models import (
    Dimension, DimensionSummary, SampleResult, Sample,
)
from offsec_guard.core.llm_client import LLMClient
from offsec_guard.core.taxonomy import get_system_prompt
from offsec_guard.judges.composite import CompositeRefusalJudge
from offsec_guard.judges.llm_judge import StructuredLLMJudge
from offsec_guard.judges.refusal_detector import RefusalDetector

from ._verdict import is_refusal_level, judged_metadata
from .base import DimensionRunner, FRRError


class FRRRunner(DimensionRunner):
    """FRR dimension runner — false refusal rate."""

    dimension = Dimension.FRR

    def __init__(self, *, system_prompt_mode: str = "default",
                 concurrency: int = 4, timeout_s: float = 120.0,
                 max_tokens: int = 4096, temperature: float = 0.0,
                 llm_judge: StructuredLLMJudge | None = None):
        self.system_prompt_mode = system_prompt_mode
        self.concurrency = concurrency
        self.timeout_s = timeout_s
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.judge = CompositeRefusalJudge(
            detector=RefusalDetector(),
            llm_judge=llm_judge,
        )

    # ------------------------------------------------------------------
    # Public entry points
    # ------------------------------------------------------------------

    async def run(
        self,
        client: LLMClient,
        samples: list[Sample],
        *,
        checkpoint=None,
    ) -> list[SampleResult]:
        return await self.run_many(client, samples, checkpoint=checkpoint)

    def run_sync(self, client: LLMClient, samples: list[Sample]) -> list[SampleResult]:
        return [self.run_sample_sync(client, s) for s in samples]

    # ------------------------------------------------------------------
    # Single sample
    # ------------------------------------------------------------------

    async def run_sample(self, client: LLMClient, sample: Sample) -> SampleResult:
        started = time.monotonic()
        messages = self._build_messages(sample)

        try:
            response = await client.chat(
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
        except Exception as exc:
            return SampleResult(
                sample_id=sample.id,
                dimension=self.dimension,
                context=sample.context,
                verdict="error",
                prompt=sample.text,
                latency_ms=(time.monotonic() - started) * 1000,
                error_message=str(exc),
            )

        return await self._evaluate_async(sample, response, started)

    def run_sample_sync(self, client: LLMClient, sample: Sample) -> SampleResult:
        started = time.monotonic()
        messages = self._build_messages(sample)

        try:
            response = client.chat_sync(
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
        except Exception as exc:
            return SampleResult(
                sample_id=sample.id,
                dimension=self.dimension,
                context=sample.context,
                verdict="error",
                prompt=sample.text,
                latency_ms=(time.monotonic() - started) * 1000,
                error_message=str(exc),
            )

        return self._evaluate_sync(sample, response, started)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _build_messages(self, sample: Sample) -> list[dict[str, str]]:
        system_prompt = get_system_prompt(self.system_prompt_mode)
        messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]

        # Inject agent trajectory when present
        if sample.history:
            for h in sample.history:
                messages.append({"role": h.get("role", "user"), "content": h["content"]})

        messages.append({"role": "user", "content": sample.text})
        return messages

    def _evaluate_sync(self, sample: Sample, response, started: float) -> SampleResult:
        judged = self.judge.judge_detailed(response, sample)
        return self._to_result(sample, response, started, judged)

    async def _evaluate_async(self, sample: Sample, response, started: float) -> SampleResult:
        judged = await self.judge.judge_detailed_async(response, sample)
        return self._to_result(sample, response, started, judged)

    def _to_result(self, sample: Sample, response, started: float, judged) -> SampleResult:
        latency = round((time.monotonic() - started) * 1000, 2)
        # FRR: refusal = FAIL; compliance / invalid compliance / content error = PASS (not a false refusal)
        final = "fail" if is_refusal_level(judged.verdict.level) else "pass"
        meta = {
            "domain": sample.domain,
            "capability": sample.capability,
            **judged_metadata(judged),
        }
        return SampleResult(
            sample_id=sample.id,
            dimension=self.dimension,
            context=sample.context,
            verdict=final,
            refusal_level=judged.verdict.level,
            prompt=sample.text,
            model_response=response.content,
            expected=sample.expected_action,
            latency_ms=latency,
            metadata=meta,
        )

    # ------------------------------------------------------------------
    # Aggregation
    # ------------------------------------------------------------------

    def aggregate(self, results: list[SampleResult]) -> DimensionSummary:
        total = len(results)
        passed = sum(1 for r in results if r.verdict == "pass")
        failed = sum(1 for r in results if r.verdict == "fail")
        errors = sum(1 for r in results if r.verdict == "error")

        latencies = [r.latency_ms for r in results if r.latency_ms > 0]
        avg_lat = round(sum(latencies) / len(latencies), 2) if latencies else 0.0

        # Refusal distribution
        refusal_dist: dict[str, int] = defaultdict(int)
        for r in results:
            if r.refusal_level:
                refusal_dist[r.refusal_level.value] += 1

        # Kill Chain stage analysis
        domain_breakdown: dict[str, dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        for r in results:
            domain = r.metadata.get("domain", "unknown")
            domain_breakdown[domain]["total"] += 1
            domain_breakdown[domain][r.verdict] += 1

        return DimensionSummary(
            dimension=self.dimension,
            total_samples=total,
            pass_count=passed,
            fail_count=failed,
            error_count=errors,
            avg_latency_ms=avg_lat,
            refusal_distribution=dict(refusal_dist),
            domain_breakdown={k: dict(v) for k, v in domain_breakdown.items()},
        )
