"""Judge 抽象基类 — 含置信度."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from offsec_guard.core.models import RefusalLevel, Sample
from offsec_guard.core.llm_client import LLMResponse


@dataclass
class VerdictWithReason:
    level: RefusalLevel
    reason: str = ""
    confidence: float = 1.0


class Judge(ABC):
    """判定器抽象基类."""

    @abstractmethod
    def judge(self, response: LLMResponse, sample: Sample) -> VerdictWithReason:
        """基于 LLM 响应和样本元数据判定拒答等级."""
        ...
