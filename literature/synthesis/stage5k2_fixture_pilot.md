# Stage 5K.2 — Policy-independent synthetic fixture pilot

**Date:** 16 November 2026  
**Status:** **ENGINEERING CANDIDATE; 12/12 LOCAL CONTRACT TESTS PASS. NOT FIELD-CALIBRATED, NOT FROZEN, NOT STAGE 6 PERFORMANCE DATA.**

## Why this fixture exists

The Stage 5J real-MQTT/SQLite batch recorded service time for committed work, **not** for full-buffer rejects. Reconstructing rejected service requirements from completed-only observations would introduce selection bias. Stage 5K.2 instead provides an explicitly **fictional**, ex-ante **synthetic work-unit requirement for every offered ID** to develop a fair, paired experiment contract. These units are neither measured handler times nor promises of actual execution latency.

## Deliverables

| Artifact | Purpose | Hard boundary |
| --- | --- | --- |
| `stage5k2_workload_fixture.py` | Deterministic SHA-256-ranked event classes and synthetic work; shape/intensity/dispersion candidate fixtures | No policy results; numerical choices artificial |
| `stage5k2_independent_audit.py` | Separately parse/rehash offers and hidden work; fail closed on ID/count/work/time mismatch; cross-check confounds in pairs | Audits file integrity, not external provenance |
| `test_stage5k2_workload_fixture.py` | 12 positive, pairing, reproducibility, firewall and negative regression cases | Unit-test assertions only |
| `.github/workflows/stage5k2-fixture-integrity.yml` | Repeat the unit and pairing checks in CI; upload short-lived candidate inputs | **No physical or inferential research result** |

**Two separate channels per generated scenario:**

1. `offers.jsonl`: only `fixture_id`, `event_id`, `trusted_class` and planned source offset. A future online dispatcher must see only **locally released arrivals** from this channel. The file is a *batch source* for a load injector, **not** an oracle input to an online policy.
2. `hidden_work.jsonl`: one positive `synthetic_required_work_units` for **every offered ID**, including IDs a future policy might reject. The execution model can access this *after dispatch* and the offline auditor can use it for accounting; **online admission/dispatch cannot inspect it**.
3. `manifest.json`: declarative flags, artificial factor values, counts, paired-work mean, visibility contract and byte-for-byte SHA-256 hashes. No claimed source data, rights statement, signed approval, or service-time calibration.

## Example four-way *engineering* contract probe

Run from repository root with Python 3.12 (illustrative values **only**):

```bash
python literature/validation/stage5k2_workload_fixture.py --out-dir /tmp/stage5k2/smooth
python literature/validation/stage5k2_workload_fixture.py --out-dir /tmp/stage5k2/burst --shape clustered
python literature/validation/stage5k2_workload_fixture.py --out-dir /tmp/stage5k2/intense --horizon-ns 500000000
python literature/validation/stage5k2_workload_fixture.py --out-dir /tmp/stage5k2/variable --dispersion variable

python literature/validation/stage5k2_independent_audit.py /tmp/stage5k2/smooth
python literature/validation/stage5k2_independent_audit.py /tmp/stage5k2/smooth --pair-with /tmp/stage5k2/burst --axis burst_shape
python literature/validation/stage5k2_independent_audit.py /tmp/stage5k2/smooth --pair-with /tmp/stage5k2/intense --axis intensity
python literature/validation/stage5k2_independent_audit.py /tmp/stage5k2/smooth --pair-with /tmp/stage5k2/variable --axis work_dispersion
python literature/validation/test_stage5k2_workload_fixture.py
```

The example uses seed 1729, **60** fictitious events, **15** urgent, planned **1 second** horizon, and mean **4 artificial work units**; smooth-versus-clustered preserves first/last planned time and **identical per-ID work**. The intensity contrast halves the horizon with the same work/shape; dispersion switches from all-4 to balanced 1/7 work units with the same mean and arrival times. These are **software verification values**, **not operationally derived parameter choices**.

## Independently audited invariants

- Raw bytes match manifest hashes; IDs are unique and the same one-to-one population across channels.
- No synthetic work, measured service duration, future-arrival information, or queue outcome is present in `offers.jsonl`.
- Planned timestamps are strictly increasing; first/last timestamps match the horizon.
- Bursty-vs-smooth pairs preserve total offered IDs, classes, work assignments and observation horizon.
- Intensity pairs preserve IDs, classes, shape and per-ID work but change planned horizon.
- Dispersion pairs preserve IDs, classes, and each offered timestamp; work varies but total/mean offered work is fixed.
- Tampered offer bytes, tampered hidden-work bytes, a false manifest count, invalid pairing and invalid configs are rejected.

**Known limitation:** SHA-256 identifies *file bytes*, not a trusted signer or authentic external workload. A person with edit permission can regenerate files and hashes. The generator does not schedule work, implement a fair service-time simulator, enforce future-arrival isolation, model SQLite or MQTT duration, or establish any workload deadline/acceptance threshold. Current finite-buffer FIFO Stage 5J remains only an engineering pilot.

## What must happen before a scientific comparison

1. Professor approves the synthetic-only model scope and narrow novelty position, or supplies legitimate external workload anchors.
2. Justify/freeze class mix, work/service-time conversion, arrival intensity, observation horizon, finite K, urgent deadline and routine wait target; declare sensitivity ranges.
3. Implement matched FIFO, strict priority and closest valid existing-work comparator with **same online information**, finite-buffer admission and trace-verifiable lifecycle semantics; separate instrumentation from treatment.
4. Preregister run/block-level independent seeds, held-out source seeds, policy order, timeout/exclusion rules, statistics and acceptance thresholds.
5. Only then execute/report held-out paired trial results. Do not call this pilot a scientific finding, Best Paper evidence, or field-ready IoT deployment.
