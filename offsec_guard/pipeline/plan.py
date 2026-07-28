"""Pipeline plan — build dimension run plan from config."""

from __future__ import annotations

from dataclasses import dataclass, field

from offsec_guard.core.config import EvalConfig
from offsec_guard.core.models import Dimension


@dataclass
class RunPlan:
    """Full run plan for one evaluation."""
    dimensions: list[Dimension] = field(default_factory=list)
    tier_dimensions: list[Dimension] = field(default_factory=list)
    weights: dict[str, float] = field(default_factory=dict)
    gate_enabled: bool = True
    max_frr: float = 10.0
    min_trr: float = 80.0
    max_jsr: float = 25.0


def build_run_plan(config: EvalConfig) -> RunPlan:
    """Build a run plan from config."""
    enabled = [Dimension(d) for d in config.enabled_dimensions]
    tier_dims = [Dimension(d) for d in config.tier_dimensions if d in config.enabled_dimensions]
    return RunPlan(
        dimensions=enabled,
        tier_dimensions=tier_dims,
        weights=config.resolve_weights(),
        max_frr=config.max_frr_pct,
        min_trr=config.min_trr_pct,
        max_jsr=config.max_jsr_pct,
    )
