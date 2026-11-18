#!/usr/bin/env python3
"""Measure an *illustrative* PBKDF2 work-unit + SQLite handler on this host.

This characterizes laboratory service execution only. It does NOT calibrate
field arrival rates, device severity, rejected real-world work, hardware
capacity, or operator deadlines; no policy comparison is performed here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import sqlite3
import statistics
import time

from stage5g_reference_handler import canonical, open_db, process_one


def pct(values: list[int], fraction: float) -> int:
    s = sorted(values)
    return s[max(0, min(len(s) - 1, int((len(s) * fraction + 0.999999)) - 1))]


def run_probe(*, iterations_per_unit: int, seed: int, repetitions: int,
              output: Path, sqlite_output: Path) -> dict:
    if not (100 <= iterations_per_unit <= 1_000_000 and seed >= 0 and 5 <= repetitions <= 100):
        raise ValueError("Require 100..1e6 iterations/unit, nonnegative seed and 5..100 repetitions")
    jobs = [(unit, rep) for unit in (1, 4, 7) for rep in range(repetitions)]
    random.Random(seed).shuffle(jobs)
    # Fail before measurement if either output is already present.
    if output.exists() or sqlite_output.exists():
        raise FileExistsError("Refusing to overwrite existing calibration evidence")
    con = open_db(sqlite_output)
    rows = []
    try:
        for index, (unit, _) in enumerate(jobs):
            eid = f"synthetic_calibration_{seed}_{index:04d}"
            src = {"event_id": eid, "device_id": "device_01", "kind": "health",
                   "tamper": False, "battery_pct": 75}
            start = time.monotonic_ns()
            result = hashlib.pbkdf2_hmac("sha256", eid.encode(),
                                        b"STAGE7-ARTIFICIAL-WORK-NOT-AN-IOT-PROFILE",
                                        unit * iterations_per_unit)
            cpu_end = time.monotonic_ns()
            if len(result) != 32:
                raise RuntimeError("Artificial CPU operation failed")
            handled = process_one(con, src)
            rows.append({"event_id": eid, "units": unit,
                         "iterations": unit * iterations_per_unit,
                         "cpu_ns": cpu_end - start, "sqlite_ns": handled["service_ns"],
                         "cpu_plus_sqlite_ns": cpu_end - start + handled["service_ns"],
                         "result_json": handled["result_json"]})
    finally:
        con.close()
    # A normal reopen confirms logical SQLite persistence, not crash durability.
    verify = sqlite3.connect(sqlite_output)
    try:
        persisted = {r[0] for r in verify.execute("SELECT event_id FROM handled_alerts")}
        if persisted != {r["event_id"] for r in rows}:
            raise RuntimeError("Handler records missing after normal reopen")
    finally:
        verify.close()
    groups = {str(unit): {
        "samples": repetitions,
        "cpu_median_ns": int(statistics.median([r["cpu_ns"] for r in rows if r["units"] == unit])),
        "sqlite_median_ns": int(statistics.median([r["sqlite_ns"] for r in rows if r["units"] == unit])),
        "total_p05_ns": pct([r["cpu_plus_sqlite_ns"] for r in rows if r["units"] == unit], .05),
        "total_median_ns": int(statistics.median([r["cpu_plus_sqlite_ns"] for r in rows if r["units"] == unit])),
        "total_p95_ns": pct([r["cpu_plus_sqlite_ns"] for r in rows if r["units"] == unit], .95),
    } for unit in (1, 4, 7)}
    raw_bytes = b"".join((canonical(r) + "\n").encode() for r in rows)
    summary = {
        "status": "ARTIFICIAL_HOST_LAB_SERVICE_CHARACTERIZATION_ONLY_NOT_FIELD_CALIBRATION",
        "seed": seed, "repetitions_per_work_unit": repetitions,
        "iterations_per_unit": iterations_per_unit,
        "units": [1, 4, 7], "rows_sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "sqlite_sha256": hashlib.sha256(sqlite_output.read_bytes()).hexdigest(),
        "rows": rows,
        "by_unit": groups,
        "host": {"platform": platform.platform(), "python": platform.python_version(),
                 "sqlite": sqlite3.sqlite_version, "logical_cpus": os.cpu_count()},
        "clock": "single_process_monotonic_ns",
        "measurement": "PBKDF2_SHA256_cpu_then_reference_SQLite_WAL_FULL_commit",
        "warning": "Hypothetical work units/ratios; no source-device or service-time generalization",
    }
    with output.open("x", encoding="utf-8") as handle:
        handle.write(canonical(summary) + "\n")
    return summary


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--iterations-per-unit", type=int, default=10_000)
    p.add_argument("--seed", type=int, default=917)
    p.add_argument("--repetitions", type=int, default=8)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--sqlite-output", required=True, type=Path)
    args = p.parse_args()
    report = run_probe(iterations_per_unit=args.iterations_per_unit, seed=args.seed,
                       repetitions=args.repetitions, output=args.output,
                       sqlite_output=args.sqlite_output)
    print(json.dumps({"status": report["status"], "by_unit": report["by_unit"],
                      "seed": report["seed"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
