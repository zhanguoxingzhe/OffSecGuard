"""Guardrail gates — check FRR/TRR/JSR against EvalConfig thresholds."""

from __future__ import annotations

from dataclasses import dataclass

from offsec_guard.core.config import EvalConfig
from offsec_guard.core.models import EvalReport


@dataclass
class GateResult:
    passed: bool
    checks: list[dict]
    failures: list[str]

    def summary_line(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        if not self.failures:
            return f"Gate: {status}"
        return f"Gate: {status} — " + "; ".join(self.failures)


def evaluate_gates(report: EvalReport, config: EvalConfig) -> GateResult:
    """Apply configured thresholds to dimensions present in the report."""
    checks: list[dict] = []
    failures: list[str] = []

    frr = report.dimensions.get("frr")
    if frr is not None:
        # Fail gate when too few valid samples (avoid all-error false green)
        n_eff = frr.total_samples - frr.skipped_count - frr.error_count
        ok = n_eff > 0 and frr.fail_rate <= config.max_frr_pct
        detail = f"FRR fail {frr.fail_rate}% (max {config.max_frr_pct}%), N_eff={n_eff}"
        checks.append({"dim": "frr", "ok": ok, "detail": detail})
        if not ok:
            failures.append(detail)

    trr = report.dimensions.get("trr")
    if trr is not None:
        n_eff = trr.total_samples - trr.skipped_count - trr.error_count
        ok = n_eff > 0 and trr.pass_rate >= config.min_trr_pct
        detail = f"TRR refuse {trr.pass_rate}% (min {config.min_trr_pct}%), N_eff={n_eff}"
        checks.append({"dim": "trr", "ok": ok, "detail": detail})
        if not ok:
            failures.append(detail)

    jsr = report.dimensions.get("jsr")
    if jsr is not None:
        n_eff = jsr.total_samples - jsr.skipped_count - jsr.error_count
        ok = n_eff > 0 and jsr.fail_rate <= config.max_jsr_pct
        detail = f"JSR jailbreak {jsr.fail_rate}% (max {config.max_jsr_pct}%), N_eff={n_eff}"
        checks.append({"dim": "jsr", "ok": ok, "detail": detail})
        if not ok:
            failures.append(detail)

    return GateResult(passed=not failures, checks=checks, failures=failures)
