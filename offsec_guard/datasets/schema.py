"""Dataset schema — validate sample format consistency."""

from __future__ import annotations

from dataclasses import dataclass, field

from offsec_guard.core.models import (
    ContextLabel, DomainLabel, CapabilityLabel, ExpectedAction, Sample,
)

VALID_CONTEXTS = {"authorized", "unauthorized", "universal_harm", "grey_zone", "instrumental"}
VALID_DOMAINS = {
    "reconnaissance", "weaponization", "delivery", "exploitation",
    "installation", "command_control", "post_exploitation", "exfiltration",
}
VALID_CAPABILITIES = {
    "knowledge_query", "code_generation", "tool_operation",
    "script_execution", "network_operation", "data_manipulation",
}
VALID_ACTIONS = {"execute", "refuse", "conditional"}
VALID_DIFFICULTIES = {"easy", "medium", "hard"}


@dataclass
class SampleRecord:
    """Raw sample record loaded from file."""
    id: str
    text: str
    context: str = "authorized"
    domain: str = "exploitation"
    capability: str = "tool_operation"
    expected_action: str = "execute"
    difficulty: str = "medium"
    source: str = "manual"
    tags: list[str] = field(default_factory=list)
    history: list[dict[str, str]] = field(default_factory=list)

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.context not in VALID_CONTEXTS:
            errors.append(f"invalid context '{self.context}'")
        if self.domain not in VALID_DOMAINS:
            errors.append(f"invalid domain '{self.domain}'")
        if self.capability not in VALID_CAPABILITIES:
            errors.append(f"invalid capability '{self.capability}'")
        if self.expected_action not in VALID_ACTIONS:
            errors.append(f"invalid expected_action '{self.expected_action}'")
        if self.difficulty not in VALID_DIFFICULTIES:
            errors.append(f"invalid difficulty '{self.difficulty}'")
        return errors

    def to_sample(self) -> Sample:
        return Sample(
            id=self.id,
            text=self.text,
            context=self.context,  # type: ignore[arg-type]
            domain=self.domain,  # type: ignore[arg-type]
            capability=self.capability,  # type: ignore[arg-type]
            expected_action=self.expected_action,  # type: ignore[arg-type]
            difficulty=self.difficulty,  # type: ignore[arg-type]
            source=self.source,
            tags=self.tags,
            history=self.history,
        )

    @classmethod
    def from_dict(cls, data: dict) -> "SampleRecord":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
