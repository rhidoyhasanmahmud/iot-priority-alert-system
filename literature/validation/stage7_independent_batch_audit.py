#!/usr/bin/env python3
"""Re-audit every raw artifact and pairing in an exploratory synthetic batch.

The raw fixture/SQLite/ledger are inputs. The original emitter's reported
per-run counts or effect sizes are NEVER accepted without recomputation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import statistics

from stage7_calibration_audit import audit as audit_calibration
from stage7_independent_replay_audit import audit_run
from stage5k2_independent_audit import audit as audit_fixture, audit_pair


class BatchAuditError(ValueError):
    pass


def check(value: bool, reason: str) -> None:
    if not value:
        raise BatchAuditError(reason)


def safe_path(root: Path, relative: str) -> Path:
    check(isinstance(relative, str), "Missing path")
    path = (root / relative).resolve()
    check(path.is_relative_to(root.resolve()), "Evidence path escapes batch root")
    return path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit_batch(root: Path, *, require_mqtt: bool = False) -> dict:
    batch = json.loads((root / "batch.json").read_text(encoding="utf-8"))
    check(batch.get("status") == "EXPLORATORY_SYNTHETIC_ENGINEERING_ONLY_NOT_PREREGISTERED"
          and batch.get("field_calibrated") is False
          and batch.get("research_protocol_approved") is False
          and batch.get("novel_policy_verified") is False
          and batch.get("scientific_conclusion_allowed") is False,
          "Batch makes an unapproved scientific/generalization claim")
    check(batch.get("complete") is True, "Batch did not finish all trials")
    transport = batch.get("transport")
    check(transport in {"inproc", "mqtt"}, "Unknown transport")
    if require_mqtt:
        check(transport == "mqtt", "Inprocess evidence cannot satisfy real MQTT gate")
    policies = batch.get("policies")
    seeds = batch.get("seeds")
    capacities = batch.get("capacity_K")
    scenarios = batch.get("scenario_contract")
    check(policies == ["fifo", "strict_urgent_first"], "Wrong conventional policy set")
    check(isinstance(seeds, list) and len(seeds) >= 2 and len(set(seeds)) == len(seeds),
          "Bad seed population")
    check(isinstance(capacities, list) and len(capacities) > 0 and
          len(set(capacities)) == len(capacities), "Bad K levels")
    check(set(scenarios) == {"smooth", "burst", "intense", "variable"},
          "Missing paired-factor scenarios")
    count = batch["events_per_run"]
    scale = batch["work_units_to_pbkdf2_iterations"]
    check(count >= 20 and count % 4 == 0 and type(scale) is int and scale > 0,
          "Invalid candidate work model")
    check(batch.get("debug_targets_status") == "ARTIFICIAL_NOT_OWNER_APPROVED" and
          batch.get("debug_urgent_deadline_ms") == 20.0 and
          batch.get("debug_routine_tau_ms") == 20.0,
          "Artificial thresholds were redefined after trial")
    cal = safe_path(root, batch["calibration_report"])
    cal_db = safe_path(root, batch["calibration_sqlite"])
    check(sha256(cal) == batch["calibration_sha256"] and
          sha256(cal_db) == batch["calibration_sqlite_sha256"],
          "Raw lab characterization hashes differ")
    check(audit_calibration(cal, cal_db)["field_calibrated"] is False,
          "Lab profile improperly promoted to field calibration")
    check(json.loads(cal.read_text())["iterations_per_unit"] == scale,
          "Trial work model differs from calibration probe")

    fixture_paths = {}
    for seed in seeds:
        for scenario in scenarios:
            fixture = root / "fixtures" / f"seed{seed}_{scenario}"
            audited = audit_fixture(fixture)
            check(audited["count"] == count, "Wrong offered IDs in fixture")
            fixture_paths[(seed, scenario)] = fixture
        base = fixture_paths[(seed, "smooth")]
        audit_pair(base, fixture_paths[(seed, "burst")], "burst_shape")
        audit_pair(base, fixture_paths[(seed, "intense")], "intensity")
        audit_pair(base, fixture_paths[(seed, "variable")], "work_dispersion")

    runs = batch.get("runs")
    expected = len(seeds) * len(capacities) * len(scenarios) * len(policies)
    check(isinstance(runs, list) and len(runs) == batch.get("expected_run_count") == expected,
          "Run population incomplete")
    seen = set()
    blocks: dict[tuple, dict] = {}
    for row in runs:
        key = (row["seed"], row["K"], row["scenario"], row["policy"])
        check(key not in seen and key[0] in seeds and key[1] in capacities and
              key[2] in scenarios and key[3] in policies,
              "Duplicate/missing/unplanned run design cell")
        seen.add(key)
        check(row.get("fixture_dir") == f"fixtures/seed{row['seed']}_{row['scenario']}",
              "Wrong source pairing path")
        ledger = safe_path(root, row["ledger_path"])
        db = safe_path(root, row["sqlite_path"])
        check(sha256(ledger) == row["ledger_sha256"] and
              sha256(db) == row["sqlite_sha256"], "Raw artifact hash differs")
        records = [json.loads(line) for line in ledger.read_text().splitlines() if line.strip()]
        manifest = next(item for item in records if item["type"] == "manifest")
        check(manifest.get("synthetic_iterations_per_work_unit") == scale and
              manifest.get("K") == row["K"] and manifest.get("policy_id") == row["policy"],
              "Worker model/policy/K differs from predeclared cell")
        audited = audit_run(records, db, fixture_paths[(row["seed"], row["scenario"])],
                            require_mqtt=require_mqtt)
        check(audited["status"] == row.get("independent_gate") and
              audited["offered"] == row.get("offered") == count and
              audited["committed"] == row.get("committed") and
              audited["rejected"] == row.get("rejected") and
              audited["U_artificial_debug_only"] == row.get("U_debug") and
              audited["R_artificial_debug_only"] == row.get("R_debug") and
              audited["source_fixture_sha256"] == row.get("source_fixture_sha256") and
              audited["hidden_fixture_sha256"] == row.get("hidden_fixture_sha256"),
              "Emitter claimed counts/fractions differ from independent reconstruction")
        blocks.setdefault(key[:3], {})[key[3]] = audited
    check(len(seen) == expected and all(set(x) == set(policies) for x in blocks.values()),
          "One conventional policy missing in matched seed/K/scenario block")

    descriptive = {}
    for scenario in scenarios:
        effects_u, effects_r = [], []
        for (seed, K, key_scenario), block in blocks.items():
            if key_scenario != scenario:
                continue
            baseline, candidate = block["fifo"], block["strict_urgent_first"]
            effects_u.append(candidate["U_artificial_debug_only"] - baseline["U_artificial_debug_only"])
            effects_r.append(candidate["R_artificial_debug_only"] - baseline["R_artificial_debug_only"])
        descriptive[scenario] = {
            "paired_blocks_including_K_and_seed": len(effects_u),
            "U_difference_priority_minus_fifo_median_debug": statistics.median(effects_u),
            "R_difference_priority_minus_fifo_median_debug": statistics.median(effects_r),
        }
    return {
        "status": "PASS_EXPLORATORY_SYNTHETIC_BATCH_RAW_EVIDENCE_ONLY",
        "transport": transport, "independent_seeds": len(seeds),
        "trials_independently_audited": len(runs),
        "policy_pairs": len(blocks), "all_scenarios": sorted(scenarios),
        "field_calibrated": False, "scientific_inference_allowed": False,
        "effects": descriptive, "effect_warning": "DESCRIPTIVE DEBUG; NO SIGNED PROTOCOL / NO INFERENCE",
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--batch-dir", type=Path, required=True)
    p.add_argument("--require-mqtt", action="store_true")
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    result = audit_batch(args.batch_dir, require_mqtt=args.require_mqtt)
    if args.output:
        with args.output.open("x", encoding="utf-8") as f:
            json.dump(result, f, indent=2, sort_keys=True)
            f.write("\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
