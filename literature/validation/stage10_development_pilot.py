#!/usr/bin/env python3
"""Stage 10 RESERVED development pilot: independent, fail-closed, no inference.

Generates source-matched K3 and K0 synthetic blocks, runs every comparator in a
fresh process, audits physical SQLite and all raw event populations, and reports
descriptive pilot statistics. Never takes Stage 8/9 held-out seeds.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys

from stage5k2_workload_fixture import save_fixture
from stage9_independent_audit import audit_run as stage9_audit
from stage10_independent_audit import audit_run as stage10_audit


HERE = Path(__file__).resolve().parent
DEVELOPMENT_SEEDS = set(range(9001, 9011))
CELLS = {
    "burst": ("clustered", "flat", 1_000_000_000, 3),
    "smooth": ("smooth", "flat", 1_000_000_000, 3),
    "overload": ("smooth", "flat", 250_000_000, 3),
    "variable": ("smooth", "variable", 1_000_000_000, 3),
    "burst_K0": ("clustered", "flat", 1_000_000_000, 0),
}
POLICIES = (
    "fifo_deferred", "strict_deferred", "pushout_deferred",
    "pushout_reserved_deferred",
    "pushout_slack_deferred", "pushout_slack", "stage9_pushout_strict",
)


def _exec(args: list[str]) -> None:
    completed = subprocess.run([sys.executable, *args], cwd=HERE,
                               text=True, capture_output=True, timeout=50)
    if completed.returncode:
        raise RuntimeError(f"TRIAL FAILED: {' '.join(args)}\n{completed.stderr}")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--seeds", type=int, nargs="+", default=[9001, 9002, 9003])
    p.add_argument("--cells", nargs="+", choices=list(CELLS),
                   default=["burst", "smooth", "overload", "burst_K0"])
    p.add_argument("--B", type=int, default=8)
    p.add_argument("--transport", choices=["inproc", "mqtt"], default="inproc")
    a = p.parse_args()
    if (not set(a.seeds) <= DEVELOPMENT_SEEDS or len(set(a.seeds)) != len(a.seeds)
            or len(set(a.cells)) != len(a.cells) or a.B <= 0):
        raise ValueError("Only unique reserved Stage10 9001..9010 development seeds/cells; B>0")
    a.out_dir.mkdir(parents=True, exist_ok=False)
    fixture_root = a.out_dir / "fixtures"
    run_root = a.out_dir / "runs"
    fixture_root.mkdir()
    run_root.mkdir()
    blocks = [(s, c) for s in a.seeds for c in a.cells]
    random.Random(20261117).shuffle(blocks)
    metrics = []
    for index, (seed, cell) in enumerate(blocks, start=1):
        shape, dispersion, horizon, K = CELLS[cell]
        fixture = fixture_root / f"s{seed}_{cell}"
        save_fixture(fixture, seed=seed, count=60, urgent_count=15,
                     horizon_ns=horizon, shape=shape, dispersion=dispersion)
        policy_order = list(POLICIES)
        random.Random(seed*100 + len(cell)).shuffle(policy_order)
        for policy in policy_order:
            prefix = run_root / f"s{seed}_{cell}_{policy}"
            ledger = prefix.with_suffix(".jsonl")
            main_sqlite = prefix.with_suffix(".sqlite")
            spool = run_root / f"s{seed}_{cell}_{policy}_spool.sqlite"
            if policy == "stage9_pushout_strict":
                _exec([str(HERE / "stage9_urgent_pushout.py"),
                       "--fixture-dir", str(fixture), "--transport", a.transport,
                       "--K", str(K), "--output", str(ledger),
                       "--sqlite-output", str(main_sqlite)])
                records = [json.loads(x) for x in ledger.read_text().splitlines() if x.strip()]
                audit = stage9_audit(records, main_sqlite, fixture,
                                     require_mqtt=a.transport == "mqtt")
                urgent = [x for x in records if x.get("type") == "offer" and
                          x.get("trusted_class") == "URGENT"]
                routine = [x for x in records if x.get("type") == "offer" and
                           x.get("trusted_class") == "ROUTINE"]
                U = sum(x["terminal"] != "COMPLETED" or
                        x["complete_ns"] > x["urgent_deadline_ns"] for x in urgent)/len(urgent)
                R = sum(x["terminal"] == "COMPLETED" and
                        x["start_ns"] <= x["offer_ns"] + 20_000_000 for x in routine)/len(routine)
                C = sum(x["terminal"] == "COMPLETED" for x in routine)/len(routine)
                result = {"U": U, "R": R, "C": C,
                          "cancelled":audit["cancelled_pushout"],
                          "rejected":audit["rejected_full"], "spool_inserted":0}
            else:
                B = 0 if policy == "pushout_slack" else a.B
                _exec([str(HERE / "stage10_bounded_recovery.py"),
                       "--fixture-dir", str(fixture), "--policy", policy,
                       "--K", str(K), "--B", str(B), "--transport", a.transport,
                       "--output", str(ledger), "--sqlite-output", str(main_sqlite),
                       "--spool-output", str(spool)])
                records = [json.loads(x) for x in ledger.read_text().splitlines() if x.strip()]
                result = stage10_audit(records, main_sqlite, spool, fixture,
                                       require_mqtt=a.transport == "mqtt")
            metrics.append({"seed": seed, "cell": cell, "K": K,
                            "transport": a.transport,
                            "policy": policy, "B": 0 if policy in
                            {"pushout_slack", "stage9_pushout_strict"} else a.B,
                            "U": result["U"], "R": result["R"], "C": result["C"],
                            "cancelled":result["cancelled"], "rejected":result["rejected"],
                            "spool_inserted": result["spool_inserted"],
                            "ledger_sha256":hashlib.sha256(ledger.read_bytes()).hexdigest(),
                            "audit_passed":True})
            print(json.dumps({"block":f"{index}/{len(blocks)}", **metrics[-1]},
                             sort_keys=True), flush=True)
    fieldnames = list(metrics[0])
    with (a.out_dir / "pilot_metrics.csv").open("x", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(metrics)
    summary = []
    for cell in a.cells:
        for policy in POLICIES:
            subset = [r for r in metrics if r["cell"] == cell and r["policy"] == policy]
            summary.append({"cell":cell,"K":CELLS[cell][3],"B":subset[0]["B"],
                            "policy":policy,"n_seeds":len(subset),
                            **{m:round(sum(x[m] for x in subset)/len(subset),6)
                               for m in ("U","R","C")},
                            "cancelled_total":sum(x["cancelled"] for x in subset),
                            "spool_inserted_total":sum(x["spool_inserted"] for x in subset)})
    (a.out_dir / "pilot_summary.json").write_text(
        json.dumps({"status":"STAGE10_RESERVED_PILOT_NO_INFERENCE",
                    "seeds":a.seeds,"cells":a.cells,"B":a.B,
                    "transport":a.transport,
                    "total_independently_audited_runs":len(metrics),
                    "results":summary},indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":"PILOT_COMPLETE_NO_INFERENCE", "trials":len(metrics),
                      "output":str(a.out_dir / "pilot_summary.json")},sort_keys=True))


if __name__ == "__main__":
    main()
