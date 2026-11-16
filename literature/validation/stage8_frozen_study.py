#!/usr/bin/env python3
"""Execute an immutable, *conditional synthetic-only* controlled MQTT study.

Held-out source seeds are reserved for one complete run after the protocol and
analysis have been committed. Never use them for tuning or debugging. Failure
produces a clearly invalid partial manifest, not selectively retained results.
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
from datetime import datetime, timezone

from stage5k2_workload_fixture import save_fixture


PROTOCOL_SHA256 = "1fe656270ce5843af8b26a6a288f712bb4afbf25a05f7d1f2ea9221e93163c52"
PROTOCOL_ID = "STI-2026-STAGE8-SYNTHETIC-HOLDOUT-V1"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_protocol(path: Path) -> dict:
    if sha256(path) != PROTOCOL_SHA256:
        raise ValueError("Study protocol has changed since freeze; no experiment authorized")
    config = json.loads(path.read_text(encoding="utf-8"))
    if (config["protocol_id"] != PROTOCOL_ID or config["experimental_runs"] != 450
            or len(config["holdout_seeds"]) != 30 or len(set(config["holdout_seeds"])) != 30
            or set(config["holdout_seeds"]) & (set(config["pilot_only_seeds"]) |
                                               set(config["known_prior_pilot_seeds_excluded"]))
            or config["policies"] != ["fifo", "strict_urgent_first", "routine_wait_guard"]
            or config["transport"] != "mqtt" or config["real_iot_workload_calibrated"] is not False
            or config["candidate_novelty_claimed"] is not False):
        raise ValueError("Frozen study identities/constraints are invalid")
    return config


def checked_command(cmd: list[str], timeout_s: int) -> str:
    completed = subprocess.run(cmd, capture_output=True, text=True,
                               timeout=timeout_s, check=False)
    if completed.returncode:
        raise RuntimeError(f"Command failed: {cmd[1]} (exit {completed.returncode}): "
                           f"{completed.stderr[-2000:]} {completed.stdout[-1500:]}")
    return completed.stdout


def policy_order(config: dict, seed: int, scenario: str, K: int) -> list[str]:
    policies = list(config["policies"])
    seed_material = f"stage8|{config['seed_block_order_shuffle_seed']}|{seed}|{scenario}|{K}"
    seed_hash = int.from_bytes(hashlib.sha256(seed_material.encode()).digest()[:8], "big")
    random.Random(seed_hash).shuffle(policies)
    return policies


def plan(config: dict, *, pilot: bool, pilot_seeds: tuple[int, ...] = (7001,)) -> list[tuple]:
    cells = (config["study_cells"][:2] if pilot else config["study_cells"])
    seeds = (pilot_seeds if pilot else config["holdout_seeds"])
    if pilot and (not seeds or not set(seeds).issubset(config["pilot_only_seeds"])):
        raise ValueError("Pilot may use only the reserved tuning seeds")
    blocks = [(seed, cell["scenario"], cell["K"]) for seed in seeds for cell in cells]
    random.Random(config["seed_block_order_shuffle_seed"]).shuffle(blocks)
    return [(seed, scenario, K, policy) for seed, scenario, K in blocks
            for policy in policy_order(config, seed, scenario, K)]


def run_study(*, config_path: Path, output_dir: Path, pilot: bool,
              pilot_seeds: tuple[int, ...], git_revision: str,
              timeout_s: int = 35) -> dict:
    config = load_protocol(config_path)
    if not pilot and (not git_revision or git_revision == "UNCOMMITTED"):
        raise ValueError("Held-out experiment requires a frozen Git commit identifier")
    if timeout_s != config["execution"]["per_trial_timeout_s"]:
        raise ValueError("Cannot modify frozen per-trial timeout")
    root = Path(__file__).resolve().parent
    trials = plan(config, pilot=pilot, pilot_seeds=pilot_seeds)
    if not pilot and len(trials) != config["experimental_runs"]:
        raise ValueError("Frozen study cell count differs from the protocol")
    output_dir.mkdir(parents=True, exist_ok=False)
    fixtures_root = output_dir / "fixtures"
    runs_root = output_dir / "runs"
    fixtures_root.mkdir()
    runs_root.mkdir()
    all_keys = sorted(set((seed, scenario) for seed, scenario, _, _ in trials))
    for seed, scenario in all_keys:
        args = config["scenarios"][scenario]
        save_fixture(fixtures_root / f"s{seed}_{scenario}", seed=seed,
                     count=config["source_count"], urgent_count=config["urgent_count"],
                     **args)

    report_path, cal_db = (output_dir / "lab_service_characterization.json",
                           output_dir / "lab_service_characterization.sqlite")
    manifest = {
        "status": "INCOMPLETE_NOT_SCIENTIFIC_EVIDENCE",
        "protocol_id": PROTOCOL_ID,
        "protocol_sha256": PROTOCOL_SHA256,
        "study_phase": "RESERVED_TUNING_ENGINEERING_PILOT" if pilot else "FROZEN_HELDOUT_SYNTHETIC",
        "provenance": "ARTIFICIAL_NOT_FIELD_CALIBRATED_NOT_NOVELTY_APPROVED",
        "field_calibrated": False,
        "novelty_verified": False,
        "transport": "inproc" if pilot else "mqtt",
        "head_source_revision": git_revision,
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "host": {
            "platform": platform.platform(), "python": platform.python_version(),
            "sqlite": sqlite3.sqlite_version, "logical_cpu_count": os.cpu_count(),
        },
        "seeds": list(pilot_seeds if pilot else config["holdout_seeds"]),
        "planned_trial_count": len(trials),
        "planned_trial_cells": [{"seed": s, "scenario": n, "K": k, "policy": p}
                                for s, n, k, p in trials],
        "calibration": None,
        "runs": [],
    }
    try:
        checked_command([sys.executable, str(root / "stage7_calibration_probe.py"),
                         "--seed", "917", "--repetitions", "12",
                         "--iterations-per-unit", str(config["pbkdf2_iterations_per_work_unit"]),
                         "--output", str(report_path), "--sqlite-output", str(cal_db)], 60)
        audited_cal = json.loads(checked_command(
            [sys.executable, str(root / "stage7_calibration_audit.py"),
             "--report", str(report_path), "--sqlite", str(cal_db)], 20))
        if audited_cal.get("field_calibrated") is not False or not str(audited_cal["status"]).startswith("PASS_"):
            raise RuntimeError("Standalone laboratory characterization failed the independent audit")
        manifest["calibration"] = {"report": report_path.name, "report_sha256": sha256(report_path),
                                   "sqlite": cal_db.name, "sqlite_sha256": sha256(cal_db),
                                   "audit_status": audited_cal["status"]}

        for idx, (seed, scenario, K, policy) in enumerate(trials, start=1):
            cell = f"s{seed}_{scenario}_K{K}_{policy}"
            ledger = runs_root / f"{cell}.jsonl"
            sqlite_path = runs_root / f"{cell}.sqlite"
            fixture = fixtures_root / f"s{seed}_{scenario}"
            transport = "inproc" if pilot else "mqtt"
            checked_command([sys.executable, str(root / "stage7_controlled_replay.py"),
                             "--fixture-dir", str(fixture), "--policy", policy,
                             "--transport", transport, "--K", str(K),
                             "--iterations-per-unit", str(config["pbkdf2_iterations_per_work_unit"]),
                             "--urgent-deadline-ms", str(config["urgent_deadline_ms"]),
                             "--routine-tau-ms", str(config["routine_tau_ms"]),
                             "--sqlite-output", str(sqlite_path), "--output", str(ledger),
                             "--timeout-s", str(timeout_s)], timeout_s + 20)
            audit_command = [sys.executable, str(root / "stage7_independent_replay_audit.py"),
                             "--ledger", str(ledger), "--sqlite", str(sqlite_path),
                             "--fixture-dir", str(fixture)]
            if not pilot:
                audit_command.append("--require-mqtt")
            audited = json.loads(checked_command(audit_command, 20))
            if audited["status"] != "PASS_STAGE7_SYNTHETIC_ACCOUNTING_ONLY":
                raise RuntimeError("Independent per-run raw/SQLite audit did not PASS")
            manifest["runs"].append({
                "execution_order": idx, "seed": seed, "scenario": scenario,
                "K": K, "policy": policy,
                "fixture_dir": f"fixtures/{fixture.name}",
                "ledger": f"runs/{ledger.name}", "ledger_sha256": sha256(ledger),
                "sqlite": f"runs/{sqlite_path.name}", "sqlite_sha256": sha256(sqlite_path),
                "source_fixture_sha256": audited["source_fixture_sha256"],
                "hidden_fixture_sha256": audited["hidden_fixture_sha256"],
                "offered": audited["offered"], "committed": audited["committed"],
                "rejected": audited["rejected"], "U": audited["U_artificial_debug_only"],
                "R": audited["R_artificial_debug_only"],
                "independent_audit_status": audited["status"],
            })
            print(f"INDEPENDENTLY AUDITED {idx}/{len(trials)} {cell} "
                  f"({audited['committed']} SQLite commits)", flush=True)
    finally:
        manifest["finished_utc"] = datetime.now(timezone.utc).isoformat()
        manifest["complete"] = len(manifest["runs"]) == len(trials)
        manifest["status"] = ("COMPLETE_REQUIRES_BATCH_INDEPENDENT_AUDIT"
                              if manifest["complete"] else "INCOMPLETE_NOT_SCIENTIFIC_EVIDENCE")
        with (output_dir / "study.json").open("x", encoding="utf-8") as stream:
            json.dump(manifest, stream, indent=2, sort_keys=True)
            stream.write("\n")
    if not manifest["complete"]:
        raise RuntimeError("Held-out batch incomplete: data MUST NOT be cherry-picked")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, default=Path(__file__).with_name("stage8_frozen_protocol.json"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--mode", choices=["pilot", "holdout"], required=True)
    parser.add_argument("--pilot-seeds", nargs="+", type=int, default=[7001])
    parser.add_argument("--git-revision", default="UNCOMMITTED")
    args = parser.parse_args()
    result = run_study(config_path=args.protocol, output_dir=args.output_dir,
                       pilot=(args.mode == "pilot"), pilot_seeds=tuple(args.pilot_seeds),
                       git_revision=args.git_revision)
    print(json.dumps({"status": result["status"], "completed": len(result["runs"]),
                      "phase": result["study_phase"]}, sort_keys=True))


if __name__ == "__main__":
    main()
