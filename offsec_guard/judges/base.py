"""Judge abstract base — includes confidence."""

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
    """Judge abstract base class."""

    @abstractmethod
    def judge(self, response: LLMResponse, sample: Sample) -> VerdictWithReason:
        """Judge refusal level from LLM response and sample metadata."""
        ...
