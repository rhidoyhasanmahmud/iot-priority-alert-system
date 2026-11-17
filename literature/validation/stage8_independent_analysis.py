#!/usr/bin/env python3
"""Independently audit Stage 8 RAW MQTT/SQLite evidence and frozen analysis.

This module does not import the Stage 8 trial emitter or scheduling policy. It
reopens each database, reconstructs offered-population endpoints from ledger,
validates held-out protocol factors, and resamples *paired source seeds*, never
individual jobs. No field or novelty/generalization claims are made.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import sqlite3
import statistics

from stage5k2_independent_audit import audit as audit_fixture, audit_pair
from stage7_independent_replay_audit import audit_run
from stage7_calibration_audit import audit as audit_calibration


FROZEN_PROTOCOL_SHA256 = "1fe656270ce5843af8b26a6a288f712bb4afbf25a05f7d1f2ea9221e93163c52"
POLICIES = ("fifo", "strict_urgent_first", "routine_wait_guard")


class StudyAuditError(ValueError):
    pass


def check(ok: bool, message: str) -> None:
    if not ok:
        raise StudyAuditError(message)


def safe_file(root: Path, relative: str) -> Path:
    check(isinstance(relative, str) and bool(relative), "Missing relative artifact path")
    path = (root / relative).resolve()
    check(path.is_relative_to(root.resolve()) and path.is_file(), "Artifact path missing or escapes root")
    return path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for part in iter(lambda: stream.read(65536), b""):
            h.update(part)
    return h.hexdigest()


def quantile(values: list[float], p: float) -> float:
    if not values:
        raise ValueError("Cannot estimate quantile on empty evidence")
    sorted_values = sorted(values)
    pos = (len(sorted_values) - 1) * p
    low = math.floor(pos)
    high = math.ceil(pos)
    return sorted_values[low] + (pos - low) * (sorted_values[high] - sorted_values[low])


def mean_ci(paired_differences: list[float], *, seed: int, repetitions: int) -> dict:
    check(len(paired_differences) >= 2, "Too few independent seed blocks for resampling")
    rng = random.Random(seed)
    n = len(paired_differences)
    estimates = []
    for _ in range(repetitions):
        estimates.append(sum(paired_differences[rng.randrange(n)] for _ in range(n)) / n)
    return {"paired_seed_count": n, "mean": statistics.mean(paired_differences),
            "ci95_low": quantile(estimates, 0.025),
            "ci95_high": quantile(estimates, 0.975),
            "units": "ABSOLUTE_PROPORTION_POINTS_NOT_PERCENT_CHANGE",
            "method": "PAIRED_SEED_CLUSTER_PERCENTILE_BOOTSTRAP_10000_REPLICATES"}


def percentile_started_routine_wait_ms(rows: list[dict]) -> float | None:
    waits = [(x["start_ns"] - x["offer_ns"]) / 1e6 for x in rows
             if x.get("type") == "offer" and x["trusted_class"] == "ROUTINE"
             and x["terminal"] == "COMPLETED"]
    return quantile(waits, 0.95) if waits else None


def observed_arrival_diagnostics(rows: list[dict], source_fixture: Path) -> dict:
    """Quantify observed delivery differences without selecting/excluding runs."""
    offers = [row for row in rows if row.get("type") == "offer"]
    expected_ids = [json.loads(line)["event_id"] for line in
                    (source_fixture / "offers.jsonl").read_text().splitlines() if line.strip()]
    observed_ids = [row["event_id"] for row in offers]
    expected_rank = {eid: i for i, eid in enumerate(expected_ids)}
    positions = [expected_rank[eid] for eid in observed_ids]
    return {
        "observed_first_to_last_offer_span_ms":
            (offers[-1]["offer_ns"] - offers[0]["offer_ns"]) / 1e6,
        "source_order_inversions": sum(positions[i] > positions[j]
                                       for i in range(len(positions))
                                       for j in range(i + 1, len(positions))),
        "urgent_rejected": sum(row["trusted_class"] == "URGENT" and
                               row["terminal"] == "REJECTED" for row in offers),
        "routine_rejected": sum(row["trusted_class"] == "ROUTINE" and
                                row["terminal"] == "REJECTED" for row in offers),
    }


def independent_order(config: dict, seed: int, scenario: str, K: int) -> list[str]:
    material = f"stage8|{config['seed_block_order_shuffle_seed']}|{seed}|{scenario}|{K}"
    random_seed = int.from_bytes(hashlib.sha256(material.encode()).digest()[:8], "big")
    options = list(POLICIES)
    random.Random(random_seed).shuffle(options)
    return options


def expected_trials(config: dict, pilot: bool, seeds: list[int]) -> list[tuple]:
    cells = config["study_cells"][:2] if pilot else config["study_cells"]
    blocks = [(seed, cell["scenario"], cell["K"]) for seed in seeds for cell in cells]
    random.Random(config["seed_block_order_shuffle_seed"]).shuffle(blocks)
    return [(seed, scenario, K, policy) for seed, scenario, K in blocks
            for policy in independent_order(config, seed, scenario, K)]


def audit_study(root: Path, protocol_path: Path, *, pilot: bool = False) -> dict:
    check(sha256(protocol_path) == FROZEN_PROTOCOL_SHA256,
          "Frozen protocol file hash is different; no post-hoc revisions allowed")
    config = json.loads(protocol_path.read_text(encoding="utf-8"))
    check(config["protocol_id"] == "STI-2026-STAGE8-SYNTHETIC-HOLDOUT-V1"
          and config["policies"] == list(POLICIES), "Wrong frozen study/policies")
    study = json.loads((root / "study.json").read_text(encoding="utf-8"))
    check(study["protocol_sha256"] == FROZEN_PROTOCOL_SHA256 and
          study["protocol_id"] == config["protocol_id"] and study["complete"] is True and
          study["status"] == "COMPLETE_REQUIRES_BATCH_INDEPENDENT_AUDIT" and
          study["provenance"] == "ARTIFICIAL_NOT_FIELD_CALIBRATED_NOT_NOVELTY_APPROVED" and
          study["field_calibrated"] is False and study["novelty_verified"] is False,
          "Invalid status, provenance or incomplete evidence")
    expected_phase = "RESERVED_TUNING_ENGINEERING_PILOT" if pilot else "FROZEN_HELDOUT_SYNTHETIC"
    check(study["study_phase"] == expected_phase and
          study["transport"] == ("inproc" if pilot else "mqtt"),
          "Pilot/heldout or transport substitution")
    seeds = study["seeds"]
    check(type(seeds) is list and len(seeds) == len(set(seeds)), "Duplicate seed")
    if pilot:
        check(set(seeds).issubset(set(config["pilot_only_seeds"])), "Pilot seed leaks holdout")
    else:
        check(seeds == config["holdout_seeds"] and len(seeds) == 30 and
              study["head_source_revision"] != "UNCOMMITTED", "Incorrect frozen holdout seed list")
    expected = expected_trials(config, pilot, seeds)
    actual = [(x["seed"], x["scenario"], x["K"], x["policy"])
              for x in study["planned_trial_cells"]]
    check(actual == expected and study["planned_trial_count"] == len(expected),
          "Run planning/order differs from frozen seed/block/policy randomization")
    runs = study["runs"]
    check(len(runs) == len(expected) == (len(seeds) * 6 if pilot else 450),
          "Missing or duplicated experimental cells")
    cal = study.get("calibration")
    check(isinstance(cal, dict) and cal.get("audit_status", "").startswith("PASS_"),
          "Missing laboratory host calibration evidence")
    cal_report = safe_file(root, cal["report"])
    cal_sqlite = safe_file(root, cal["sqlite"])
    check(sha256(cal_report) == cal["report_sha256"] and
          sha256(cal_sqlite) == cal["sqlite_sha256"], "Calibration raw hashes changed")
    check(audit_calibration(cal_report, cal_sqlite)["field_calibrated"] is False,
          "Lab characterization incorrectly promoted to field evidence")

    fixtures: dict[tuple[int, str], Path] = {}
    for seed in seeds:
        for scenario in set(x[1] for x in expected):
            path = root / "fixtures" / f"s{seed}_{scenario}"
            info = audit_fixture(path)
            spec = config["scenarios"][scenario]
            check(info["count"] == config["source_count"] and
                  info["urgent_count"] == config["urgent_count"] and
                  info["shape"] == spec["shape"] and
                  info["work_dispersion"] == spec["dispersion"] and
                  info["planned_horizon_ns"] == spec["horizon_ns"],
                  "Predeclared synthetic scenario source/work family differs")
            fixtures[(seed, scenario)] = path
        if not pilot:
            base = fixtures[(seed, "smooth")]
            audit_pair(base, fixtures[(seed, "burst")], "burst_shape")
            audit_pair(base, fixtures[(seed, "overload")], "intensity")
            audit_pair(base, fixtures[(seed, "variable")], "work_dispersion")

    blocks: dict[tuple, dict] = {}
    for index, item in enumerate(runs, 1):
        key = (item["seed"], item["scenario"], item["K"], item["policy"])
        check(key == expected[index - 1] and item["execution_order"] == index,
              "Run missing, duplicated or reordered after freeze")
        check(item["fixture_dir"] == f"fixtures/s{item['seed']}_{item['scenario']}",
              "Run source fixture does not match registered cell")
        ledger = safe_file(root, item["ledger"])
        db = safe_file(root, item["sqlite"])
        check(sha256(ledger) == item["ledger_sha256"] and
              sha256(db) == item["sqlite_sha256"], "Raw ledger/SQLite file hash changed")
        records = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines()
                   if line.strip()]
        m = next(row for row in records if row["type"] == "manifest")
        check(m["policy_id"] == item["policy"] and m["K"] == item["K"] and
              m["synthetic_iterations_per_work_unit"] == config["pbkdf2_iterations_per_work_unit"]
              and m["urgent_deadline_offset_ns"] == int(config["urgent_deadline_ms"] * 1e6)
              and m["routine_tau_ns"] == int(config["routine_tau_ms"] * 1e6),
              "Worker/policy/threshold changed after protocol freeze")
        found = audit_run(records, db, fixtures[(item["seed"], item["scenario"])],
                          require_mqtt=not pilot)
        check(found["status"] == item["independent_audit_status"] and
              found["source_fixture_sha256"] == item["source_fixture_sha256"] and
              found["hidden_fixture_sha256"] == item["hidden_fixture_sha256"] and
              found["offered"] == item["offered"] == config["source_count"] and
              found["committed"] == item["committed"] and
              found["rejected"] == item["rejected"] and
              found["U_artificial_debug_only"] == item["U"] and
              found["R_artificial_debug_only"] == item["R"],
              "Emitter summary diverged from independent raw replay audit")
        blocks.setdefault(key[:3], {})[key[3]] = {
            "U": found["U_artificial_debug_only"],
            "R": found["R_artificial_debug_only"],
            "rejected": found["rejected"],
            "p95_routine_wait_admitted_ms": percentile_started_routine_wait_ms(records),
            **observed_arrival_diagnostics(records, fixtures[(item["seed"], item["scenario"])])
        }
    check(len(blocks) == len(seeds) * (2 if pilot else 5) and
          all(set(block) == set(POLICIES) for block in blocks.values()),
          "Missing a policy from one or more matched seed/scenario/K blocks")

    result = {
        "status": ("PASS_PILOT_NO_SCIENTIFIC_INFERENCE" if pilot else
                   "PASS_SYNTHETIC_HELDOUT_FULL_INDEPENDENT_AUDIT"),
        "protocol_id": config["protocol_id"],
        "protocol_sha256": FROZEN_PROTOCOL_SHA256,
        "field_calibrated": False, "algorithm_novelty_verified": False,
        "inference_scope": "CONDITIONAL_THIS_ARTIFICIAL_SINGLE_WORKER_MODEL_ONLY",
        "independent_source_seeds": len(seeds),
        "runs_independently_reaudited": len(runs),
        "three_policy_matched_blocks": len(blocks),
        "raw_ledger_and_sqlite_verified": True,
        "researcher_slo_approval": False,
        "secondary_exploratory": {},
    }
    if pilot:
        result["warning"] = "TUNING_SEEDS_ONLY_NO_HELDOUT_OR_MANUSCRIPT_RESULTS"
        return result

    threshold_u = config["conditional_joint_targets"]["absolute_urgent_U_max"]
    threshold_r = config["conditional_joint_targets"]["absolute_routine_R_min"]
    boot_seed = config["bootstrap_seed"]
    reps = config["bootstrap_resamples"]
    for cell_index, cell in enumerate(config["study_cells"]):
        s, K = cell["scenario"], cell["K"]
        ordered = [blocks[(seed, s, K)] for seed in seeds]
        baseline = [x["strict_urgent_first"] for x in ordered]
        guard = [x["routine_wait_guard"] for x in ordered]
        fifo = [x["fifo"] for x in ordered]
        differences = {
            "R_guard_minus_priority": [g["R"] - p["R"] for g, p in zip(guard, baseline)],
            "U_guard_minus_priority": [g["U"] - p["U"] for g, p in zip(guard, baseline)],
            "R_guard_minus_fifo": [g["R"] - f["R"] for g, f in zip(guard, fifo)],
            "U_guard_minus_fifo": [g["U"] - f["U"] for g, f in zip(guard, fifo)],
        }
        descriptive = {
            "role": cell["role"], "independent_seeds": len(seeds),
            "policy_outcomes": {
                p: {
                    "mean_U": statistics.mean(x[p]["U"] for x in ordered),
                    "mean_R": statistics.mean(x[p]["R"] for x in ordered),
                    "mean_rejected": statistics.mean(x[p]["rejected"] for x in ordered),
                    "mean_urgent_rejected": statistics.mean(x[p]["urgent_rejected"] for x in ordered),
                    "mean_routine_rejected": statistics.mean(x[p]["routine_rejected"] for x in ordered),
                    "median_observed_local_offer_span_ms": statistics.median(
                        x[p]["observed_first_to_last_offer_span_ms"] for x in ordered),
                    "total_source_order_inversions": sum(
                        x[p]["source_order_inversions"] for x in ordered),
                    "seed_cells_joint_feasible_count": sum(x[p]["U"] <= threshold_u and
                                                         x[p]["R"] >= threshold_r for x in ordered),
                    "per_run_routine_p95_ms_median_admitted_only":
                        (statistics.median(waits) if (waits := [x[p]["p95_routine_wait_admitted_ms"]
                                                               for x in ordered if x[p]["p95_routine_wait_admitted_ms"]
                                                               is not None]) else None),
                } for p in POLICIES
            },
            "paired_effects": {
                name: mean_ci(values, seed=boot_seed + cell_index * 10 + j,
                              repetitions=reps)
                for j, (name, values) in enumerate(differences.items())
            },
        }
        result["secondary_exploratory"][f"{s}_K{K}"] = descriptive

    primary = config["primary_cell"]
    selected = result["secondary_exploratory"][f"{primary['scenario']}_K{primary['K']}"]
    r_ci = selected["paired_effects"]["R_guard_minus_priority"]
    u_ci = selected["paired_effects"]["U_guard_minus_priority"]
    r_margin = config["primary_decision"]["minimum_routine_R_gain"]
    u_margin = config["primary_decision"]["maximum_allowed_urgent_U_increase"]
    result["primary_predeclared_gate"] = {
        "cell": primary, "candidate": config["primary_policy"],
        "comparator": config["primary_comparator"],
        "routine_mean_paired_gain_and_ci95": r_ci,
        "urgent_mean_paired_harm_and_ci95": u_ci,
        "predeclared_routine_gain_min": r_margin,
        "predeclared_max_urgent_harm": u_margin,
        "supported_under_model": (r_ci["ci95_low"] > r_margin and
                                  u_ci["ci95_high"] <= u_margin),
        "interpretation": "CONDITIONAL_SYNTHETIC_EMPIRICAL_GATE_ONLY_NOT_DEPLOYMENT_EFFICACY",
        "falsification_rule": "NEGATIVE_OR_INCONCLUSIVE_FINDING_REPORTED_WITHOUT_REFITTING",
    }
    result["statistical_warning"] = (
        "Percentile paired-seed bootstrap; time-correlated jobs inside a run are NOT "
        "independent units. Secondary intervals are exploratory and unadjusted. "
        "Thresholds are artificial, prior-art comparison and external validation open.")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study-dir", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, default=Path(__file__).with_name("stage8_frozen_protocol.json"))
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit_study(args.study_dir, args.protocol, pilot=args.pilot)
    if args.output:
        with args.output.open("x", encoding="utf-8") as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write("\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
