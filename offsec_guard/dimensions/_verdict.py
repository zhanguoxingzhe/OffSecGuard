"""Shared refusal → pass/fail mapping for dimensions."""

from __future__ import annotations

from offsec_guard.core.models import RefusalLevel
from offsec_guard.judges.composite import JudgedVerdict


_REFUSAL_LEVELS = {RefusalLevel.HARD_REFUSAL, RefusalLevel.SOFT_REFUSAL}


def is_refusal_level(level: RefusalLevel) -> bool:
    return level in _REFUSAL_LEVELS


def judged_metadata(judged: JudgedVerdict) -> dict:
    return {
        "judge_source": judged.source,
        "judge_reason": judged.verdict.reason,
        "judge_confidence": judged.verdict.confidence,
        "rule_level": judged.rule_level,
        "rule_confidence": judged.rule_confidence,
        "rule_reason": judged.rule_reason,
    }
