"""批量跑 Capability Gold（默认只跑护栏 scorecard 中 cohort≥2 的模型）.

示例:
  python scripts/run_batch_capability.py \\
    --scorecard results/batch_select_stress/_scorecard/stress_redteam_core_scorecard.json \\
    --min-cohort 2 --workers 4 --concurrency 3
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import threading
import time
from collections import defaultdict, deque
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCORECARD = (
    ROOT / "results" / "batch_select_stress" / "_scorecard" / "stress_redteam_core_scorecard.json"
)
DEFAULT_DATASET = ROOT / "datasets" / "v1" / "gold" / "capability.jsonl"
DEFAULT_OUT = ROOT / "results" / "batch_capability_v02"
_PRINT_LOCK = threading.Lock()


def log(msg: str) -> None:
    with _PRINT_LOCK:
        print(msg, flush=True)


def vendor_of(mid: str) -> str:
    return (mid.split("/", 1)[0] or mid).lower()


def safe_slug(mid: str) -> str:
    return mid.replace("/", "_")


def cli_model(mid: str) -> str:
    if mid.startswith("paperguru/") or mid.startswith("guru/"):
        return mid
    return f"openrouter/{mid}"


def load_models(scorecard: Path, min_cohort: int) -> list[dict]:
    data = json.loads(scorecard.read_text(encoding="utf-8"))
    rows = data.get("rows") or data.get("models")
    if rows is None:
        for v in data.values():
            if isinstance(v, list) and v and isinstance(v[0], dict) and "catalog_id" in v[0]:
                rows = v
                break
    if not rows:
        raise SystemExit(f"no model rows in {scorecard}")
    out = []
    seen = set()
    for r in rows:
        cid = r.get("catalog_id")
        if not cid or cid in seen:
            continue
        co = int(r.get("cohort_ord") or 0)
        if co < min_cohort:
            continue
        seen.add(cid)
        out.append({
            "catalog_id": cid,
            "cohort_ord": co,
            "cohort_label": r.get("cohort_label") or "",
            "gen_label": r.get("gen_label") or "",
        })
    out.sort(key=lambda x: (-x["cohort_ord"], x["catalog_id"]))
    return out


def is_done(out_dir: Path) -> bool:
    return any(out_dir.glob("capability_*_summary.json"))


def run_one(mid: str, args: argparse.Namespace) -> tuple[str, int, float]:
    out_dir = Path(args.output_root) / safe_slug(mid)
    out_dir.mkdir(parents=True, exist_ok=True)
    if is_done(out_dir) and not args.force:
        log(f"[skip] {mid}")
        return mid, 0, 0.0
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "run_capability_eval.py"),
        "--model", cli_model(mid),
        "--dataset", str(args.dataset),
        "--concurrency", str(args.concurrency),
        "--output-dir", str(out_dir),
    ]
    if args.include_pending:
        cmd.append("--include-pending")
    t0 = time.time()
    log(f"[run] {mid} -> {out_dir}")
    proc = subprocess.run(cmd, cwd=str(ROOT))
    dt = time.time() - t0
    log(f"[done] {mid} exit={proc.returncode} {dt:.1f}s")
    return mid, proc.returncode, dt


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scorecard", type=Path, default=DEFAULT_SCORECARD)
    ap.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    ap.add_argument("--output-root", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--min-cohort", type=int, default=2, help="1=一代起, 2=二代以上, 3=仅三代")
    ap.add_argument("--workers", type=int, default=4, help="同时跑几个厂商")
    ap.add_argument("--concurrency", type=int, default=3, help="单模型题并发")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--include-pending", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    models = load_models(args.scorecard, args.min_cohort)
    args.output_root.mkdir(parents=True, exist_ok=True)
    manifest = {
        "min_cohort": args.min_cohort,
        "n_models": len(models),
        "dataset": str(args.dataset),
        "models": models,
    }
    (args.output_root / "batch_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    log(f"[batch] models={len(models)} min_cohort={args.min_cohort} out={args.output_root}")
    for m in models:
        log(f"  - {m['catalog_id']}  ({m['cohort_label']})")

    if args.dry_run:
        return

    # 一厂一线程 + 跨厂并行
    by_vendor: dict[str, deque[str]] = defaultdict(deque)
    for m in models:
        by_vendor[vendor_of(m["catalog_id"])].append(m["catalog_id"])

    vendors = list(by_vendor.keys())
    results: list[tuple[str, int, float]] = []

    def next_job() -> str | None:
        # round-robin vendors that still have queue
        for _ in range(len(vendors)):
            v = vendors.pop(0)
            vendors.append(v)
            if by_vendor[v]:
                return by_vendor[v].popleft()
        return None

    inflight_vendors: set[str] = set()
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as ex:
        futs = {}
        while True:
            while len(futs) < args.workers:
                # pick a model whose vendor is free
                picked = None
                for v in list(vendors):
                    if v in inflight_vendors:
                        continue
                    if by_vendor[v]:
                        picked = by_vendor[v].popleft()
                        inflight_vendors.add(v)
                        break
                if not picked:
                    break
                fut = ex.submit(run_one, picked, args)
                futs[fut] = vendor_of(picked)

            if not futs:
                break
            done, _ = wait(futs.keys(), return_when=FIRST_COMPLETED)
            for fut in done:
                v = futs.pop(fut)
                inflight_vendors.discard(v)
                results.append(fut.result())

    ok = sum(1 for _, code, _ in results if code == 0)
    fail = [mid for mid, code, _ in results if code != 0]
    summary = {
        "n_submitted": len(results),
        "n_ok": ok,
        "n_fail": len(fail),
        "failed": fail,
        "elapsed_s": {mid: round(dt, 1) for mid, _, dt in results},
    }
    (args.output_root / "batch_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    log(f"[batch] ok={ok} fail={len(fail)} -> {args.output_root / 'batch_summary.json'}")
    if fail:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
