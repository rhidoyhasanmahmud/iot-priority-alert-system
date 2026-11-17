#!/usr/bin/env python3
"""Stage 9 pre-registered, synthetic-only, four-policy controlled study.

No held-out seed is opened by this script's pilot mode. The holdout requires a
nonempty frozen source revision. A failed run leaves an incomplete manifest and
may not be selectively rerun, excluded, or called scientific evidence.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
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


PROTOCOL_SHA256 = "ece4f64d62e668eafe5d3518219155ca76c3d017c00fb029fafa3d18b1f29b89"
PROTOCOL_ID = "STI-2026-STAGE9-URGENT-PUSHOUT-HELDOUT-V1"
POLICIES = ("fifo", "strict_urgent_first", "routine_wait_guard", "urgent_pushout_strict")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_protocol(path: Path) -> dict:
    if sha256(path) != PROTOCOL_SHA256:
        raise ValueError("Stage 9 protocol differs from the pre-registered SHA256")
    config = json.loads(path.read_text())
    seeds = config["holdout_seeds"]
    if (config["protocol_id"] != PROTOCOL_ID or config["experimental_runs"] != 600
            or config["policies"] != list(POLICIES) or config["transport"] != "mqtt"
            or config["field_calibrated"] is not False
            or config["candidate_novelty_verified"] is not False
            or config["source_count"] != 60 or config["urgent_count"] != 15
            or len(seeds) != 30 or len(set(seeds)) != 30
            or set(seeds) & set(config["pilot_only_seeds"])
            or min(seeds) != 220001 or max(seeds) != 220030
            or config["execution"]["per_trial_timeout_s"] != 35):
        raise ValueError("Stage 9 identities, holdout separation, or factors differ")
    return config


def command(args: list[str], timeout: int) -> str:
    completed = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    if completed.returncode:
        raise RuntimeError(f"Failed {Path(args[1]).name}: {completed.stderr[-1800:]}\n"
                           f"{completed.stdout[-1000:]}")
    return completed.stdout


def policy_order(config: dict, seed: int, scenario: str, K: int) -> list[str]:
    material = (f"stage9|{config['policy_within_block_shuffle_seed']}|"
                f"{seed}|{scenario}|{K}")
    digest = hashlib.sha256(material.encode()).digest()
    choices = list(POLICIES)
    random.Random(int.from_bytes(digest[:8], "big")).shuffle(choices)
    return choices


def plan(config: dict, *, pilot: bool, pilot_seeds: tuple[int, ...]) -> list[tuple]:
    seeds = pilot_seeds if pilot else tuple(config["holdout_seeds"])
    if pilot and (not seeds or len(set(seeds)) != len(seeds)
                  or not set(seeds).issubset(config["pilot_only_seeds"])):
        raise ValueError("Pilot seeds must be unique and within reserved pilot seeds")
    cells = config["study_cells"][:2] if pilot else config["study_cells"]
    blocks = [(seed, cell["scenario"], cell["K"]) for seed in seeds for cell in cells]
    random.Random(config["block_shuffle_seed"]).shuffle(blocks)
    return [(s, name, K, p) for s, name, K in blocks
            for p in policy_order(config, s, name, K)]


def study(config_path: Path, out: Path, *, pilot: bool, pilot_seeds: tuple[int, ...],
          git_revision: str) -> dict:
    config = load_protocol(config_path)
    if not pilot and (not git_revision or git_revision == "UNCOMMITTED"
                      or len(git_revision) < 8):
        raise ValueError("Heldout requires a pinned frozen Git commit")
    ordered = plan(config, pilot=pilot, pilot_seeds=pilot_seeds)
    if not pilot and len(ordered) != config["experimental_runs"]:
        raise ValueError("Incorrect number of planned held-out cells")
    out.mkdir(parents=True, exist_ok=False)
    (out / "fixtures").mkdir()
    (out / "runs").mkdir()
    root = Path(__file__).resolve().parent
    manifest = {
        "status": "INCOMPLETE_NOT_SCIENTIFIC_EVIDENCE", "complete": False,
        "protocol_id": PROTOCOL_ID, "protocol_sha256": PROTOCOL_SHA256,
        "study_phase": "RESERVED_TUNING_ENGINEERING_PILOT" if pilot else "FROZEN_HELDOUT_SYNTHETIC",
        "provenance": "SYNTHETIC_NOT_FIELD_CALIBRATED_PUSHOUT_PRIOR_ART",
        "field_calibrated": False, "novelty_verified": False,
        "transport": "inproc" if pilot else "mqtt",
        "head_source_revision": git_revision,
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "host": {"platform": platform.platform(), "python": platform.python_version(),
                 "sqlite": sqlite3.sqlite_version, "logical_cpu_count": os.cpu_count()},
        "seeds": list(pilot_seeds if pilot else config["holdout_seeds"]),
        "planned_trial_count": len(ordered),
        "planned_trial_cells": [{"seed": s, "scenario": n, "K": k, "policy": p}
                                for s, n, k, p in ordered],
        "calibration": None, "runs": [],
    }
    try:
        fixture_keys = sorted({(s, n) for s, n, _, _ in ordered})
        for s, n in fixture_keys:
            save_fixture(out / "fixtures" / f"s{s}_{n}", seed=s,
                         count=config["source_count"], urgent_count=config["urgent_count"],
                         **config["scenarios"][n])
        cal_report, cal_db = out / "lab_service_characterization.json", out / "lab_service_characterization.sqlite"
        command([sys.executable, str(root / "stage7_calibration_probe.py"),
                 "--seed", "917", "--repetitions", "12", "--iterations-per-unit",
                 str(config["pbkdf2_iterations_per_work_unit"]), "--output", str(cal_report),
                 "--sqlite-output", str(cal_db)], 60)
        cal_audit = json.loads(command([sys.executable, str(root / "stage7_calibration_audit.py"),
                                        "--report", str(cal_report), "--sqlite", str(cal_db)], 20))
        if cal_audit.get("field_calibrated") is not False or not cal_audit["status"].startswith("PASS_"):
            raise RuntimeError("Independent host calibration failed")
        manifest["calibration"] = {"report": cal_report.name, "report_sha256": sha256(cal_report),
                                   "sqlite": cal_db.name, "sqlite_sha256": sha256(cal_db),
                                   "audit_status": cal_audit["status"]}
        for idx, (s, n, K, policy) in enumerate(ordered, 1):
            cell = f"s{s}_{n}_K{K}_{policy}"
            fixture = out / "fixtures" / f"s{s}_{n}"
            ledger, db = out / "runs" / f"{cell}.jsonl", out / "runs" / f"{cell}.sqlite"
            candidate = policy == "urgent_pushout_strict"
            executable = "stage9_urgent_pushout.py" if candidate else "stage7_controlled_replay.py"
            args = [sys.executable, str(root / executable), "--fixture-dir", str(fixture)]
            if not candidate:
                args += ["--policy", policy]
            args += ["--transport", "inproc" if pilot else "mqtt", "--K", str(K),
                     "--iterations-per-unit", str(config["pbkdf2_iterations_per_work_unit"]),
                     "--urgent-deadline-ms", str(config["urgent_deadline_ms"]),
                     "--routine-tau-ms", str(config["routine_tau_ms"]),
                     "--sqlite-output", str(db), "--output", str(ledger),
                     "--timeout-s", str(config["execution"]["per_trial_timeout_s"])]
            command(args, config["execution"]["per_trial_timeout_s"] + 20)
            audit_script = "stage9_independent_audit.py" if candidate else "stage7_independent_replay_audit.py"
            audit_args = [sys.executable, str(root / audit_script), "--ledger", str(ledger),
                          "--sqlite", str(db), "--fixture-dir", str(fixture)]
            if not pilot:
                audit_args.append("--require-mqtt")
            audit = json.loads(command(audit_args, 20))
            expected_status = ("PASS_STAGE9_INDEPENDENT_PUSHOUT_QUEUE_AND_SQLITE_AUDIT" if candidate
                               else "PASS_STAGE7_SYNTHETIC_ACCOUNTING_ONLY")
            if audit["status"] != expected_status:
                raise RuntimeError(f"Independent audit failure: {cell}")
            manifest["runs"].append({
                "execution_order": idx, "seed": s, "scenario": n, "K": K, "policy": policy,
                "fixture_dir": f"fixtures/{fixture.name}",
                "ledger": f"runs/{ledger.name}", "ledger_sha256": sha256(ledger),
                "sqlite": f"runs/{db.name}", "sqlite_sha256": sha256(db),
                "source_fixture_sha256": audit["source_fixture_sha256"],
                "hidden_fixture_sha256": audit["hidden_fixture_sha256"],
                "offered": audit["offered"], "committed": audit["committed"],
                "rejected": audit.get("rejected", audit.get("rejected_full")),
                "cancelled_pushout": audit.get("cancelled_pushout", 0),
                "pushouts": audit.get("pushouts", 0),
                "U": audit["U"] if candidate else audit["U_artificial_debug_only"],
                "R": audit["R"] if candidate else audit["R_artificial_debug_only"],
                "independent_audit_status": audit["status"],
            })
            print(f"INDEPENDENTLY AUDITED {idx}/{len(ordered)} {cell}", flush=True)
    finally:
        manifest["finished_utc"] = datetime.now(timezone.utc).isoformat()
        manifest["complete"] = len(manifest["runs"]) == len(ordered)
        manifest["status"] = ("COMPLETE_REQUIRES_BATCH_INDEPENDENT_AUDIT" if manifest["complete"]
                              else "INCOMPLETE_NOT_SCIENTIFIC_EVIDENCE")
        with (out / "study.json").open("x", encoding="utf-8") as stream:
            json.dump(manifest, stream, indent=2, sort_keys=True)
            stream.write("\n")
    if not manifest["complete"]:
        raise RuntimeError("Incomplete study: partial observations cannot be promoted to evidence")
    return manifest


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--protocol", type=Path, default=Path(__file__).with_name("stage9_frozen_protocol.json"))
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--mode", choices=["pilot", "holdout"], required=True)
    p.add_argument("--pilot-seeds", nargs="+", type=int, default=[8008])
    p.add_argument("--git-revision", default="UNCOMMITTED")
    args = p.parse_args()
    result = study(args.protocol, args.output_dir, pilot=args.mode == "pilot",
                   pilot_seeds=tuple(args.pilot_seeds), git_revision=args.git_revision)
    print(json.dumps({"status": result["status"], "completed": len(result["runs"])}, sort_keys=True))


if __name__ == "__main__":
    main()
