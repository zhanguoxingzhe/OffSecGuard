# OffSecGuard

**Dual-axis evaluation for offensive AI agents: guardrails ≠ capability.**

OffSecGuard is an open evaluation framework for choosing base models for
authorized red-team / web-pentest agents. It measures two things separately and
**refuses to merge them into one vanity score**:

| Axis | Question | Metrics |
|------|----------|---------|
| **A. Guardrails** | Should the model act? | FRR · TRR · JSR → Safety Tier |
| **B. Capability proxy** | Can it work like an agent brain? | TSR · OAR · PQR → `cap_score` |

Selection rule we actually use: **pass guardrail gates ∩ high `cap_score`**, then
optional product-side target runs (CVE-Bench / Cybench stay out of this cheap screen).

Chinese overview: [README.zh-CN.md](README.zh-CN.md) · Docs index: [docs/README.md](docs/README.md)

---

## Why this exists

Generic safety benches mix **authorized** offensive work with **unauthorized**
harm. That systematically inflates false refusals for pentest agents—or
underestimates misuse if you only optimize for cooperation.

Production lesson: a model can look “safe” (high TRR / low JSR) and still be
unusable under an authorized engagement prompt (high FRR). Another can pass
guardrails and still pick the wrong tools mid-engagement. Dual-axis fixes both
failure modes for **model shortlisting**.

---

## Guardrail results (Gold v1.2 + fixed judge)

Gold sizes: FRR **120** · TRR **207** · JSR **42**.  
Default structured judge: `paperguru/guru-pro-1.2` (disclose same-family bias when
scoring PaperGuru; human audit on a 25-sample queue: **23/25 agree**).

| Metric | Tier2 target | GPT-5.4 | PaperGuru 1.2 |
|--------|--------------|---------|-----------------|
| FRR fail ↓ | &lt;5% | **57.5%** | **13.3%** |
| TRR refuse ↑ | &gt;90% | **100%** | **91.8%** |
| JSR jail ↓ | &lt;15% | **0%** | **16.7%** |
| Tier | — | Unrated | Unrated |

Reading: GPT-5.4 is a strong **refusal wall**; PaperGuru is more
**engagement-transparent** on FRR but misses the JSR gate. Neither clears all
three thresholds—we do **not** lower the ruler to mint a Tier.

Derived **misuse_risk** (abuse-surface view) is exported in reports and is
**not** used for selection. See [docs/SCORING.md](docs/SCORING.md).

---

## Capability proxy (cap-gold-v0.2)

Cheap single-turn proxies (not end-to-end exploit success):

- **TSR** — tool selection given authorized state  
- **OAR** — next action given tool observation  
- **PQR** — short plan quality from an authorized brief  
- `cap_score = 0.4·TSR + 0.4·OAR + 0.2·PQR`

Protocol: student trajectories propose items → Teacher Panel
(`claude-opus-4.8` + `gpt-5.6-terra`) calibrates gold tool calls → freeze
**cap-gold-v0.2** (N=60) → rule scoring (no live LLM grader).

Example leaderboard snapshot (30 models, cohort ≥ 2):  
[examples/scorecards/capability_cohort2plus_leaderboard.json](examples/scorecards/capability_cohort2plus_leaderboard.json)

Top of that freeze: `openai/gpt-5.5` and `qwen/qwen3.7-max` both ≈ **83.5**
`cap_score`. Treat N=60 as a **selection screen**, not a world championship.

Details: [docs/CAPABILITY_EVAL.md](docs/CAPABILITY_EVAL.md)

---

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Unix:    source .venv/bin/activate
pip install -e ".[dev]"

cp .env.example .env   # set OPENROUTER_API_KEY (and optional PAPERGURU_*)

# Smoke FRR (5 samples)
python cli.py run --model openrouter/openai/gpt-4.1-mini \
  --dims frr --tier gold --samples 5 \
  --config configs/presets/quick_frr_only.yaml

# Formal guardrail Gold + judge
python cli.py run --model openrouter/openai/gpt-5.4 \
  --dims frr,trr,jsr --tier gold --judge \
  --config configs/presets/gold_frr_trr_jsr.yaml

# Capability Gold
python scripts/run_capability_eval.py \
  --model openrouter/openai/gpt-5.4-mini \
  --gold datasets/v1/gold/capability.jsonl
```

CLI reference: [docs/CLI_REFERENCE.md](docs/CLI_REFERENCE.md)

---

## Repository layout

```
offsec_guard/     # eval framework
datasets/v1/gold/ # frozen Gold JSONL (capability hosts redacted for public release)
configs/presets/  # ready-made run configs
scripts/          # freeze / batch / capability runners
docs/             # methodology, scoring, bundles, decisions
examples/         # published scorecard snapshots
tests/            # unit tests
```

**Not in this public tree (on purpose):** raw LangSmith/DuckDB dumps, unreviewed
distill pools, full private run directories. Internal working copies may keep those
separately.

---

## Safety / dual-use notice

This project includes **authorized offensive prompts**, **unauthorized / harmful
prompts**, and **jailbreak patterns** used only to score model refusals. It is
an evaluation harness, not an exploit kit. Do not use it to attack systems
without authorization. Capability items are redacted for public release
(`REDACTED_DOMAIN`); please keep them that way in forks.

---

## Limitations

- Gold N is modest (guardrail ~369; capability 60).  
- Capability is a **proxy**, not CVE-Bench / Cybench mission success.  
- Default judge is PaperGuru → same-family risk when judging PaperGuru.  
- Single-turn / short-history ≠ full multi-agent product loop.  
- Public capability Gold is host-redacted; semantics preserved for scoring.

---

## License

[MIT](LICENSE) — permissive use, modification, and redistribution.

## Citation

If you use OffSecGuard in work or papers, please cite this repository and the
Gold freeze versions (`gold-v1.2`, `cap-gold-v0.2`).
