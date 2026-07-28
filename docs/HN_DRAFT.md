# Hacker News draft (not published)

> Status: draft for review · 2026-07-28  
> Post as **Show HN** after repo is public + LICENSE + Gold-only data cut.

---

## Title options (pick one)

1. **Show HN: OffSecGuard – dual-axis eval for offensive AI agents (safety ≠ capability)**
2. **Show HN: Why the “safest” LLM is often the worst pentest agent**
3. **Show HN: Measuring authorized false refusals and tool-use skill for red-team agents**

Recommended: **#1** (Show HN + clear dual-axis promise). Put the spicy claim in the first paragraph.

---

## Body (paste into HN)

**Show HN: OffSecGuard – dual-axis eval for offensive AI agents (safety ≠ capability)**

We build authorized offensive agents (web/red-team style). Picking a base model by “safety leaderboard” or generic refusal rate kept failing us: some models refuse the job they’re hired for; others sail through safety gates but pick the wrong tools mid-engagement.

So we split evaluation into two axes and refuse to merge them into one vanity score.

### Axis A — Guardrails (should it act?)

Under an **authorized engagement** system prompt (same family as our product prefix):

- **FRR** — false refusal on in-scope offensive tasks (lower better; Tier2 &lt; 5%)
- **TRR** — true refusal on unauthorized / harmful asks (higher better; &gt; 90%)
- **JSR** — jailbreak success / non-refusal under attack prompts (lower better; &lt; 15%)

Gold freeze (eval-first, not “dump all production logs”):

- FRR 120 · TRR 207 · JSR 42  
- Real agent traces are only ~15–30% of FRR Gold (calibration), after rewriting Monitor/Plan blobs into atomic user instructions  
- Distilled research pools stay out of the official denominator

Same Gold + fixed structured judge (PaperGuru as default cost-zero judge; we disclose same-family bias when judging ourselves; human audit on a 25-sample queue: 23/25 agree):

| Metric | Tier2 | GPT-5.4 | PaperGuru 1.2 |
|--------|-------|---------|-----------------|
| FRR fail ↓ | &lt;5% | 57.5% | 13.3% |
| TRR refuse ↑ | &gt;90% | 98.3%* | 91.8% |
| JSR jail ↓ | &lt;15% | 0% | 16.7% |
| Tier | — | Unrated | Unrated |

\*Confirm TRR from the gold_gpt54_judge_pg_v12 run when posting; table above follows methodology §5.3 narrative—verify numbers from `summary.json` before publish.

Reading: GPT-5.4 is a strong **refusal wall** (great TRR/JSR, terrible FRR for authorized offensive work). PaperGuru is more **engagement-transparent** on FRR but misses Tier on JSR. Neither clears the three-way gate—which is the point of not lowering the ruler.

We also publish a derived **misuse_risk** view (how abusable the guardrail surface looks). It is explicitly **not** used for model selection.

### Axis B — Capability proxy (can it work?)

Guardrail score ≠ “good pentest brain.” We added a cheap second screen (not full CVE-Bench / Cybench—those stay for system-level validation):

- **TSR** — tool selection given authorized state  
- **OAR** — next action given tool observation  
- **PQR** — short plan quality from an authorized brief  
- `cap_score = 0.4·TSR + 0.4·OAR + 0.2·PQR`

Protocol: student trajectories propose items → **Teacher Panel** (Claude Opus 4.8 + GPT-5.6-Terra) calibrates gold tool calls / equivalence sets → freeze **cap-gold-v0.2** (N=60) → score with rules, not live LLM grading.

Batch snapshot (30 models, cohort ≥2, N=60 each), top of the board:

| Model | cap_score |
|-------|-----------|
| openai/gpt-5.5 | 83.5 |
| qwen/qwen3.7-max | 83.5 |
| z-ai/glm-5.1 | 81.7 |
| … | … |

Selection rule we actually use: **pass guardrail gates ∩ high cap_score** (shortlist), then optional product-side target runs. No single blended “OffSec IQ.”

### What’s open

- Eval framework + CLI (`--tier gold`, `--eval-bundle`, capability runners)  
- Frozen Gold JSONL (hosts redacted)  
- Docs: methodology, judge design, scoring, capability protocol  
- Leaderboard JSON / scorecard exports  

What’s **not** open (on purpose): raw LangSmith/DuckDB production dumps, unreviewed distill pools, API keys.

### Limits (please roast these)

- Gold N is small; treat as a **selection screen**, not a world championship.  
- Capability is a **proxy**, not end-to-end exploit success.  
- Default judge is our own model → same-family risk; we use human audit + fixed prompts for reproducibility.  
- Single-turn / short-history eval ≠ full multi-agent loop.

Repo: https://github.com/zhanguoxingzhe/OffSecGuard  
Docs entry: `docs/README.md`  
Reproduce guardrail: `python cli.py run --dims frr,trr,jsr --tier gold --judge --config configs/presets/gold_frr_trr_jsr.yaml`  
Reproduce capability: `python scripts/run_capability_eval.py --gold datasets/v1/gold/capability.jsonl …`

Happy to take criticism on thresholds, Teacher Panel choice, and whether 60 capability items is too thin (it is—we’re expanding under versioned freezes).

---

## Comment you should post first (sticky)

If people ask “why not just Cybench?”:

> Cybench/CVE-Bench measure **system + tools + environment**. We need a **cheap base-model screen** that separates (1) refuses authorized work, (2) fails unauthorized work, (3) picks tools like a red-team agent. Full benches stay in product integration. Dual-axis on purpose—no merged score.

---

## Pre-flight checklist before clicking Submit

- [ ] Public GitHub repo + LICENSE (Apache-2.0 or MIT)  
- [ ] README in English for HN audience; Chinese README ok as secondary  
- [ ] Only Gold + constructed samples in the public tree; no DuckDB / distilled raw  
- [ ] Verify FRR/TRR/JSR numbers from frozen `summary.json` (do not trust this draft table blindly)  
- [ ] Link a static leaderboard JSON or HTML (capability + optional stress report)  
- [ ] Disclose PaperGuru judge conflict of interest in README Limitations  
- [ ] `.env` / secrets scrubbed; `results/` stays gitignored or publish only `_scorecard/` exports  
- [ ] Prefer weekday morning US time for Show HN  
