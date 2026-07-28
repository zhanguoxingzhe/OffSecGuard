"""Per-sample checkpoint (JSONL) — resume by sample_id after restart.

Layout (relative to --output-dir):
  run_meta.json      — eval_id / config fingerprint
  checkpoint.jsonl   — one SampleResult line appended per finished sample
"""

from __future__ import annotations

import asyncio
import json
import os
from dataclasses import asdict, fields
from pathlib import Path
from typing import Any, Iterable

from offsec_guard.core.models import Dimension, RefusalLevel, SampleResult

META_NAME = "run_meta.json"
CHECKPOINT_NAME = "checkpoint.jsonl"


def serialize_sample_result(sr: SampleResult) -> dict[str, Any]:
    d = asdict(sr)
    d["dimension"] = sr.dimension.value
    if sr.refusal_level is not None:
        d["refusal_level"] = sr.refusal_level.value
    return d


def deserialize_sample_result(raw: dict[str, Any]) -> SampleResult:
    data = dict(raw)
    dim = data.get("dimension", "frr")
    data["dimension"] = dim if isinstance(dim, Dimension) else Dimension(dim)
    rl = data.get("refusal_level")
    if rl in (None, ""):
        data["refusal_level"] = None
    elif isinstance(rl, RefusalLevel):
        data["refusal_level"] = rl
    else:
        data["refusal_level"] = RefusalLevel(rl)
    allowed = {f.name for f in fields(SampleResult)}
    return SampleResult(**{k: v for k, v in data.items() if k in allowed})


def fingerprint(meta: dict[str, Any]) -> dict[str, Any]:
    """Key fields used on resume to verify config fingerprint match."""
    keys = (
        "model",
        "eval_bundle",
        "prompt_profiles",
        "judge_enabled",
        "judge_model",
        "tier",
    )
    return {k: meta.get(k) for k in keys}


class SampleCheckpoint:
    """Asyncio-safe per-sample result store."""

    def __init__(
        self,
        path: Path,
        *,
        retry_errors: bool = True,
        load: bool = True,
    ):
        self.path = Path(path)
        self.retry_errors = retry_errors
        self._lock = asyncio.Lock()
        self._by_id: dict[str, SampleResult] = {}
        if load and self.path.exists():
            self._load()

    def _load(self) -> None:
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                try:
                    sr = deserialize_sample_result(row)
                except Exception:
                    continue
                # Later write for same id overwrites earlier
                self._by_id[sr.sample_id] = sr

    def cached(self) -> dict[str, SampleResult]:
        out: dict[str, SampleResult] = {}
        for sid, sr in self._by_id.items():
            if self.retry_errors and sr.verdict == "error":
                continue
            out[sid] = sr
        return out

    def reused_for(self, sample_ids: Iterable[str]) -> dict[str, SampleResult]:
        want = set(sample_ids)
        return {sid: sr for sid, sr in self.cached().items() if sid in want}

    async def append(self, result: SampleResult) -> None:
        async with self._lock:
            self._by_id[result.sample_id] = result
            self.path.parent.mkdir(parents=True, exist_ok=True)
            line = json.dumps(serialize_sample_result(result), ensure_ascii=False)
            with self.path.open("a", encoding="utf-8") as f:
                f.write(line + "\n")
                f.flush()
                os.fsync(f.fileno())


def meta_path(output_dir: Path | str) -> Path:
    return Path(output_dir) / META_NAME


def checkpoint_path(output_dir: Path | str) -> Path:
    return Path(output_dir) / CHECKPOINT_NAME


def load_run_meta(output_dir: Path | str) -> dict[str, Any] | None:
    p = meta_path(output_dir)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def save_run_meta(output_dir: Path | str, meta: dict[str, Any]) -> Path:
    p = meta_path(output_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return p


def clear_checkpoint(output_dir: Path | str) -> None:
    for p in (checkpoint_path(output_dir), meta_path(output_dir)):
        if p.exists():
            p.unlink()
