"""逐条 checkpoint 续跑单测."""

from __future__ import annotations

import asyncio
from pathlib import Path

from offsec_guard.core.models import Dimension, Sample, SampleResult
from offsec_guard.dimensions.base import DimensionRunner
from offsec_guard.pipeline.checkpoint import (
    SampleCheckpoint,
    deserialize_sample_result,
    fingerprint,
    serialize_sample_result,
)


def _sr(sid: str, verdict: str = "pass") -> SampleResult:
    return SampleResult(
        sample_id=sid,
        dimension=Dimension.FRR,
        context="authorized",
        verdict=verdict,  # type: ignore[arg-type]
        prompt="p",
        model_response="r",
    )


def test_serialize_roundtrip(tmp_path: Path):
    sr = _sr("frr-1", "fail")
    raw = serialize_sample_result(sr)
    back = deserialize_sample_result(raw)
    assert back.sample_id == "frr-1"
    assert back.verdict == "fail"
    assert back.dimension == Dimension.FRR


def test_checkpoint_append_and_reuse(tmp_path: Path):
    path = tmp_path / "checkpoint.jsonl"

    async def _run():
        ck = SampleCheckpoint(path, retry_errors=True, load=False)
        await ck.append(_sr("a", "pass"))
        await ck.append(_sr("b", "error"))
        return ck

    asyncio.run(_run())

    ck2 = SampleCheckpoint(path, retry_errors=True, load=True)
    reused = ck2.reused_for(["a", "b", "c"])
    assert set(reused) == {"a"}  # error 默认重试，不计入 reuse


def test_fingerprint_stable():
    a = {
        "model": "openrouter/x",
        "eval_bundle": "stress_redteam",
        "prompt_profiles": {"frr": "product", "trr": "ceiling", "jsr": "ceiling"},
        "judge_enabled": True,
        "judge_model": "paperguru/guru-pro-1.2",
        "tier": "gold",
        "eval_id": "eval-ignore",
    }
    b = dict(a)
    b["eval_id"] = "eval-other"
    assert fingerprint(a) == fingerprint(b)


class _FakeRunner(DimensionRunner):
    dimension = Dimension.FRR
    concurrency = 2

    def __init__(self):
        self.calls: list[str] = []

    async def run_sample(self, client, sample: Sample) -> SampleResult:
        self.calls.append(sample.id)
        return _sr(sample.id, "pass")

    def aggregate(self, results):
        raise NotImplementedError


def test_run_many_skips_cached(tmp_path: Path):
    path = tmp_path / "checkpoint.jsonl"

    async def seed():
        ck = SampleCheckpoint(path, load=False)
        await ck.append(_sr("s1", "pass"))
        return ck

    asyncio.run(seed())

    samples = [
        Sample(
            id="s1",
            text="t1",
            context="authorized",
            domain="reconnaissance",
            capability="knowledge_query",
            expected_action="execute",
        ),
        Sample(
            id="s2",
            text="t2",
            context="authorized",
            domain="reconnaissance",
            capability="knowledge_query",
            expected_action="execute",
        ),
    ]
    runner = _FakeRunner()

    async def go():
        ck = SampleCheckpoint(path, retry_errors=True, load=True)
        return await runner.run_many(None, samples, checkpoint=ck)  # type: ignore[arg-type]

    rows = asyncio.run(go())
    assert [r.sample_id for r in rows] == ["s1", "s2"]
    assert runner.calls == ["s2"]
