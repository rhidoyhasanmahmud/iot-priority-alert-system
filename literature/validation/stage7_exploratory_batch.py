#!/usr/bin/env python3
"""Reproducible but *NOT PREREGISTERED* artificial MQTT/SQLite policy pilot.

Separate fresh gateway/SQLite process for each seed, scenario, K and baseline.
The source fixture is made once per matched block, and the verifier runs in
another process. Statistical inference, operational calibration, and a novel
algorithm are explicitly out of scope until research protocol approval.
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
import subprocess
import sys

from stage5k2_workload_fixture import save_fixture


SCENARIOS = {
    "smooth": {"shape": "smooth", "dispersion": "flat", "horizon_ns": 1_000_000_000},
    "burst": {"shape": "clustered", "dispersion": "flat", "horizon_ns": 1_000_000_000},
    "intense": {"shape": "smooth", "dispersion": "flat", "horizon_ns": 500_000_000},
    "variable": {"shape": "smooth", "dispersion": "variable", "horizon_ns": 1_000_000_000},
}
POLICIES = ("fifo", "strict_urgent_first")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def checked_command(args: list[str], *, timeout_s: int) -> tuple[str, str]:
    result = subprocess.run(args, capture_output=True, text=True,
                            timeout=timeout_s, check=False)
    if result.returncode:
        raise RuntimeError(f"Subprocess failed ({result.returncode}): {args[1]}\n"
                           f"stdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}")
    return result.stdout, result.stderr


def run_batch(*, output_dir: Path, transport: str, seeds: tuple[int, ...],
              capacities: tuple[int, ...], count: int = 60,
              iterations_per_unit: int = 10_000, shuffle_seed: int = 20261116,
              timeout_s: int = 30) -> dict:
    if (transport not in {"inproc", "mqtt"} or len(seeds) < 2 or
            len(seeds) != len(set(seeds)) or any(s < 0 for s in seeds) or
            not capacities or len(set(capacities)) != len(capacities) or
            any(k < 0 for k in capacities) or
            count < 20 or count % 4 != 0 or not 100 <= iterations_per_unit <= 1_000_000):
        raise ValueError("Invalid candidate study design: use >=2 distinct seeds, even 4-multiple count")
    root = Path(__file__).parent
    output_dir.mkdir(parents=True, exist_ok=False)
    fixture_root = output_dir / "fixtures"
    fixture_root.mkdir()
    runs_root = output_dir / "runs"
    runs_root.mkdir()

    cal_report, cal_db = output_dir / "lab_calibration.json", output_dir / "lab_calibration.sqlite"
    checked_command([sys.executable, str(root / "stage7_calibration_probe.py"),
                     "--seed", "917", "--repetitions", "12",
                     "--iterations-per-unit", str(iterations_per_unit),
                     "--output", str(cal_report), "--sqlite-output", str(cal_db)], timeout_s=60)
    calibration_out, _ = checked_command(
        [sys.executable, str(root / "stage7_calibration_audit.py"),
         "--report", str(cal_report), "--sqlite", str(cal_db)], timeout_s=20)
    calibration = json.loads(calibration_out)
    if not calibration["status"].startswith("PASS_") or calibration["field_calibrated"] is not False:
        raise RuntimeError("Artificial lab probe failed independent evidence gate")

    fixtures = {}
    for seed in seeds:
        for scenario, args in SCENARIOS.items():
            name = f"seed{seed}_{scenario}"
            path = fixture_root / name
            save_fixture(path, seed=seed, count=count, urgent_count=count // 4, **args)
            fixtures[(seed, scenario)] = path

    planned = [(seed, K, scenario, policy) for seed in seeds
               for K in capacities for scenario in SCENARIOS for policy in POLICIES]
    random.Random(shuffle_seed).shuffle(planned)
    report = {
        "status": "EXPLORATORY_SYNTHETIC_ENGINEERING_ONLY_NOT_PREREGISTERED",
        "field_calibrated": False, "research_protocol_approved": False,
        "novel_policy_verified": False, "scientific_conclusion_allowed": False,
        "transport": transport, "independent_trial_seed_count": len(seeds),
        "seeds": list(seeds), "capacity_K": list(capacities),
        "events_per_run": count, "work_units_to_pbkdf2_iterations": iterations_per_unit,
        "shuffle_seed": shuffle_seed, "scenario_contract": SCENARIOS,
        "policies": list(POLICIES),
        "debug_urgent_deadline_ms": 20.0, "debug_routine_tau_ms": 20.0,
        "debug_targets_status": "ARTIFICIAL_NOT_OWNER_APPROVED",
        "calibration_report": cal_report.name,
        "calibration_sha256": sha256(cal_report),
        "calibration_sqlite": cal_db.name,
        "calibration_sqlite_sha256": sha256(cal_db),
        "host": {"platform": platform.platform(), "python": platform.python_version(),
                 "sqlite": sqlite3.sqlite_version, "logical_cpus": os.cpu_count()},
        "runs": [],
    }
    try:
        for index, (seed, K, scenario, policy) in enumerate(planned, 1):
            name = f"s{seed}_K{K}_{scenario}_{policy}"
            ledger = runs_root / f"{name}.jsonl"
            db = runs_root / f"{name}.sqlite"
            fixture = fixtures[(seed, scenario)]
            out, stderr = checked_command(
                [sys.executable, str(root / "stage7_controlled_replay.py"),
                 "--fixture-dir", str(fixture), "--policy", policy,
                 "--transport", transport, "--K", str(K),
                 "--iterations-per-unit", str(iterations_per_unit),
                 "--urgent-deadline-ms", "20", "--routine-tau-ms", "20",
                 "--sqlite-output", str(db), "--output", str(ledger),
                 "--timeout-s", str(timeout_s)], timeout_s=timeout_s + 20)
            gate_args = [sys.executable, str(root / "stage7_independent_replay_audit.py"),
                         "--ledger", str(ledger), "--sqlite", str(db),
                         "--fixture-dir", str(fixture)]
            if transport == "mqtt":
                gate_args.append("--require-mqtt")
            audited, _ = checked_command(gate_args, timeout_s=20)
            gate = json.loads(audited)
            if gate["status"] != "PASS_STAGE7_SYNTHETIC_ACCOUNTING_ONLY":
                raise RuntimeError("Independent replay audit did not PASS")
            report["runs"].append({
                "execution_order": index, "seed": seed, "K": K, "scenario": scenario,
                "policy": policy, "fixture_dir": f"fixtures/{fixture.name}",
                "ledger_path": f"runs/{ledger.name}", "sqlite_path": f"runs/{db.name}",
                "ledger_sha256": sha256(ledger), "sqlite_sha256": sha256(db),
                "offered": gate["offered"], "committed": gate["committed"],
                "rejected": gate["rejected"],
                "U_debug": gate["U_artificial_debug_only"],
                "R_debug": gate["R_artificial_debug_only"],
                "independent_gate": gate["status"],
                "source_fixture_sha256": gate["source_fixture_sha256"],
                "hidden_fixture_sha256": gate["hidden_fixture_sha256"],
            })
            print(f"PASS {index}/{len(planned)} {name}: {gate['committed']} SQL / "
                  f"{gate['rejected']} rejected (debug only)", flush=True)
    finally:
        # Persist a partial clearly INVALID diagnostic report if any run fails.
        report["complete"] = len(report["runs"]) == len(planned)
        report["expected_run_count"] = len(planned)
        with (output_dir / "batch.json").open("x", encoding="utf-8") as f:
            json.dump(report, f, indent=2, sort_keys=True)
            f.write("\n")
    if not report["complete"]:
        raise RuntimeError("Incomplete synthetic exploratory batch; cannot be used as evidence")
    return report


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir", required=True, type=Path)
    p.add_argument("--transport", choices=["inproc", "mqtt"], default="inproc")
    p.add_argument("--seeds", nargs="+", type=int, default=[101, 202])
    p.add_argument("--capacities", nargs="+", type=int, default=[0, 3])
    p.add_argument("--events", type=int, default=60)
    p.add_argument("--iterations-per-unit", type=int, default=10_000)
    p.add_argument("--shuffle-seed", type=int, default=20261116)
    p.add_argument("--timeout-s", type=int, default=30)
    args = p.parse_args()
    result = run_batch(output_dir=args.output_dir, transport=args.transport,
                       seeds=tuple(args.seeds), capacities=tuple(args.capacities),
                       count=args.events, iterations_per_unit=args.iterations_per_unit,
                       shuffle_seed=args.shuffle_seed, timeout_s=args.timeout_s)
    print(f"Synthetic batch contract complete: {len(result['runs'])} runs; "
          "NO FIELD CALIBRATION OR SCIENTIFIC INFERENCE")


if __name__ == "__main__":
    main()
