"""Dataset registry — metadata and loading."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class DatasetMeta:
    name: str
    version: str = "1.0"
    total_samples: int = 0
    dimensions: list[str] = field(default_factory=list)
    path: str = ""
    description: str = ""
    source: str = "builtin"


class DatasetRegistry:
    """Dataset registry."""

    def __init__(self):
        self._datasets: dict[str, DatasetMeta] = {}

    def register(self, meta: DatasetMeta) -> None:
        self._datasets[meta.name] = meta

    def get(self, name: str) -> DatasetMeta | None:
        return self._datasets.get(name)

    def list(self) -> list[DatasetMeta]:
        return sorted(self._datasets.values(), key=lambda m: m.name)

    def load_samples(self, name: str, limit: int = 0) -> list[dict[str, Any]]:
        meta = self.get(name)
        if meta is None:
            raise KeyError(f"Dataset '{name}' not registered")
        from .loaders import load_jsonl
        return load_jsonl(meta.path, limit=limit)


_registry: DatasetRegistry | None = None


def get_registry() -> DatasetRegistry:
    global _registry
    if _registry is None:
        _registry = DatasetRegistry()
    return _registry


def register_builtin_datasets(datasets_dir: Path) -> DatasetRegistry:
    import yaml
    reg = get_registry()
    manifest_path = datasets_dir / "MANIFEST.yaml"
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = yaml.safe_load(f) or {}
        for dim in manifest.get("dimensions", []):
            samples_dir = datasets_dir / "samples" / dim
            if not samples_dir.exists():
                continue
            for sample_file in sorted(samples_dir.glob("*.jsonl")):
                stem = sample_file.stem
                count = sum(1 for _ in open(sample_file, encoding="utf-8"))
                reg.register(DatasetMeta(
                    name=f"{dim}/{stem}",
                    version=manifest.get("version", "1.0"),
                    total_samples=count,
                    dimensions=[dim],
                    path=str(sample_file),
                    source="builtin",
                ))
    return reg
