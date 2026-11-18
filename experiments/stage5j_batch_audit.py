#!/usr/bin/env python3
"""Independent Stage 5J multi-run synthetic controlled-testbed evidence audit.

Reopens EVERY saved SQLite database, independently rechecks its Stage 5H JSONL
and synthetic source, verifies paired base/burst planned-horizon equality, and
checks per-process resource diagnostics. Does NOT infer research improvement.
"""

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import random

from stage5h_joint_audit import gate
from stage5d_lifecycle_audit import AuditError, require, nonnegative_int


SHAPES = ("base", "burst", "overload")


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def finite_nonnegative(value, label):
    require(type(value) in (int, float) and math.isfinite(value) and value >= 0,
            f"{label} must be finite and nonnegative")


def audit_batch(batch, directory):
    require(isinstance(batch, dict) and set(batch) == {"manifest", "runs"},
            "batch file must have manifest + runs")
    manifest, runs = batch["manifest"], batch["runs"]
    require(isinstance(manifest, dict) and isinstance(runs, list),
            "invalid manifest/runs")
    require(manifest.get("stage") == "5J" and
            manifest.get("type") == "controlled_pilot_manifest", "not a Stage5J batch")
    require(manifest.get("purpose") == "engineering_reproducibility_only_not_scientific_benchmark",
            "undeclared pilot scope")
    require(manifest.get("policy") == "one_worker_fifo_class_neutral_finite_K",
            "unexpected scheduling policy; no new algorithm authorized")
    require(manifest.get("workload_kind") == "seeded_fictional_stage5g_device_context_rule",
            "cannot relabel experimental source origin")
    require(manifest.get("timing_targets_status") == "ARTIFICIAL_DEBUG_ONLY_NOT_OWNER_APPROVED",
            "demo timing targets misrepresented")
    transport = manifest.get("transport")
    require(transport in ("inproc", "mqtt"), "transport must be explicit")
    seeds = manifest.get("seeds")
    require(isinstance(seeds, list) and len(seeds) >= 2 and
            all(type(s) is int and s >= 0 for s in seeds) and len(set(seeds)) == len(seeds),
            "need at least two distinct independent seeded input sets")
    events = nonnegative_int(manifest.get("events_per_shape"), "events_per_shape")
    capacities = manifest.get("capacities_K")
    require(isinstance(capacities, list) and len(capacities) >= 2 and
            all(type(k) is int and k >= 0 for k in capacities) and
            len(set(capacities)) == len(capacities),
            "need multiple distinct nonnegative synthetic waiting capacities")
    require(8 <= events <= 10000, "unsupported source event count")
    require(manifest.get("shapes") == list(SHAPES), "not the frozen three source shapes")
    random_seed = nonnegative_int(manifest.get("randomization_seed"), "shuffle seed")
    require(manifest.get("clock_note") ==
            "new process/monotonic clock per run; never subtract across runs",
            "unsafe cross-run clock claim")
    require(manifest.get("resource_note") ==
            "10ms sampled /proc VmRSS is NOT true peak or memory limit",
            "sampled RSS must disclose bias")
    require(isinstance(manifest.get("host"), dict) and
            all(manifest["host"].get(k) is not None for k in
                ("platform", "python", "sqlite", "logical_cpu_count")),
            "host runtime fingerprint incomplete")
    for k in ("urgent_deadline_ms", "routine_tau_ms"):
        require(type(manifest.get(k)) in (int, float) and
                math.isfinite(manifest[k]) and manifest[k] > 0,
                f"{k} must be positive artificial debug timing only")

    expected_order = [(s, k, shape) for s in seeds for k in capacities for shape in SHAPES]
    random.Random(random_seed).shuffle(expected_order)
    require(len(runs) == len(expected_order), "missing / surplus run in paired design")
    directory = Path(directory)
    by_seed = {}
    total_completed = total_rejected = 0
    observations = []
    for i, (row, pair) in enumerate(zip(runs, expected_order)):
        require(isinstance(row, dict), "each run must be an object")
        seed, K, shape = pair
        stem = f"seed{seed}_K{K}_{shape}"
        require(row.get("order") == i and row.get("seed") == seed and
                row.get("K") == K and row.get("shape") == shape,
                f"run order/seed/capacity pairing altered at {i}")
        for key, expected in (("ledger_path", stem + ".jsonl"),
                              ("db_path", stem + ".sqlite"),
                              ("runner_log_path", stem + ".runner.log")):
            require(row.get(key) == expected, f"{stem} unexpected {key}")
        ledger_path, db_path = directory / row["ledger_path"], directory / row["db_path"]
        log_path = directory / row["runner_log_path"]
        require(ledger_path.is_file() and db_path.is_file() and log_path.is_file(),
                f"{stem} missing raw evidence")
        require(row.get("ledger_sha256") == digest(ledger_path),
                f"{stem} ledger fingerprint changed")
        require(row.get("db_sha256") == digest(db_path),
                f"{stem} SQLite fingerprint changed")
        require(row.get("runner_log_sha256") == digest(log_path),
                f"{stem} process log fingerprint changed")
        with ledger_path.open(encoding="utf-8") as f:
            trace = [json.loads(line) for line in f if line.strip()]
        summary = gate(trace, db_path, require_mqtt=(transport == "mqtt"))
        require(summary["transport"] == transport and summary["shape"] == shape,
                f"{stem} mislabeled trace transport/shape")
        declared = next(r for r in trace if r["type"] == "manifest")
        require(declared["seed"] == seed and declared["K"] == K,
                f"{stem} seed/K differs from batch design")
        require(declared["planned_unique"] == events and
                declared["routine_tau_ns"] == int(manifest["routine_tau_ms"] * 1e6),
                f"{stem} input count / routine tau differs from design")
        urgent = [r for r in trace if r["type"] == "offer" and
                  r["trusted_class"] == "URGENT"]
        require(all(r["urgent_deadline_ns"] - r["offer_ns"] ==
                    int(manifest["urgent_deadline_ms"] * 1e6) for r in urgent),
                f"{stem} urgent debug deadline inconsistent")
        horizon = 0 if shape == "overload" else (events - 1) * 8_000_000
        require(row.get("source_horizon_ns") == horizon,
                f"{stem} source horizon differs from declared profile")
        offers = [r["offer_ns"] for r in trace if r["type"] == "offer"]
        require(row.get("observed_offer_span_ns") == max(offers) - min(offers),
                f"{stem} observed offered span changed")
        for key, actual in (("published_unique", summary["published_unique"]),
                            ("offered_unique", summary["offered_unique"]),
                            ("admitted", summary["admitted"]),
                            ("rejected", summary["rejected"]),
                            ("db_rows_independently_matched", summary["db_rows_independently_matched"]),
                            ("service_p95_ns", summary["db_handler_service_p95_ns"]),
                            ("queue_wait_p95_ns", summary["offer_to_start_p95_ns"]),
                            ("source_sha256", declared["source_sha256"]),
                            ("urgent_failure_U_debug", summary["urgent_failure_U_bounds"]),
                            ("routine_timely_start_R_debug", summary["routine_timely_start_R_bounds"])):
            require(row.get(key) == actual, f"{stem} summary mismatch: {key}")
        require(row.get("return_code") == 0, f"{stem} reported process failure")
        for key in ("wall_elapsed_ns", "child_user_cpu_s", "child_system_cpu_s"):
            finite_nonnegative(row.get(key), f"{stem}.{key}")
        require(type(row.get("rss_samples")) is int and row["rss_samples"] >= 0,
                f"{stem} invalid RSS sample count")
        require(row.get("rss_sampling_interval_ms") == 10,
                f"{stem} undocumented RSS sampling interval")
        rss = row.get("sampled_rss_max_bytes")
        require(rss is None or (type(rss) is int and rss > 0),
                f"{stem} invalid sampled RSS")
        require(not row["rss_samples"] or rss is not None,
                f"{stem} RSS samples exist but maximum missing")
        by_seed.setdefault((seed, K), {})[shape] = (declared["source_sha256"], horizon)
        total_completed += summary["admitted"]
        total_rejected += summary["rejected"]
        observations.append({"seed": seed, "K": K, "shape": shape,
                             "offered": summary["offered_unique"],
                             "committed": summary["admitted"],
                             "rejected": summary["rejected"],
                             "planned_horizon_ns": horizon,
                             "observed_offer_span_ns": row["observed_offer_span_ns"],
                             "service_p95_ns": summary["db_handler_service_p95_ns"]})

    for (seed, K), items in by_seed.items():
        require(set(items) == set(SHAPES), f"seed{seed}/K{K} missing shape")
        a, b, c = (items[shape] for shape in SHAPES)
        require(a[0] == b[0] == c[0] and a[1] == b[1] and c[1] == 0,
                f"seed{seed}/K{K} not source-matched base/burst/overload")
    for seed in seeds:
        expected_hash = by_seed[(seed, capacities[0])]["base"][0]
        require(all(by_seed[(seed, K)]["base"][0] == expected_hash for K in capacities),
                f"seed{seed} source payload changed across waiting capacities")
    return {
        "stage": "5J", "technical_audit": "PASS", "transport": transport,
        "runs_audited": len(runs), "seeds": sorted(seeds),
        "capacities_K": capacities,
        "matched_base_burst_horizon_per_seed": True,
        "total_synthetic_offers": sum(r["offered"] for r in observations),
        "total_committed_lab_sqlite_rows": total_completed,
        "total_full_buffer_rejects": total_rejected,
        "per_run_diagnostics": observations,
        "scientific_inference": "NOT_AUTHORIZED: correlated synthetic events, tiny lab service and unapproved targets",
        "field_calibration": "NOT_AVAILABLE",
        "novel_policy_evaluation": "NOT_PERFORMED",
    }


def self_test():
    import tempfile
    from stage5j_controlled_pilot import run_batch
    with tempfile.TemporaryDirectory(prefix="stage5j-independent-audit-") as tmp:
        dest = Path(tmp) / "batch"
        rows = run_batch(output_dir=dest, transport="inproc", seeds=(71, 72),
                         events=12, capacities=(0, 1), shuffle_seed=14)
        good = audit_batch(rows, dest)
        assert good["runs_audited"] == 12 and good["technical_audit"] == "PASS"
        print("PASS independent positive twelve-run synthetic pilot")
        corruptions = [
            ("wrong planned source horizon", lambda d: d["runs"][0].update(source_horizon_ns=1)),
            ("forged ledger hash", lambda d: d["runs"][0].update(ledger_sha256="x")),
            ("wrong committed count", lambda d: d["runs"][0].update(admitted=999)),
            ("false seed pairing", lambda d: d["runs"][0].update(seed=42)),
            ("false runner CPU", lambda d: d["runs"][0].update(child_user_cpu_s=-1)),
            ("false log hash", lambda d: d["runs"][0].update(runner_log_sha256="x")),
            ("missing case", lambda d: d["runs"].pop()),
            ("pretend owner-approved timing", lambda d: d["manifest"].update(
                timing_targets_status="OPERATOR_APPROVED")),
            ("pretend new scheduler", lambda d: d["manifest"].update(policy="novel_priority")),
        ]
        for label, mutate in corruptions:
            changed = copy.deepcopy(rows)
            mutate(changed)
            try:
                audit_batch(changed, dest)
            except AuditError:
                print("PASS rejected corrupt batch:", label)
            else:
                raise AssertionError("Auditor did not reject " + label)
        print("PASS 9/9 independent batch negatives; no research-performance claim")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("batch", nargs="?", type=Path)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    if args.batch is None:
        ap.error("batch.json path required")
    doc = json.loads(args.batch.read_text(encoding="utf-8"))
    print(json.dumps(audit_batch(doc, args.batch.parent), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
