# Controlled IoT Alert Scheduling Experiments

This directory holds **executable laboratory simulations/testbeds**, immutable frozen protocols, independent audit code, synthetic fixtures, and checked-in result snapshots. The literature reviews, research questions, analysis, and publication decision records live in [`literature/`](../literature/README.md).

**Scientific boundary:** These are *artificial-input* experiments using a local MQTT broker, one nonpreemptive application worker, a finite local waiting queue and SQLite persistence. They do **not** demonstrate field IoT representativeness, deployment SLAs, method novelty, crash/restart recovery, or universally superior scheduling. The Stage 10 primary artificial-model gate passed, while equal-resource routine completion comparisons and K=0 negative controls are unfavorable; see [the full Stage 10 result and limitations](../literature/synthesis/stage10-heldout-result-record.md).

## Directory layout

- `stage*_*.py`: simulators, controlled experiment runners, independent data auditors and analyses, grouped by stable stage prefixes.
- `test_stage*.py`: automated positive/negative/frozen-protocol regression tests.
- `stage{8,9,10}_frozen_protocol.json`: **byte-pinned, immutable** preregistration records. Do not change their content or reuse heldout seeds.
- `fixtures/`: versioned synthetic trace, ledger, manifest and encoded SQLite test artifacts.
- `stage10-pilot/`: existing development-pilot summary snapshots; not publishable heldout results.
- `stage10-first-heldout-independent-result.json`: the original independent 600-run result snapshot (preserved bytes).

## Quick checks (from repository root)

```bash
python -m compileall -q experiments
python -m unittest discover -s experiments -p 'test_*.py' -v
```

The test suite uses reserved synthetic development seeds and does **not** rerun heldout studies. MQTT integration workflows additionally run broker-backed regression tests. Historical one-time Stage 8, Stage 9, and Stage 10 heldout jobs are disabled for subsequent PRs; only their preflight or unit-validation steps remain active. For a *new* scientific experiment, create a **separately versioned protocol, seed allocation, workflow and output record**.

## Structure migration record

The original `literature/validation/` directory was relocated to this root-level `experiments/` directory. Every historical experiment, fixture, protocol, and result file was moved **without changing blob bytes**; the only executable content edit is an example command path in `stage5i_evidence_gate.py`. Internal script imports, protocol files and within-directory fixture references continue to resolve. The relocation is *not* a new scientific run or data revision.

The Stage 10 immutable protocol SHA-256 is `c66ba9824418ba20fc08be4bcfbb71bc72bff5e04f5b03d38794ccd297fa1429`. The original first-heldout evidence and provenance are documented in [the frozen result record](../literature/synthesis/stage10-heldout-result-record.md).
