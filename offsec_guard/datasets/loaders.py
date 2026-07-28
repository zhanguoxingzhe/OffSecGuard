"""Generic data loaders — JSONL / CSV / YAML."""

from __future__ import annotations

import csv
import json
from typing import Any


def load_jsonl(path: str, *, limit: int = 0) -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            samples.append(json.loads(line))
            if limit > 0 and len(samples) >= limit:
                break
    return samples


def load_csv(path: str, *, limit: int = 0) -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            samples.append(dict(row))
            if limit > 0 and len(samples) >= limit:
                break
    return samples


def load_yaml(path: str, *, limit: int = 0) -> list[dict[str, Any]]:
    import yaml
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if isinstance(data, list):
        return data[:limit] if limit > 0 else data
    if isinstance(data, dict) and "samples" in data:
        samples = data["samples"]
        return samples[:limit] if limit > 0 else samples
    return [data] if limit != 0 else [data]
