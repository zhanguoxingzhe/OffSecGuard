"""跑 batch_select_*（按厂商互斥并行 + DeepSeek/OpenRouter 双引擎）.

续跑两级:
  1) 模型级：已有完整 summary.json → 跳过该模型
  2) 样本级：cli 默认写 output-dir/checkpoint.jsonl，中断后同命令续跑未完成题

调度（默认 --by-vendor）:
  - 同一厂商（openai/anthropic/qwen/...）同时只跑 1 个型号
  - 不同厂商可并行，上限 --workers（= 同时跑几个平台）

双引擎 (--split-engines):
  - DeepSeek 车道：deepseek/*（v4→官方 API；r1/v3.2→OpenRouter）
  - OpenRouter 车道：其它厂
  两车道并行；各车道内部仍遵守「一厂一线程」

示例:
  python scripts/run_batch_select.py --eval-bundle stress_redteam \\
    --output-root results/batch_select_stress --split-engines \\
    --by-vendor --workers 4 --concurrency 2 --concurrency-deepseek 1
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
import time
from collections import deque
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "configs" / "batch" / "openrouter_mainstream_models.yaml"
DEFAULT_OUT = ROOT / "results" / "batch_select"
_PRINT_LOCK = threading.Lock()

# 官方 DeepSeek /models 当前仅有这两款（2026-07）
DEEPSEEK_NATIVE: dict[str, str] = {
    "deepseek/deepseek-v4-pro": "deepseek-v4-pro",
    "deepseek/deepseek-v4-flash": "deepseek-v4-flash",
}


@dataclass(frozen=True)
class Route:
    mid: str
    lane: str  # deepseek | openrouter
    cli_model: str
    via: str  # deepseek_native | openrouter


def vendor_of(mid: str) -> str:
    """openai/gpt-x → openai；paperguru/guru → paperguru."""
    return (mid.split("/", 1)[0] or mid).lower()


def route_model(mid: str, *, prefer_native_deepseek: bool = True) -> Route:
    if mid.startswith("deepseek/"):
        native = DEEPSEEK_NATIVE.get(mid) if prefer_native_deepseek else None
        if native:
            return Route(
                mid=mid,
                lane="deepseek",
                cli_model=f"deepseek/{native}",
                via="deepseek_native",
            )
        return Route(
            mid=mid,
            lane="deepseek",
            cli_model=f"openrouter/{mid}",
            via="openrouter",
        )
    if mid.startswith("paperguru/") or mid.startswith("guru/"):
        return Route(mid=mid, lane="openrouter", cli_model=mid, via="paperguru")
    return Route(
        mid=mid,
        lane="openrouter",
        cli_model=f"openrouter/{mid}",
        via="openrouter",
    )


def safe_slug(mid: str) -> str:
    return mid.replace("/", "_")


def is_done(out_dir: Path) -> bool:
    summary = out_dir / "summary.json"
    if not summary.exists():
        kids = list(out_dir.glob("eval-*/summary.json"))
        if not kids:
            return False
        summary = kids[0]
    try:
        data = json.loads(summary.read_text(encoding="utf-8"))
    except Exception:
        return False
    dims = data.get("dimensions") or {}
    return bool(dims.get("frr") and dims.get("trr") and dims.get("jsr"))


def load_ids(batch: str) -> list[str]:
    data = yaml.safe_load(CATALOG.read_text(encoding="utf-8"))
    rows = data.get(batch) or []
    return [r["id"] if isinstance(r, dict) else r for r in rows]


def log_line(mf, msg: str) -> None:
    with _PRINT_LOCK:
        print(msg, end="" if msg.endswith("\n") else "\n", flush=True)
        if mf is not None:
            mf.write(msg if msg.endswith("\n") else msg + "\n")
            mf.flush()


def build_cmd(route: Route, out_dir: Path, args: argparse.Namespace, conc: int) -> list[str]:
    cmd = [
        sys.executable,
        "-u",
        str(ROOT / "cli.py"),
        "run",
        "--model",
        route.cli_model,
        "--dims",
        "frr,trr,jsr",
        "--tier",
        "gold",
        "--judge",
        "--eval-bundle",
        args.eval_bundle,
        "--config",
        args.config,
        "--concurrency",
        str(conc),
        "--output-dir",
        str(out_dir),
    ]
    if route.via == "deepseek_native":
        cmd += ["--provider", "deepseek"]
        ds_base = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        cmd += ["--base-url", ds_base]
    if args.prompt_profile_frr:
        cmd += ["--prompt-profile-frr", args.prompt_profile_frr]
    if args.prompt_profile_trr:
        cmd += ["--prompt-profile-trr", args.prompt_profile_trr]
    if args.prompt_profile_jsr:
        cmd += ["--prompt-profile-jsr", args.prompt_profile_jsr]
    return cmd


def run_one(
    *,
    idx: int,
    total: int,
    route: Route,
    args: argparse.Namespace,
    env: dict,
    log_dir: Path,
    mf,
    conc: int,
    prefix_logs: bool,
) -> tuple[str, int, float]:
    mid = route.mid
    out_dir = args.output_root / safe_slug(mid)
    out_dir.mkdir(parents=True, exist_ok=True)
    model_log = log_dir / f"{safe_slug(mid)}.log"
    cmd = build_cmd(route, out_dir, args, conc)
    vendor = vendor_of(mid)
    tag = f"[{vendor}:{safe_slug(mid)}] "
    header = (
        f"\n=== [{idx}/{total}] {mid} vendor={vendor} lane={route.lane} "
        f"via={route.via} conc={conc} {datetime.now(timezone.utc).isoformat()} ===\n"
        f"CMD: {' '.join(cmd)}\n"
    )
    log_line(mf, header)
    t0 = time.time()
    with model_log.open("w", encoding="utf-8") as lf:
        lf.write(header)
        lf.flush()
        proc = subprocess.Popen(
            cmd,
            cwd=str(ROOT),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
        assert proc.stdout is not None
        for outline in proc.stdout:
            display = f"{tag}{outline}" if prefix_logs else outline
            with _PRINT_LOCK:
                print(display, end="", flush=True)
                lf.write(outline)
                lf.flush()
                if mf is not None:
                    mf.write(display if display.endswith("\n") else display + "\n")
                    mf.flush()
        rc = proc.wait()
    elapsed = time.time() - t0
    status = "OK" if rc == 0 else f"FAIL({rc})"
    log_line(
        mf,
        f"[{status}] model {idx}/{total} {mid} vendor={vendor} via={route.via} "
        f"{elapsed/60:.1f}min -> {out_dir} log={model_log.name}\n",
    )
    return mid, rc, elapsed


def run_lane_serial(
    *,
    lane: str,
    routes: list[Route],
    args: argparse.Namespace,
    env: dict,
    log_dir: Path,
    mf,
    conc: int,
) -> tuple[int, int]:
    ok = fail = 0
    log_line(mf, f"[lane:{lane}] serial n={len(routes)} concurrency={conc}\n")
    for i, route in enumerate(routes, 1):
        use_conc = (
            args.concurrency_paperguru
            if route.mid.startswith("paperguru/")
            else conc
        )
        _, rc, _ = run_one(
            idx=i,
            total=len(routes),
            route=route,
            args=args,
            env=env,
            log_dir=log_dir,
            mf=mf,
            conc=use_conc,
            prefix_logs=False,
        )
        if rc == 0:
            ok += 1
        else:
            fail += 1
            if args.stop_on_error:
                break
    return ok, fail


def run_lane_by_vendor(
    *,
    lane: str,
    routes: list[Route],
    args: argparse.Namespace,
    env: dict,
    log_dir: Path,
    mf,
    max_vendors: int,
    conc: int,
) -> tuple[int, int]:
    """同一厂商同时只跑 1 个型号；不同厂商最多 max_vendors 路并行."""
    if not routes:
        log_line(mf, f"[lane:{lane}] empty, skip\n")
        return 0, 0

    vendors = sorted({vendor_of(r.mid) for r in routes})
    max_vendors = max(1, min(max_vendors, len(vendors)))
    log_line(
        mf,
        f"[lane:{lane}] by-vendor n={len(routes)} vendors={vendors} "
        f"parallel_vendors<={max_vendors} sample_conc={conc}\n",
    )

    waiting: deque[tuple[int, Route]] = deque(
        (i, r) for i, r in enumerate(routes, 1)
    )
    ok = fail = 0
    active_vendors: set[str] = set()
    in_flight: dict = {}

    with ThreadPoolExecutor(max_workers=max_vendors) as pool:
        while waiting or in_flight:
            # 尽量提交：厂商空闲且未达并行上限
            deferred: deque[tuple[int, Route]] = deque()
            while waiting and len(active_vendors) < max_vendors:
                idx, route = waiting.popleft()
                v = vendor_of(route.mid)
                if v in active_vendors:
                    deferred.append((idx, route))
                    continue
                use_conc = (
                    args.concurrency_paperguru
                    if route.mid.startswith("paperguru/")
                    else conc
                )
                fut = pool.submit(
                    run_one,
                    idx=idx,
                    total=len(routes),
                    route=route,
                    args=args,
                    env=env,
                    log_dir=log_dir,
                    mf=mf,
                    conc=use_conc,
                    prefix_logs=True,
                )
                in_flight[fut] = (v, route.mid)
                active_vendors.add(v)
                log_line(
                    mf,
                    f"[lane:{lane}] start {route.mid} "
                    f"(active_vendors={sorted(active_vendors)})\n",
                )
            # 本轮因厂商占用跳过的放回队列尾部
            waiting.extend(deferred)

            if not in_flight:
                # 死锁保护：waiting 非空但都因 vendor 占用 — 不应发生
                if waiting:
                    log_line(mf, f"[lane:{lane}] WARN scheduler stall, force serial one\n")
                    idx, route = waiting.popleft()
                    use_conc = conc
                    _, rc, _ = run_one(
                        idx=idx,
                        total=len(routes),
                        route=route,
                        args=args,
                        env=env,
                        log_dir=log_dir,
                        mf=mf,
                        conc=use_conc,
                        prefix_logs=True,
                    )
                    if rc == 0:
                        ok += 1
                    else:
                        fail += 1
                break

            done_set, _ = wait(in_flight.keys(), return_when=FIRST_COMPLETED)
            for fut in done_set:
                v, mid = in_flight.pop(fut)
                active_vendors.discard(v)
                try:
                    _, rc, _ = fut.result()
                except Exception as exc:
                    log_line(mf, f"[FAIL] {mid} exception: {exc}\n")
                    fail += 1
                    continue
                if rc == 0:
                    ok += 1
                else:
                    fail += 1
                    if args.stop_on_error:
                        # 取消未完成：不再提交新的
                        waiting.clear()
    return ok, fail


def run_lane(
    *,
    lane: str,
    routes: list[Route],
    args: argparse.Namespace,
    env: dict,
    log_dir: Path,
    mf,
    workers: int,
    conc: int,
) -> tuple[int, int]:
    if not routes:
        log_line(mf, f"[lane:{lane}] empty, skip\n")
        return 0, 0
    if args.by_vendor or workers <= 1:
        if not args.by_vendor and workers <= 1:
            return run_lane_serial(
                lane=lane,
                routes=routes,
                args=args,
                env=env,
                log_dir=log_dir,
                mf=mf,
                conc=conc,
            )
        return run_lane_by_vendor(
            lane=lane,
            routes=routes,
            args=args,
            env=env,
            log_dir=log_dir,
            mf=mf,
            max_vendors=workers if args.by_vendor else 1,
            conc=conc,
        )
    # --no-by-vendor 且 workers>1：允许同厂多版本（不推荐）
    log_line(
        mf,
        f"[lane:{lane}] WARN --no-by-vendor: may run multiple versions of same vendor\n",
    )
    ok = fail = 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futs = {
            pool.submit(
                run_one,
                idx=i,
                total=len(routes),
                route=route,
                args=args,
                env=env,
                log_dir=log_dir,
                mf=mf,
                conc=(
                    args.concurrency_paperguru
                    if route.mid.startswith("paperguru/")
                    else conc
                ),
                prefix_logs=True,
            ): route.mid
            for i, route in enumerate(routes, 1)
        }
        from concurrent.futures import as_completed

        for fut in as_completed(futs):
            mid = futs[fut]
            try:
                _, rc, _ = fut.result()
            except Exception as exc:
                log_line(mf, f"[FAIL] {mid} exception: {exc}\n")
                fail += 1
                continue
            if rc == 0:
                ok += 1
            else:
                fail += 1
    return ok, fail


def main() -> int:
    ap = argparse.ArgumentParser(description="Run OffSecGuard batch_select_* Gold evals")
    ap.add_argument("--batch", default="batch_select_core")
    ap.add_argument("--output-root", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--config", default="configs/presets/gold_frr_trr_jsr.yaml")
    ap.add_argument(
        "--eval-bundle",
        default="agent_product",
        help="agent_product | assistant_safety | stress_redteam | paper_main",
    )
    ap.add_argument("--prompt-profile-frr", default="")
    ap.add_argument("--prompt-profile-trr", default="")
    ap.add_argument("--prompt-profile-jsr", default="")
    ap.add_argument(
        "--split-engines",
        action="store_true",
        help="DeepSeek 队列与 OpenRouter 队列并行（官方 DS key + OR key）",
    )
    ap.add_argument(
        "--no-native-deepseek",
        action="store_true",
        help="deepseek/* 全部仍走 OpenRouter（仅分队列，不用官方 API）",
    )
    ap.add_argument(
        "--by-vendor",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="同一厂商同时只跑 1 个型号（默认开；--no-by-vendor 关闭）",
    )
    ap.add_argument(
        "--workers",
        type=int,
        default=4,
        help="最多同时跑几个厂商/平台（默认 4；配合 --by-vendor）",
    )
    ap.add_argument(
        "--workers-deepseek",
        type=int,
        default=1,
        help="DeepSeek 车道并行厂商数（deepseek 只有一家，保持 1）",
    )
    ap.add_argument(
        "--concurrency",
        type=int,
        default=2,
        help="单模型样本并发（OpenRouter 车道）",
    )
    ap.add_argument(
        "--concurrency-deepseek",
        type=int,
        default=4,
        help="单模型样本并发（DeepSeek 车道）",
    )
    ap.add_argument("--concurrency-paperguru", type=int, default=1)
    ap.add_argument("--only", default="", help="逗号分隔模型 ID 子集")
    ap.add_argument("--limit", type=int, default=0, help="最多跑 N 个未完成模型")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="忽略已完成，强制重跑")
    ap.add_argument(
        "--retry-errors",
        action="store_true",
        help="只重跑 checkpoint 中仍有 verdict=error 的模型（配合默认 resume 只补 error 题）",
    )
    ap.add_argument("--stop-on-error", action="store_true")
    args = ap.parse_args()
    args.workers = max(1, int(args.workers))
    args.workers_deepseek = max(1, int(args.workers_deepseek))

    ids = load_ids(args.batch)
    if args.only:
        want = {x.strip() for x in args.only.split(",") if x.strip()}
        ids = [i for i in ids if i in want]
        missing = want - set(ids)
        if missing:
            print(f"WARN: --only 未命中: {sorted(missing)}")

    args.output_root.mkdir(parents=True, exist_ok=True)
    log_dir = args.output_root / "_logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    master = log_dir / f"batch_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.log"

    def checkpoint_error_count(out_dir: Path) -> int:
        cp = out_dir / "checkpoint.jsonl"
        if not cp.exists():
            return 0
        latest: dict[str, str] = {}
        try:
            with cp.open("r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        row = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    sid = row.get("sample_id")
                    if sid:
                        latest[sid] = row.get("verdict") or ""
        except OSError as exc:
            print(f"[warn] cannot read checkpoint {cp}: {exc}")
            return 0
        return sum(1 for v in latest.values() if v == "error")

    pending_ids: list[str] = []
    for mid in ids:
        out_dir = args.output_root / safe_slug(mid)
        if args.retry_errors:
            n_err = checkpoint_error_count(out_dir)
            if n_err <= 0:
                print(f"[skip-no-error] {mid}")
                continue
            print(f"[retry-errors] {mid} n_error={n_err}")
            pending_ids.append(mid)
            continue
        if not args.force and is_done(out_dir):
            print(f"[skip] {mid}")
            continue
        pending_ids.append(mid)

    if args.limit and args.limit > 0:
        pending_ids = pending_ids[: args.limit]

    prefer_native = not args.no_native_deepseek
    routes = [route_model(m, prefer_native_deepseek=prefer_native) for m in pending_ids]
    ds_routes = [r for r in routes if r.lane == "deepseek"]
    or_routes = [r for r in routes if r.lane == "openrouter"]
    or_vendors = sorted({vendor_of(r.mid) for r in or_routes})

    print(
        f"batch={args.batch} total={len(ids)} pending={len(routes)} "
        f"by_vendor={args.by_vendor} split_engines={args.split_engines} "
        f"out={args.output_root}"
    )
    print(
        f"  openrouter_lane: n={len(or_routes)} vendors={or_vendors} "
        f"parallel_vendors<={args.workers} sample_conc={args.concurrency}"
    )
    print(
        f"  deepseek_lane:   n={len(ds_routes)} "
        f"parallel_vendors<={args.workers_deepseek} "
        f"sample_conc={args.concurrency_deepseek}"
    )
    for r in ds_routes:
        print(f"    - {r.mid} -> {r.cli_model} ({r.via})")
    print(f"master_log={master}")

    if args.split_engines and prefer_native and not os.getenv("DEEPSEEK_API_KEY"):
        env_file = ROOT / ".env"
        has = False
        if env_file.exists():
            has = "DEEPSEEK_API_KEY=" in env_file.read_text(encoding="utf-8")
        if not has:
            print("WARN: DEEPSEEK_API_KEY 未设置；native deepseek 会失败，可加 --no-native-deepseek")

    if args.dry_run:
        for r in routes:
            print(
                f"[dry][{r.lane}/{r.via}] vendor={vendor_of(r.mid)} "
                f"{r.cli_model} -> {args.output_root / safe_slug(r.mid)}"
            )
        return 0

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env.setdefault("PYTHONPATH", str(ROOT))

    ok = fail = 0
    with master.open("a", encoding="utf-8") as mf:
        mf.write(
            f"# start {datetime.now(timezone.utc).isoformat()} "
            f"pending={len(routes)} by_vendor={args.by_vendor} "
            f"split={args.split_engines}\n"
        )
        mf.flush()

        if args.split_engines:
            with ThreadPoolExecutor(max_workers=2) as pool:
                fut_or = pool.submit(
                    run_lane,
                    lane="openrouter",
                    routes=or_routes,
                    args=args,
                    env=env,
                    log_dir=log_dir,
                    mf=mf,
                    workers=args.workers,
                    conc=args.concurrency,
                )
                fut_ds = pool.submit(
                    run_lane,
                    lane="deepseek",
                    routes=ds_routes,
                    args=args,
                    env=env,
                    log_dir=log_dir,
                    mf=mf,
                    workers=args.workers_deepseek,
                    conc=args.concurrency_deepseek,
                )
                for fut in (fut_or, fut_ds):
                    o, f = fut.result()
                    ok += o
                    fail += f
        else:
            o, f = run_lane(
                lane="all",
                routes=routes,
                args=args,
                env=env,
                log_dir=log_dir,
                mf=mf,
                workers=args.workers,
                conc=args.concurrency,
            )
            ok, fail = o, f

        summary = (
            f"# done {datetime.now(timezone.utc).isoformat()} "
            f"ok={ok} fail={fail} pending_left={max(0, len(routes) - ok - fail)}\n"
        )
        log_line(mf, summary)

    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
