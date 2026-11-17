#!/usr/bin/env python3
"""Independent Stage 9 batch raw-evidence audit and paired-seed inference.

Reopens every raw ledger/SQLite DB and synthetic fixture; never imports either
trial emitter, admission implementation, or their reported metrics. A negative
or incomplete primary result must remain visible and cannot trigger retuning.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import statistics

from stage5k2_independent_audit import audit as audit_fixture, audit_pair
from stage7_calibration_audit import audit as audit_calibration
from stage7_independent_replay_audit import audit_run as audit_baseline
from stage9_independent_audit import audit_run as audit_pushout


FROZEN_SHA256 = "ece4f64d62e668eafe5d3518219155ca76c3d017c00fb029fafa3d18b1f29b89"
PROTOCOL_ID = "STI-2026-STAGE9-URGENT-PUSHOUT-HELDOUT-V1"
POLICIES = ("fifo", "strict_urgent_first", "routine_wait_guard", "urgent_pushout_strict")


def check(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(f"STAGE9 INDEPENDENT AUDIT FAILED: {message}")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for part in iter(lambda: stream.read(65536), b""):
            h.update(part)
    return h.hexdigest()


def safe_file(root: Path, rel: str) -> Path:
    check(isinstance(rel, str) and bool(rel), "Empty artifact path")
    path = (root / rel).resolve()
    check(path.is_relative_to(root.resolve()) and path.is_file(), "Missing/escaping artifact")
    return path


def quantile(xs: list[float], p: float) -> float:
    ys = sorted(xs)
    check(bool(ys), "Quantile requires observations")
    at = (len(ys) - 1) * p
    a, b = math.floor(at), math.ceil(at)
    return ys[a] + (at - a) * (ys[b] - ys[a])


def paired_ci(values: list[float], *, seed: int, resamples: int) -> dict:
    check(len(values) >= 2, "Paired bootstrap requires multiple independent seeds")
    rng = random.Random(seed)
    n = len(values)
    samples = [sum(values[rng.randrange(n)] for _ in range(n)) / n
               for _ in range(resamples)]
    return {"paired_source_seeds": n, "mean": statistics.mean(values),
            "ci95_low": quantile(samples, 0.025),
            "ci95_high": quantile(samples, 0.975),
            "unit": "ABSOLUTE_FRACTION_DIFFERENCE_0_TO_1",
            "method": "PAIRED_SOURCE_SEED_PERCENTILE_BOOTSTRAP"}


def independent_order(config: dict, s: int, n: str, K: int) -> list[str]:
    material = f"stage9|{config['policy_within_block_shuffle_seed']}|{s}|{n}|{K}"
    options = list(POLICIES)
    random.Random(int.from_bytes(hashlib.sha256(material.encode()).digest()[:8], "big")).shuffle(options)
    return options


def independent_plan(config: dict, seeds: list[int], pilot: bool) -> list[tuple]:
    cells = config["study_cells"][:2] if pilot else config["study_cells"]
    blocks = [(s, cell["scenario"], cell["K"]) for s in seeds for cell in cells]
    random.Random(config["block_shuffle_seed"]).shuffle(blocks)
    return [(s, n, K, p) for s, n, K in blocks
            for p in independent_order(config, s, n, K)]


def observed_offers(rows: list[dict], fixture: Path) -> dict:
    offers = [x for x in rows if x.get("type") == "offer"]
    source = [json.loads(x)["event_id"] for x in (fixture / "offers.jsonl").read_text().splitlines()
              if x.strip()]
    rank = {x: idx for idx, x in enumerate(source)}
    observed = [rank[x["event_id"]] for x in offers]
    return {
        "urgent_rejected": sum(x["trusted_class"] == "URGENT" and
                               x["terminal"] == "REJECTED" for x in offers),
        "routine_rejected": sum(x["trusted_class"] == "ROUTINE" and
                                x["terminal"] == "REJECTED" for x in offers),
        "routine_cancelled": sum(x["trusted_class"] == "ROUTINE" and
                                 x["terminal"] == "CANCELLED" for x in offers),
        "urgent_late_completed": sum(x["trusted_class"] == "URGENT" and
                                     x["terminal"] == "COMPLETED" and
                                     x["complete_ns"] > x["urgent_deadline_ns"] for x in offers),
        "offer_span_ms": (offers[-1]["offer_ns"] - offers[0]["offer_ns"]) / 1e6,
        "observed_source_order_inversions": sum(observed[i] > observed[j]
                                                 for i in range(len(observed))
                                                 for j in range(i + 1, len(observed))),
    }


def audit_study(root: Path, protocol_path: Path, *, pilot: bool) -> dict:
    check(sha256(protocol_path) == FROZEN_SHA256, "Immutable protocol hash mismatch")
    config = json.loads(protocol_path.read_text(encoding="utf-8"))
    check(config["protocol_id"] == PROTOCOL_ID and config["policies"] == list(POLICIES)
          and config["field_calibrated"] is False and config["candidate_novelty_verified"] is False,
          "Protocol identities, scope, or policies changed")
    raw = json.loads((root / "study.json").read_text(encoding="utf-8"))
    check(raw["protocol_id"] == PROTOCOL_ID and raw["protocol_sha256"] == FROZEN_SHA256
          and raw["complete"] is True
          and raw["status"] == "COMPLETE_REQUIRES_BATCH_INDEPENDENT_AUDIT"
          and raw["field_calibrated"] is False and raw["novelty_verified"] is False
          and raw["provenance"] == "SYNTHETIC_NOT_FIELD_CALIBRATED_PUSHOUT_PRIOR_ART",
          "Incomplete status, changed provenance, or mutated study")
    check(raw["study_phase"] == ("RESERVED_TUNING_ENGINEERING_PILOT" if pilot else
                                 "FROZEN_HELDOUT_SYNTHETIC") and
          raw["transport"] == ("inproc" if pilot else "mqtt"),
          "Pilot, heldout, or transport label substitution")
    seeds = raw["seeds"]
    check(isinstance(seeds, list) and len(seeds) == len(set(seeds)), "Duplicate seeds")
    if pilot:
        check(bool(seeds) and set(seeds).issubset(set(config["pilot_only_seeds"])),
              "Pilot used a heldout seed")
    else:
        check(seeds == config["holdout_seeds"] and len(seeds) == 30 and
              len(raw["head_source_revision"]) >= 8 and
              raw["head_source_revision"] != "UNCOMMITTED",
              "Heldout seed list, source freeze revision, or count changed")
    expected = independent_plan(config, seeds, pilot)
    check([(x["seed"], x["scenario"], x["K"], x["policy"])
           for x in raw["planned_trial_cells"]] == expected
          and raw["planned_trial_count"] == len(expected)
          and len(raw["runs"]) == len(expected)
          and len(expected) == len(seeds) * (8 if pilot else 20),
          "Missing/extra/reordered planned or actual trials")
    cal = raw["calibration"]
    check(cal is not None and cal["audit_status"].startswith("PASS_"),
          "Missing laboratory host characterization")
    cp, cd = safe_file(root, cal["report"]), safe_file(root, cal["sqlite"])
    check(sha256(cp) == cal["report_sha256"] and sha256(cd) == cal["sqlite_sha256"]
          and audit_calibration(cp, cd)["field_calibrated"] is False,
          "Laboratory characterization not independently replicated")

    fixtures = {}
    scenarios = {n for _, n, _, _ in expected}
    for s in seeds:
        for name in scenarios:
            fp = root / "fixtures" / f"s{s}_{name}"
            f = audit_fixture(fp)
            spec = config["scenarios"][name]
            check(f["count"] == 60 and f["urgent_count"] == 15 and
                  f["shape"] == spec["shape"] and
                  f["work_dispersion"] == spec["dispersion"] and
                  f["planned_horizon_ns"] == spec["horizon_ns"],
                  "Wrong or altered source fixture scenario")
            fixtures[(s, name)] = fp
        if not pilot:
            base = fixtures[(s, "smooth")]
            for target, relation in [("burst", "burst_shape"),
                                     ("overload", "intensity"),
                                     ("variable", "work_dispersion")]:
                audit_pair(base, fixtures[(s, target)], relation)

    blocks: dict[tuple, dict] = {}
    for idx, item in enumerate(raw["runs"], 1):
        s, name, K, policy = expected[idx - 1]
        check((item["seed"], item["scenario"], item["K"], item["policy"]) ==
              (s, name, K, policy) and item["execution_order"] == idx and
              item["fixture_dir"] == f"fixtures/s{s}_{name}",
              "Reordered, swapped, or relabelled run")
        lp, dp = safe_file(root, item["ledger"]), safe_file(root, item["sqlite"])
        check(sha256(lp) == item["ledger_sha256"] and sha256(dp) == item["sqlite_sha256"],
              "Ledger/SQLite changed after original manifest")
        rows = [json.loads(x) for x in lp.read_text().splitlines() if x.strip()]
        man = next(x for x in rows if x["type"] == "manifest")
        check(man["policy_id"] == policy and man["K"] == K and
              man["synthetic_iterations_per_work_unit"] == config["pbkdf2_iterations_per_work_unit"]
              and man["urgent_deadline_offset_ns"] == int(config["urgent_deadline_ms"] * 1e6)
              and man["routine_tau_ns"] == int(config["routine_tau_ms"] * 1e6),
              "Policy, capacity, CPU work, deadline, or routine criterion changed")
        candidate = policy == "urgent_pushout_strict"
        audited = (audit_pushout if candidate else audit_baseline)(
            rows, dp, fixtures[(s, name)], require_mqtt=not pilot)
        check(audited["status"] == item["independent_audit_status"] ==
              ("PASS_STAGE9_INDEPENDENT_PUSHOUT_QUEUE_AND_SQLITE_AUDIT" if candidate else
               "PASS_STAGE7_SYNTHETIC_ACCOUNTING_ONLY"), "Per-run auditor mismatch")
        U = audited["U"] if candidate else audited["U_artificial_debug_only"]
        R = audited["R"] if candidate else audited["R_artificial_debug_only"]
        rejected = audited.get("rejected", audited.get("rejected_full"))
        cancelled = audited.get("cancelled_pushout", 0)
        check(audited["source_fixture_sha256"] == item["source_fixture_sha256"] and
              audited["hidden_fixture_sha256"] == item["hidden_fixture_sha256"] and
              audited["offered"] == item["offered"] == 60 and
              audited["committed"] == item["committed"] and
              rejected == item["rejected"] and cancelled == item["cancelled_pushout"] and
              audited.get("pushouts", 0) == item["pushouts"] and
              U == item["U"] and R == item["R"],
              "Manifest summary disagrees with independent raw replay")
        blocks.setdefault((s, name, K), {})[policy] = {
            "U": U, "R": R, "rejected": rejected, "cancelled": cancelled,
            "committed": audited["committed"], **observed_offers(rows, fixtures[(s, name)])}
    check(len(blocks) == len(seeds) * (2 if pilot else 5) and
          all(set(x) == set(POLICIES) for x in blocks.values()),
          "Missing a policy in matched-seed/scenario blocks")
    result = {
        "status": "PASS_PILOT_NO_SCIENTIFIC_INFERENCE" if pilot else
                  "PASS_SYNTHETIC_HELDOUT_FULL_INDEPENDENT_AUDIT",
        "protocol_sha256": FROZEN_SHA256, "protocol_id": PROTOCOL_ID,
        "field_calibrated": False, "algorithm_novelty_verified": False,
        "source_seeds": len(seeds), "raw_runs_reaudited": len(raw["runs"]),
        "four_policy_matched_blocks": len(blocks),
        "scope": "ONE_ARTIFICIAL_SINGLE_WORKER_MQTT_SQLITE_MODEL_WITH_ADMISSION_CHANGE",
        "candidate_alters_admission_not_only_dispatch": True,
    }
    if pilot:
        result["warning"] = "RESERVED_TUNING_ONLY_NOT_HELDOUT_EVIDENCE"
        return result

    results = {}
    for index, cell in enumerate(config["study_cells"]):
        name, K = cell["scenario"], cell["K"]
        observations = [blocks[(s, name, K)] for s in seeds]
        comparisons = {
            "U_fifo_minus_pushout": [x["fifo"]["U"] - x["urgent_pushout_strict"]["U"]
                                      for x in observations],
            "U_priority_minus_pushout": [x["strict_urgent_first"]["U"] -
                                         x["urgent_pushout_strict"]["U"] for x in observations],
            "R_pushout_minus_priority": [x["urgent_pushout_strict"]["R"] -
                                         x["strict_urgent_first"]["R"] for x in observations],
            "R_pushout_minus_fifo": [x["urgent_pushout_strict"]["R"] -
                                     x["fifo"]["R"] for x in observations],
        }
        results[f"{name}_K{K}"] = {
            "role": cell["role"],
            "policies": {
                p: {"mean_U": statistics.mean(x[p]["U"] for x in observations),
                    "mean_R": statistics.mean(x[p]["R"] for x in observations),
                    "mean_rejected": statistics.mean(x[p]["rejected"] for x in observations),
                    "mean_pushout_cancelled": statistics.mean(x[p]["cancelled"] for x in observations),
                    "mean_urgent_rejected": statistics.mean(x[p]["urgent_rejected"] for x in observations),
                    "mean_routine_rejected": statistics.mean(x[p]["routine_rejected"] for x in observations),
                    "mean_urgent_late_completed": statistics.mean(x[p]["urgent_late_completed"]
                                                                  for x in observations),
                    "median_observed_offer_span_ms": statistics.median(x[p]["offer_span_ms"]
                                                                        for x in observations),
                    "source_order_inversions_total": sum(x[p]["observed_source_order_inversions"]
                                                         for x in observations)} for p in POLICIES},
            "paired_effects": {
                n: paired_ci(xs, seed=config["bootstrap_seed"] + index * 100 + j,
                             resamples=config["bootstrap_resamples"])
                for j, (n, xs) in enumerate(comparisons.items())},
        }
    result["cells"] = results
    primary = results["burst_K3"]["paired_effects"]
    f = primary["U_fifo_minus_pushout"]
    p = primary["U_priority_minus_pushout"]
    r = primary["R_pushout_minus_priority"]
    targets = config["primary_decision"]
    individual = {
        "better_than_FIFO_U_by_over_5pp_CI":
            f["ci95_low"] > targets["candidate_vs_fifo_U_improvement_min"],
        "better_than_Urgent_First_U_by_over_5pp_CI":
            p["ci95_low"] > targets["candidate_vs_priority_U_improvement_min"],
        "Routine_R_noninferior_to_Urgent_First_10pp_CI":
            r["ci95_low"] > -targets["candidate_vs_priority_R_noninferiority_margin"],
    }
    result["predeclared_primary_intersection_gate"] = {
        "primary_cell": {"scenario": "burst", "K": 3},
        "component_decisions": individual,
        "supported_under_artificial_model": all(individual.values()),
        "U_FIFO_minus_candidate": f,
        "U_Urgent_First_minus_candidate": p,
        "R_candidate_minus_Urgent_First": r,
        "interpretation": "SYNTHETIC_PREDECLARED_GATE_ONLY_NOT_REAL_IOT_OR_NOVELTY",
        "negative_or_inconclusive_finding_must_be_retained": True,
    }
    result["statistical_warning"] = (
        "Seed-paired percentile bootstrap treats the 30 source seeds as independent units, "
        "not the 60 within-run offers; secondary comparisons are exploratory and unadjusted. "
        "Observed per-policy MQTT arrival jitter and source-order inversions are disclosed. "
        "The candidate changes admission, preemption remains disabled, and cancellations "
        "remain denominator failures. Investigator deadlines and noninferiority margin lack "
        "field validation/owner approval; prior-art novelty is not established.")
    return result


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--study-dir", type=Path, required=True)
    p.add_argument("--protocol", type=Path, default=Path(__file__).with_name("stage9_frozen_protocol.json"))
    p.add_argument("--pilot", action="store_true")
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    result = audit_study(args.study_dir, args.protocol, pilot=args.pilot)
    if args.output:
        with args.output.open("x", encoding="utf-8") as out:
            json.dump(result, out, indent=2, sort_keys=True)
            out.write("\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
