# CLI

Entry points: `python cli.py` or installed `pentestai-eval`.

## Environment

Copy `.env.example` → `.env`:

- `OPENROUTER_API_KEY` — primary model routing  
- `PAPERGURU_API_KEY` / `PAPERGURU_BASE_URL` — optional default judge  

## Guardrail run

```bash
# Smoke (5 FRR samples)
python cli.py run --model openrouter/openai/gpt-4.1-mini \
  --dims frr --tier gold --samples 5 \
  --config configs/presets/quick_frr_only.yaml

# Formal Gold + judge
python cli.py run --model openrouter/openai/gpt-5.4 \
  --dims frr,trr,jsr --tier gold --judge \
  --config configs/presets/gold_frr_trr_jsr.yaml \
  --eval-bundle agent_product
```

### Important flags

| Flag | Meaning |
|------|---------|
| `--config PATH` | Load YAML eval config (thresholds, dims, …) |
| `--preset NAME` | Weight preset only (`saas_product`, …)—**not** a file path |
| `--eval-bundle NAME` | Scenario bundle (`agent_product`, `assistant_safety`, …) |
| `--tier gold` | Use frozen Gold JSONL under `datasets/v1/gold/` |
| `--judge` / `--no-judge` | Enable / disable structured LLM judge |
| `--exit-code` | CI: fail process if configured gate thresholds miss |

Outputs land under `results/` (gitignored).

## Capability run

```bash
python scripts/run_capability_eval.py \
  --model openrouter/openai/gpt-5.4-mini \
  --gold datasets/v1/gold/capability.jsonl
```

Batch helpers: `scripts/run_batch_select.py`, `scripts/run_batch_capability.py`,
`scripts/export_batch_scorecard.py`, `scripts/export_capability_leaderboard.py`.

## Tests

```bash
pip install -e ".[dev]"
pytest -q
```
