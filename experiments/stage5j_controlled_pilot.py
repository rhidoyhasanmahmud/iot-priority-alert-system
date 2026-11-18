#!/usr/bin/env python3
"""Stage 5J: repeatable *synthetic controlled-testbed* MQTT-to-SQLite pilot.

One fresh Stage 5H gateway process + SQLite database per run. Reuses existing
two-class FIFO, NOT a candidate scheduler. Randomizes the sequence of paired
synthetic source shapes for independent seeded runs; records host/process
diagnostics and preserves raw ledgers/SQLite backups for external auditing.

No real devices, operator deadlines, host resource limits, scientific inference,
or application representativeness are asserted by these runnable checks.
"""

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import random
import resource
import sqlite3
import subprocess
import sys
import tempfile
import time

from stage5e_gateway_pilot import scheduled_gaps_ns
from stage5h_joint_audit import gate


SHAPES = ("base", "burst", "overload")


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def rss_bytes(pid):
    """Best-effort sampled Linux VmRSS, NOT peak resident memory/CPU limit."""
    try:
        status = Path(f"/proc/{pid}/status").read_text(encoding="utf-8")
    except OSError:
        return None
    for line in status.splitlines():
        if line.startswith("VmRSS:"):
            parts = line.split()
            if len(parts) == 3 and parts[2] == "kB":
                return int(parts[1]) * 1024
    return None


def resource_run(command, interval_s=.01):
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    start = time.monotonic_ns()
    proc = subprocess.Popen(command, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True)
    max_rss = None
    rss_samples = 0
    while proc.poll() is None:
        rss = rss_bytes(proc.pid)
        if rss is not None:
            max_rss = max(max_rss or 0, rss)
            rss_samples += 1
        time.sleep(interval_s)
    output, _ = proc.communicate()
    end = time.monotonic_ns()
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    return {"return_code": proc.returncode, "output": output,
            "wall_elapsed_ns": end - start,
            "child_user_cpu_s": max(0.0, after.ru_utime - before.ru_utime),
            "child_system_cpu_s": max(0.0, after.ru_stime - before.ru_stime),
            "sampled_rss_max_bytes": max_rss,
            "rss_samples": rss_samples,
            "rss_sampling_interval_ms": int(interval_s * 1000)}


def run_batch(*, output_dir, transport, seeds, events, capacities, timeout_s=25,
              urgent_deadline_ms=50, routine_tau_ms=50, shuffle_seed=20261116,
              host="127.0.0.1", port=1883):
    if not seeds or len(set(seeds)) != len(seeds) or any(type(s) is not int or s < 0 for s in seeds):
        raise ValueError("need distinct, nonnegative seeded fixture IDs")
    if not (capacities and len(set(capacities)) == len(capacities) and
            all(type(k) is int and 0 <= k <= 10000 for k in capacities) and
            8 <= events <= 10000 and
            urgent_deadline_ms > 0 and routine_tau_ms > 0 and timeout_s > 0):
        raise ValueError("invalid positive synthetic design arguments")
    if transport not in ("mqtt", "inproc"):
        raise ValueError("transport must be mqtt or inproc")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=False)
    workload = [(seed, K, shape) for seed in seeds for K in capacities for shape in SHAPES]
    random.Random(shuffle_seed).shuffle(workload)
    try:
        paho = importlib.metadata.version("paho-mqtt")
    except importlib.metadata.PackageNotFoundError:
        paho = None
    manifest = {
        "type": "controlled_pilot_manifest", "stage": "5J",
        "purpose": "engineering_reproducibility_only_not_scientific_benchmark",
        "transport": transport, "policy": "one_worker_fifo_class_neutral_finite_K",
        "workload_kind": "seeded_fictional_stage5g_device_context_rule",
        "seeds": list(seeds), "events_per_shape": events,
        "capacities_K": list(capacities),
        "shapes": list(SHAPES), "randomization_seed": shuffle_seed,
        "urgent_deadline_ms": urgent_deadline_ms,
        "routine_tau_ms": routine_tau_ms,
        "timing_targets_status": "ARTIFICIAL_DEBUG_ONLY_NOT_OWNER_APPROVED",
        "design_note": ("base and burst have identical planned source horizon within "
                        "seed across both artificial K values; overload removes gaps "
                        "and changes source intensity"),
        "clock_note": "new process/monotonic clock per run; never subtract across runs",
        "resource_note": "10ms sampled /proc VmRSS is NOT true peak or memory limit",
        "host": {"platform": platform.platform(), "python": platform.python_version(),
                 "sqlite": sqlite3.sqlite_version, "paho": paho,
                 "logical_cpu_count": os.cpu_count()},
    }
    rows = []
    handler = Path(__file__).with_name("stage5h_joint_gateway.py")
    for order, (seed, K, shape) in enumerate(workload):
        stem = f"seed{seed}_K{K}_{shape}"
        ledger = output_dir / f"{stem}.jsonl"
        db = output_dir / f"{stem}.sqlite"
        command = [sys.executable, str(handler), "--transport", transport,
                   "--seed", str(seed), "--shape", shape, "--events", str(events),
                   "--queue-capacity", str(K),
                   "--urgent-deadline-ms", str(urgent_deadline_ms),
                   "--routine-tau-ms", str(routine_tau_ms),
                   "--timeout-s", str(timeout_s), "--host", host,
                   "--port", str(port), "--output", str(ledger),
                   "--sqlite-output", str(db)]
        resources = resource_run(command)
        runner_log = output_dir / f"{stem}.runner.log"
        with runner_log.open("x", encoding="utf-8") as f:
            f.write(resources.pop("output"))
        if resources["return_code"] != 0:
            raise RuntimeError(f"{stem}: child failed with {resources['return_code']}; "
                               f"inspect {stem}.runner.log; partial output is NOT valid")
        with ledger.open(encoding="utf-8") as f:
            trace = [json.loads(s) for s in f if s.strip()]
        summary = gate(trace, db, require_mqtt=(transport == "mqtt"))
        horizon = sum(scheduled_gaps_ns(events, shape))
        offer_times = [r["offer_ns"] for r in trace if r["type"] == "offer"]
        rows.append({"order": order, "seed": seed, "K": K, "shape": shape,
                     "ledger_path": ledger.name, "db_path": db.name,
                     "runner_log_path": f"{stem}.runner.log",
                     "ledger_sha256": sha256(ledger), "db_sha256": sha256(db),
                     "runner_log_sha256": sha256(runner_log),
                     "source_sha256": summary["source_sha256"] if "source_sha256" in summary
                     else next(r for r in trace if r["type"] == "manifest")["source_sha256"],
                     "source_horizon_ns": horizon,
                     "observed_offer_span_ns": max(offer_times) - min(offer_times),
                     "published_unique": summary["published_unique"],
                     "offered_unique": summary["offered_unique"],
                     "admitted": summary["admitted"],
                     "rejected": summary["rejected"],
                     "db_rows_independently_matched": summary["db_rows_independently_matched"],
                     "urgent_failure_U_debug": summary["urgent_failure_U_bounds"],
                     "routine_timely_start_R_debug": summary["routine_timely_start_R_bounds"],
                     "service_p95_ns": summary["db_handler_service_p95_ns"],
                     "queue_wait_p95_ns": summary["offer_to_start_p95_ns"],
                     **resources})
        print(f"PASS {order+1}/{len(workload)} {stem}: offered={summary['offered_unique']} "
              f"SQL={summary['admitted']} rejected={summary['rejected']} "
              f"source horizon={horizon/1e6:.1f}ms")
    batch = {"manifest": manifest, "runs": rows}
    with (output_dir / "batch.json").open("x", encoding="utf-8") as f:
        json.dump(batch, f, sort_keys=True, indent=2)
        f.write("\n")
    return batch


def self_test():
    from stage5j_batch_audit import audit_batch
    with tempfile.TemporaryDirectory(prefix="stage5j-smoke-") as tmp:
        dest = Path(tmp) / "pilots"
        batch = run_batch(output_dir=dest, transport="inproc", seeds=(11, 22),
                          events=12, capacities=(0, 1), shuffle_seed=19)
        result = audit_batch(batch, dest)
        assert result["runs_audited"] == 12 and result["seeds"] == [11, 22]
        assert result["matched_base_burst_horizon_per_seed"]
        print("PASS twelve-run controlled synthetic IN-PROCESS pilot; real MQTT not tested here")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--output-dir", type=Path)
    ap.add_argument("--transport", choices=("mqtt", "inproc"), default="inproc")
    ap.add_argument("--seeds", nargs="+", type=int, default=[101, 202, 303])
    ap.add_argument("--events", type=int, default=60)
    ap.add_argument("--queue-capacities", nargs="+", type=int, default=[0, 3])
    ap.add_argument("--urgent-deadline-ms", type=float, default=50.0)
    ap.add_argument("--routine-tau-ms", type=float, default=50.0)
    ap.add_argument("--shuffle-seed", type=int, default=20261116)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=1883)
    ap.add_argument("--timeout-s", type=float, default=25)
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    if args.output_dir is None:
        ap.error("--output-dir required; no implicit overwriting")
    run_batch(output_dir=args.output_dir, transport=args.transport,
              seeds=tuple(args.seeds), events=args.events,
              capacities=tuple(args.queue_capacities), shuffle_seed=args.shuffle_seed,
              urgent_deadline_ms=args.urgent_deadline_ms,
              routine_tau_ms=args.routine_tau_ms, host=args.host, port=args.port,
              timeout_s=args.timeout_s)
    print("CAUTION: exploratory synthetic testbed measurements only, not inference")


if __name__ == "__main__":
    main()
