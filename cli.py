"""OffSec Guard CLI — command-line entry point."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load repo-root .env (does not override existing env vars)
load_dotenv(Path(__file__).resolve().parent / ".env")

# Avoid silent stalls when progress logs fail encoding on Windows pipes
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)  # type: ignore[attr-defined]
except Exception:
    pass

from offsec_guard.core.config import EvalConfig
from offsec_guard.core.models import ModelIdentity
from offsec_guard.core.llm_client import create_client
from offsec_guard.datasets.schema import SampleRecord
from offsec_guard.datasets.loaders import load_jsonl
from offsec_guard.pipeline.plan import build_run_plan
from offsec_guard.pipeline.executor import ExecutionContext, PipelineExecutor
from offsec_guard.pipeline.gates import evaluate_gates
from offsec_guard.reporters.json_reporter import JSONReporter
from offsec_guard.reporters.markdown_reporter import MarkdownReporter


def _resolve_endpoint(provider: str, model_id: str, cli_base_url: str, cli_api_key: str) -> tuple[str, str]:
    """Pick base_url and api_key from provider / model prefix."""
    prov = (provider or "").lower()
    mid = (model_id or "").lower()
    use_paperguru = (
        prov in {"paperguru", "guru", "paper"}
        or mid.startswith("guru")
        or "paperguru" in mid
        or "guru-pro" in mid
        or "guru/" in mid
    )
    if use_paperguru:
        base = (
            cli_base_url
            if cli_base_url and "openrouter.ai" not in cli_base_url
            else os.getenv("PAPERGURU_BASE_URL", "")
        )
        key = cli_api_key or os.getenv("PAPERGURU_API_KEY", "")
        return base.rstrip("/"), key

    # Official DeepSeek (split from deepseek/* on OpenRouter)
    if prov == "deepseek":
        base = (
            cli_base_url
            if cli_base_url and "openrouter.ai" not in (cli_base_url or "")
            else os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        )
        key = cli_api_key or os.getenv("DEEPSEEK_API_KEY", "")
        return base.rstrip("/"), key

    base = cli_base_url or os.getenv("OFFSEC_GUARD_BASE_URL") or os.getenv(
        "OPENAI_BASE_URL", "https://openrouter.ai/api/v1"
    )
    key = cli_api_key or os.getenv("OFFSEC_GUARD_API_KEY") or os.getenv(
        "OPENROUTER_API_KEY", os.getenv("OPENAI_API_KEY", "")
    )
    return base.rstrip("/"), key


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pentestai-eval",
        description="OffSec Guard — offensive security AI agent guardrail evaluation framework",
    )
    sub = parser.add_subparsers(dest="command")

    # ---- run ----
    run_p = sub.add_parser("run", help="Run model evaluation")
    run_p.add_argument("--model", required=True, help="Model ID, e.g. openrouter/anthropic/claude-sonnet-4.6")
    run_p.add_argument("--provider", default="openrouter")
    run_p.add_argument("--base-url", default="https://openrouter.ai/api/v1")
    run_p.add_argument("--api-key", default="")
    run_p.add_argument("--dims", default="frr", help="Evaluation dimensions, comma-separated")
    run_p.add_argument("--preset", default="", choices=["internal_research", "saas_product", "model_comparison"])
    run_p.add_argument(
        "--eval-bundle",
        default="",
        choices=["", "agent_product", "assistant_safety", "stress_redteam", "paper_main"],
        help=(
            "Named eval bundle (recommended): binds per-dim prompt profile + weights + gate thresholds. "
            "See docs/EVAL_BUNDLES.md"
        ),
    )
    run_p.add_argument(
        "--prompt-profile-frr",
        default="",
        choices=["", "floor", "product", "ceiling"],
        help="Override FRR system pressure tier (prefer --eval-bundle)",
    )
    run_p.add_argument(
        "--prompt-profile-trr",
        default="",
        choices=["", "floor", "product", "ceiling"],
        help="Override TRR system pressure tier",
    )
    run_p.add_argument(
        "--prompt-profile-jsr",
        default="",
        choices=["", "floor", "product", "ceiling"],
        help="Override JSR system pressure tier",
    )
    run_p.add_argument("--samples", type=int, default=0, help="Max samples, 0=all")
    run_p.add_argument("--concurrency", type=int, default=4)
    run_p.add_argument("--output-dir", default="results")
    run_p.add_argument(
        "--no-resume",
        action="store_true",
        help="Ignore checkpoint.jsonl under output-dir; clear and rerun",
    )
    run_p.add_argument(
        "--keep-errors",
        action="store_true",
        help="On resume, keep verdict=error rows and do not retry",
    )
    run_p.add_argument("--exit-code", action="store_true", help="CI mode: exit 1 when configured gate thresholds fail")
    run_p.add_argument("--config", default="", help="Path to YAML config file")
    run_p.add_argument("--dataset", default="", help="Custom dataset path (.jsonl); empty uses built-in")
    run_p.add_argument(
        "--tier",
        default="",
        choices=["", "gold", "all"],
        help="gold=use datasets/v1/gold (formal FRR protocol); all/default=full samples",
    )
    run_p.add_argument(
        "--judge",
        action="store_true",
        help="Enable structured LLM Judge (second pass when rules are low-confidence; fixed shared judge)",
    )
    run_p.add_argument(
        "--no-judge",
        action="store_true",
        help="Disable LLM Judge (rules only)",
    )
    run_p.add_argument(
        "--judge-model",
        default="",
        help="Judge model, e.g. paperguru/guru-pro-1.2 (default: JUDGE_MODEL / config)",
    )
    run_p.add_argument("--judge-base-url", default="", help="Judge API base URL")
    run_p.add_argument("--judge-api-key", default="", help="Judge API key")

    # ---- report ----
    rep_p = sub.add_parser("report", help="Regenerate report from existing JSON results")
    rep_p.add_argument("input", help="Path to eval JSON file")
    rep_p.add_argument("--format", default="md", help="Output format: md, json, html")

    return parser


def parse_model(raw: str) -> tuple[str, str]:
    """Parse 'provider/model-id' format."""
    if "/" in raw:
        provider, model_id = raw.split("/", 1)
        return provider, model_id
    return "openrouter", raw


def _load_samples(args) -> list[dict]:
    """Load samples — custom path first; --tier gold uses formal eval protocol."""
    import sys

    # User-specified custom file
    if args.dataset:
        p = Path(args.dataset)
        if not p.exists():
            print(f"Error: Dataset file not found: {p}")
            sys.exit(1)
        return load_jsonl(str(p), limit=args.samples or 0)

    root = Path(__file__).resolve().parent / "datasets" / "v1"
    dims = [d.strip() for d in (getattr(args, "dims", "frr") or "frr").split(",") if d.strip()]
    tier = getattr(args, "tier", "") or ""

    # Gold: prefer gold/<dim>.jsonl per dimension; fallback to samples/<dim>/
    if tier == "gold":
        samples: list = []
        gold_root = root / "gold"
        samples_root = root / "samples"
        for dim in dims:
            gold_file = gold_root / f"{dim}.jsonl"
            if gold_file.exists():
                samples.extend(load_jsonl(str(gold_file), limit=args.samples or 0))
                continue
            dim_dir = samples_root / dim
            if not dim_dir.is_dir():
                print(f"Warning: no gold/{dim}.jsonl and no samples/{dim}/")
                continue
            print(f"Warning: gold/{dim}.jsonl missing — fallback to samples/{dim}/")
            for f in sorted(dim_dir.glob("*.jsonl")):
                samples.extend(load_jsonl(str(f), limit=args.samples or 0))
        return samples

    # Default: full samples (pipeline routes by expected_action)
    builtin_root = root / "samples"
    if not builtin_root.exists():
        print(f"Builtin datasets not found at {builtin_root}")
        return []

    samples = []
    for dim_dir in sorted(builtin_root.iterdir()):
        if not dim_dir.is_dir():
            continue
        for f in sorted(dim_dir.glob("*.jsonl")):
            samples.extend(load_jsonl(str(f), limit=args.samples or 0))

    return samples


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "report":
        return _cmd_report(args)

    if args.command == "run":
        return _cmd_run(args)

    parser.print_help()


def _cmd_run(args):
    # ── config ──
    if args.config:
        config = EvalConfig.from_yaml(args.config)
    else:
        config = EvalConfig.from_env()

    provider, model_id = parse_model(args.model)
    # If user writes paperguru/xxx, provider becomes paperguru
    if provider.lower() in {"paperguru", "guru", "paper"}:
        config.provider = "paperguru"
    elif provider.lower() == "deepseek":
        config.provider = "deepseek"
    else:
        config.provider = provider
    config.model_id = model_id
    # Default --base-url is openrouter; for official deepseek ignore it and use DEEPSEEK_*
    cli_base = args.base_url
    if config.provider == "deepseek" and "openrouter.ai" in (cli_base or ""):
        cli_base = ""
    base_url, api_key = _resolve_endpoint(
        config.provider, model_id, cli_base, args.api_key or config.api_key
    )
    config.base_url = base_url
    config.api_key = api_key
    config.concurrency = args.concurrency
    config.output_dir = args.output_dir
    config.resume = not bool(getattr(args, "no_resume", False))
    config.retry_checkpoint_errors = not bool(getattr(args, "keep_errors", False))

    if args.preset:
        from offsec_guard.core.config import PRESET_WEIGHTS
        config.weights = PRESET_WEIGHTS[args.preset]

    # Eval bundle: lock per-dim prompt profile / weights / gates (overridable via --prompt-profile-*)
    dims_explicit = bool(args.dims and args.dims != "frr")
    if getattr(args, "eval_bundle", "") or "":
        from offsec_guard.core.eval_bundles import apply_eval_bundle

        apply_eval_bundle(config, args.eval_bundle)
        if dims_explicit:
            config.enabled_dimensions = [d.strip() for d in args.dims.split(",") if d.strip()]
            config.tier_dimensions = list(config.enabled_dimensions)
        else:
            # Default --dims=frr uses bundle dimensions and loads matching samples
            args.dims = ",".join(config.enabled_dimensions)
    else:
        config.enabled_dimensions = [d.strip() for d in args.dims.split(",") if d.strip()]
        config.tier_dimensions = list(config.enabled_dimensions)

    if getattr(args, "prompt_profile_frr", "") or "":
        config.prompt_profile_frr = args.prompt_profile_frr
    if getattr(args, "prompt_profile_trr", "") or "":
        config.prompt_profile_trr = args.prompt_profile_trr
    if getattr(args, "prompt_profile_jsr", "") or "":
        config.prompt_profile_jsr = args.prompt_profile_jsr

    _apply_judge_config(args, config)

    if not config.api_key:
        print(
            "Error: API key required. Set OPENROUTER_API_KEY / PAPERGURU_API_KEY "
            "or --api-key."
        )
        sys.exit(1)
    if not config.base_url:
        print("Error: base_url required. Set PAPERGURU_BASE_URL / OPENAI_BASE_URL or --base-url.")
        sys.exit(1)
    print(f"Endpoint: {config.provider} → {config.base_url} | model={config.model_id}")

    # ── client ──
    identity = ModelIdentity(provider=config.provider, model_id=config.model_id,
                             display_name=config.display_name or f"{config.provider}/{config.model_id}")
    client = create_client(
        identity,
        base_url=config.base_url,
        api_key=config.api_key,
        provider=config.provider,
        timeout_s=config.timeout_s,
        max_retries=config.max_retries,
    )
    judge_client = _build_judge_client(config)

    # ── samples ──
    samples = _load_samples(args)
    if not samples:
        print("Error: No samples found. Use --dataset to specify a .jsonl file, or place datasets under datasets/v1/samples/")
        sys.exit(1)

    print(f"Loaded {len(samples)} samples")
    if config.eval_bundle:
        print(
            f"Eval bundle: {config.eval_bundle} "
            f"(FRR={config.prompt_profile_frr}, TRR={config.prompt_profile_trr}, "
            f"JSR={config.prompt_profile_jsr}; claim_tier={config.claim_tier})"
        )
    else:
        print(
            f"Prompt profiles: FRR={config.prompt_profile_frr}, "
            f"TRR={config.prompt_profile_trr}, JSR={config.prompt_profile_jsr}"
        )
    if config.judge_enabled:
        print(
            f"Judge: {config.judge_provider}/{config.judge_model_id} "
            f"→ {config.judge_base_url or '(default)'}"
        )
    else:
        print("Judge: rules-only")

    sample_objs = [SampleRecord.from_dict(s).to_sample() for s in samples]

    # ── Per-sample checkpoint (output_dir/checkpoint.jsonl) ──
    from offsec_guard.pipeline.checkpoint import (
        checkpoint_path,
        clear_checkpoint,
        fingerprint,
        load_run_meta,
        save_run_meta,
    )

    out_root = Path(config.output_dir)
    out_root.mkdir(parents=True, exist_ok=True)
    config.checkpoint_path = str(checkpoint_path(out_root))
    run_fp = {
        "model": f"{config.provider}/{config.model_id}",
        "eval_bundle": config.eval_bundle or "",
        "prompt_profiles": {
            "frr": config.prompt_profile_frr,
            "trr": config.prompt_profile_trr,
            "jsr": config.prompt_profile_jsr,
        },
        "judge_enabled": config.judge_enabled,
        "judge_model": (
            f"{config.judge_provider}/{config.judge_model_id}"
            if config.judge_enabled
            else ""
        ),
        "tier": getattr(args, "tier", "") or "",
    }
    if not config.resume:
        clear_checkpoint(out_root)
        print("Resume: off (cleared checkpoint)")
    else:
        prev = load_run_meta(out_root)
        if prev:
            prev_fp = fingerprint(prev)
            cur_fp = fingerprint(run_fp)
            if prev_fp != cur_fp:
                print("Error: checkpoint protocol does not match current CLI; refusing resume.")
                print(f"  saved: {prev_fp}")
                print(f"  now:   {cur_fp}")
                print("  Use --no-resume to clear and rerun, or align bundle/profile/judge/tier.")
                sys.exit(2)
            if prev.get("eval_id"):
                config.eval_id = prev["eval_id"]
            print(
                f"Resume: on → {config.checkpoint_path} "
                f"(eval_id={config.eval_id})"
            )
        else:
            print(f"Resume: on → {config.checkpoint_path} (new run)")
    save_run_meta(
        out_root,
        {
            "eval_id": config.eval_id,
            **run_fp,
        },
    )

    # ── pipeline ──
    plan = build_run_plan(config)
    ctx = ExecutionContext(
        config=config,
        plan=plan,
        client=client,
        model=identity,
        judge_client=judge_client,
    )
    executor = PipelineExecutor(ctx)

    report = executor.run_sync(sample_objs)

    # ── output ──
    out_dir = Path(config.output_dir) / report.eval_id
    out_dir.mkdir(parents=True, exist_ok=True)

    gate = evaluate_gates(report, config)
    report.config_snapshot["gate_passed"] = gate.passed
    report.config_snapshot["gate_failures"] = gate.failures

    # summary excludes per-row bodies; rows written separately (avoid huge write failures)
    JSONReporter.save(report, out_dir / "summary.json", include_samples=False)
    MarkdownReporter.save(report, out_dir / "scorecard.md")
    n_rows = sum(len(v) for v in report.sample_results.values())
    if n_rows:
        samples_path = out_dir / "sample_results.json"
        samples_path.write_text(
            JSONReporter.render_sample_results(report),
            encoding="utf-8",
        )

    # Terminal output
    print()
    print(f"═══ OffSec Guard: {identity.display_name}")
    if config.eval_bundle:
        print(f"Bundle: {config.eval_bundle}")
    if not config.claim_tier:
        print(f"Tier: {report.tier.value}  (non-cert run / stress — no Tier claim)")
    else:
        print(f"Tier: {report.tier.value}  (SPEC bar; Unrated = not meeting Tier thresholds)")
    print(f"Total Score: {report.total_score}/100")
    print(gate.summary_line())
    for key, summary in report.dimensions.items():
        label = summary.dimension.label
        n_eff = summary.total_samples - summary.skipped_count - summary.error_count
        err = summary.error_count
        if summary.dimension.value == "frr":
            print(
                f"  {label}: {summary.fail_rate}% fail "
                f"(N_eff={n_eff}, errors={err}; lower is better)"
            )
        elif summary.dimension.value == "jsr":
            print(
                f"  {label}: {summary.fail_rate}% jailbreak "
                f"(N_eff={n_eff}, errors={err}; lower is better)"
            )
        else:
            print(
                f"  {label}: {summary.pass_rate}% refuse "
                f"(N_eff={n_eff}, errors={err}; higher is better)"
            )
    if n_rows:
        print(f"Sample rows: {n_rows} → {out_dir / 'sample_results.json'}")
        print(
            "Audit queue: python scripts/export_audit_queue.py "
            f"{out_dir / 'sample_results.json'}"
        )
    print(f"Reports: {out_dir}/")

    # CI / release gate: configured thresholds (D1)
    if args.exit_code and not gate.passed:
        sys.exit(1)

    sys.exit(0)


def _apply_judge_config(args, config: EvalConfig) -> None:
    """Merge judge config from CLI / ENV / YAML."""
    if args.no_judge:
        config.judge_enabled = False
    elif args.judge or os.getenv("OFFSEC_GUARD_JUDGE", "").lower() in {"1", "true", "yes"}:
        config.judge_enabled = True

    # Default: in-house PaperGuru as fixed shared judge (zero marginal cost)
    default_judge = "paperguru/guru-pro-1.2"
    # When YAML already has provider+model_id, form a parseable string
    if (
        not args.judge_model
        and not os.getenv("JUDGE_MODEL")
        and config.judge_provider
        and config.judge_model_id
        and "/" not in config.judge_model_id
    ):
        judge_model_raw = f"{config.judge_provider}/{config.judge_model_id}"
    else:
        judge_model_raw = (
            args.judge_model
            or os.getenv("JUDGE_MODEL", "")
            or (
                f"{config.judge_provider}/{config.judge_model_id}"
                if config.judge_model_id
                else ""
            )
            or default_judge
        )

    # Supports paperguru/guru-pro-1.2, openrouter/openai/..., openai/...
    if judge_model_raw.startswith("openrouter/"):
        config.judge_provider = "openrouter"
        config.judge_model_id = judge_model_raw.split("/", 1)[1]
    elif judge_model_raw.lower().startswith(("paperguru/", "guru/", "paper/")):
        config.judge_provider = "paperguru"
        config.judge_model_id = judge_model_raw.split("/", 1)[1]
    elif "/" in judge_model_raw and judge_model_raw.split("/", 1)[0] in {
        "openai", "anthropic", "google", "meta-llama", "qwen",
    }:
        config.judge_provider = "openrouter"
        config.judge_model_id = judge_model_raw
    else:
        jp, jmid = parse_model(judge_model_raw)
        if jp.lower() in {"paperguru", "guru", "paper"}:
            config.judge_provider = "paperguru"
            config.judge_model_id = jmid
        elif jp.lower() == "openrouter":
            config.judge_provider = "openrouter"
            config.judge_model_id = jmid
        else:
            config.judge_provider = jp
            config.judge_model_id = jmid

    config.judge_base_url = (
        args.judge_base_url
        or config.judge_base_url
        or os.getenv("JUDGE_BASE_URL", "")
    )
    config.judge_api_key = (
        args.judge_api_key
        or config.judge_api_key
        or os.getenv("JUDGE_API_KEY", "")
    )

    if not config.judge_enabled:
        return

    # When judge credentials are not set separately: PaperGuru → PAPERGURU_*; else OpenRouter
    if not config.judge_api_key:
        if config.judge_provider == "paperguru":
            config.judge_api_key = (
                os.getenv("PAPERGURU_API_KEY", "") or config.api_key
            )
        else:
            config.judge_api_key = (
                os.getenv("OPENROUTER_API_KEY", "") or config.api_key
            )
    if not config.judge_base_url:
        if config.judge_provider == "paperguru":
            config.judge_base_url = os.getenv(
                "PAPERGURU_BASE_URL", "https://llm.paperguru.ai/v1"
            )
        else:
            config.judge_base_url = os.getenv(
                "OPENAI_BASE_URL", "https://openrouter.ai/api/v1"
            )
            config.judge_provider = config.judge_provider or "openrouter"

    if not config.judge_api_key:
        print(
            "Error: --judge enabled but no JUDGE_API_KEY / "
            "PAPERGURU_API_KEY / OPENROUTER_API_KEY available."
        )
        sys.exit(1)


def _build_judge_client(config: EvalConfig):
    if not config.judge_enabled:
        return None
    from offsec_guard.core.llm_client import OpenAICompatibleClient

    identity = ModelIdentity(
        provider=config.judge_provider,
        model_id=config.judge_model_id,
        display_name=f"judge:{config.judge_provider}/{config.judge_model_id}",
    )
    # Judge always uses explicit base_url to avoid openrouter factory hardcoding
    extra = None
    if config.judge_provider == "openrouter" or "openrouter.ai" in (config.judge_base_url or ""):
        extra = {
            "HTTP-Referer": "https://github.com/scantist/offsec-guard",
            "X-Title": "OffSec Guard Judge",
        }
    return OpenAICompatibleClient(
        identity=identity,
        base_url=config.judge_base_url or "https://openrouter.ai/api/v1",
        api_key=config.judge_api_key,
        timeout_s=min(config.timeout_s, 60.0),
        extra_headers=extra,
        max_retries=config.max_retries,
    )


def _cmd_report(args):
    from offsec_guard.core.models import EvalReport
    raw = Path(args.input).read_text(encoding="utf-8")
    report = EvalReport.from_json(raw)

    if args.format == "md":
        md = MarkdownReporter.render(report)
        out = Path(args.input).with_suffix(".md")
        out.write_text(md, encoding="utf-8")
        print(f"Markdown report saved: {out}")
    elif args.format == "json":
        print(JSONReporter.render(report))
    else:
        print(f"Unsupported format: {args.format}")


if __name__ == "__main__":
    main()
