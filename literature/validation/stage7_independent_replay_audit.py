#!/usr/bin/env python3
"""Fail-closed independent Stage 7 *fictional* replay and SQLite evidence gate.

Does not import the Stage 7 emitter or live scheduling implementation.
Validates the full offered population, per-ID hidden work pairing, conventional
policy decisions, clock/lifecycle ordering, and actual exported SQLite rows.
Not a validator of real-world workload/SLA representativeness or novelty.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sqlite3

from stage5d_lifecycle_audit import audit as lifecycle_audit, require
from stage5k2_independent_audit import audit as fixture_audit


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def independent_source(offer: dict) -> dict:
    eid = offer["event_id"]
    dev = hashlib.sha256(("stage7|" + eid + "|device").encode()).digest()[0] % 16
    battery = hashlib.sha256(("stage7|" + eid + "|battery").encode()).digest()[0] % 101
    urgent = offer["trusted_class"] == "urgent"
    return {"event_id": eid, "device_id": f"device_{dev:02d}",
            "kind": "tamper" if urgent else "health", "tamper": urgent,
            "battery_pct": battery}


def audit_run(rows: list[dict], sqlite_path: Path, fixture_dir: Path,
              *, require_mqtt: bool = False) -> dict:
    data = fixture_audit(fixture_dir)
    original_offers, hidden = data["offers"], data["hidden"]
    fixture_manifest = json.loads((fixture_dir / "manifest.json").read_text())
    base = lifecycle_audit(rows)
    m = next(item for item in rows if item["type"] == "manifest")
    policy = m["policy_id"]
    require(policy in {"fifo", "strict_urgent_first"}, "Only conventional candidate baselines allowed")
    transport = m.get("scenario_id", "").removeprefix("stage7_exploratory_")
    require(transport in {"mqtt", "inproc"}, "Unsupported or undeclared transport")
    if require_mqtt:
        require(transport == "mqtt", "Inproc ledger cannot establish MQTT execution")
    require(m.get("study_status") == "ENGINEERING_PILOT_UNREGISTERED_NOT_SCIENTIFIC_RESULTS",
            "Missing unregistered-synthetic warning")
    require(m.get("work_model") == "PBKDF2_SHA256_ILLUSTRATIVE_CPU_PLUS_SQLITE_WAL_FULL",
            "Unexpected simulated CPU/SQLite model")
    scale = m.get("synthetic_iterations_per_work_unit")
    require(type(scale) is int and 1 <= scale <= 1_000_000, "Invalid work-unit CPU conversion")
    require(m.get("offer_fixture_sha256") == fixture_manifest["offer_sha256"] and
            m.get("hidden_work_sha256") == fixture_manifest["hidden_work_sha256"] and
            m.get("fixture_id") == fixture_manifest["fixture_id"],
            "Fixture identity/hashes differ from separately supplied source")
    require(m.get("planned_source_horizon_ns") == original_offers[-1]["planned_offer_offset_ns"] -
            original_offers[0]["planned_offer_offset_ns"], "Declared source horizon changed")
    require(m.get("urgent_deadline_offset_ns", 0) > 0 and m.get("routine_tau_ns", 0) > 0,
            "Missing artificial timing limits")
    require(m.get("completion_boundary") == "post_SQLite_commit_return" and
            m.get("worker_handler") == "STAGE7_ARTIFICIAL_CPU_PLUS_STAGE5G_SQLITE",
            "Wrong completion handler/boundary")
    require(m.get("db_reopen_exact") is True and m.get("receiver_capture_complete") is True,
            "Incomplete receiver or database proof")
    require(m.get("publisher_log_complete") is True, "Incomplete publisher list")

    expected_source = [independent_source(item) for item in original_offers]
    offsets = [item["planned_offer_offset_ns"] for item in original_offers]
    gaps = [offsets[0], *(b - a for a, b in zip(offsets, offsets[1:]))]
    require(m.get("source_sha256") == hashlib.sha256(canonical(expected_source).encode()).hexdigest(),
            "Source payload hash differs from independent reconstruction")
    require(m.get("schedule_sha256") == hashlib.sha256(canonical(gaps).encode()).hexdigest(),
            "Source gap hash differs from independent reconstruction")
    require(m.get("planned_unique") == len(original_offers) == base["offered_unique"] ==
            base["published_unique"], "Offered/published/fixture cardinality mismatch")
    require(base["published_ids_without_callback"] == 0 and base["unresolved_offers"] == 0,
            "Unobserved or unfinished offers")
    require(base["delivery_attempts"] >= len(original_offers) + len(original_offers)//13 + 1,
            "Expected duplicate/invalid probes absent")
    require(base["duplicates"] >= len(original_offers)//13 and base["invalid_attempts"] >= 1,
            "Duplicate/malformed handling not observed")

    source_by_id = {s["event_id"]: s for s in expected_source}
    hidden_by_id = {w["event_id"]: w["synthetic_required_work_units"] for w in hidden}
    published = [item for item in rows if item["type"] == "published"]
    actual_offers = [item for item in rows if item["type"] == "offer"]
    require([item["event_id"] for item in published] == [item["event_id"] for item in expected_source],
            "Actual published order differs from predeclared fixture")
    require(all(item.get("source") == source_by_id[item["event_id"]] for item in published),
            "Published message changed")
    require({item["event_id"] for item in actual_offers} == set(source_by_id),
            "Offer population missing or invented IDs")

    admitted = [item for item in actual_offers if item["terminal"] == "COMPLETED"]
    expected_db = {}
    for offer in actual_offers:
        eid = offer["event_id"]
        src = source_by_id[eid]
        require(offer.get("validated_source") == src, "Offered payload differs from signed fixture")
        cls = "URGENT" if src["tamper"] else "ROUTINE"
        require(offer["trusted_class"] == cls, "Trusted class differs from source")
        if offer["terminal"] == "REJECTED":
            for key in ("synthetic_work_units_post_dispatch", "synthetic_cpu_iterations",
                        "synthetic_cpu_service_ns", "db_handler_start_ns", "db_commit_return_ns",
                        "db_service_ns", "db_committed", "db_rule_result", "db_result_json",
                        "dispatch_snapshot", "dispatch_choice_ns"):
                require(offer.get(key) is None, f"Rejected {eid} reports hidden work/dispatch/commit")
            continue

        units = hidden_by_id[eid]
        require(offer.get("synthetic_work_units_post_dispatch") == units and
                offer.get("synthetic_cpu_iterations") == units * scale,
                "Completed job work does not match independently paired hidden work")
        duration = offer.get("synthetic_cpu_service_ns")
        require(type(duration) is int and duration > 0, "Missing measured artificial CPU span")
        start, handler, commit, complete = [offer.get(key) for key in
                                            ("start_ns", "db_handler_start_ns", "db_commit_return_ns", "complete_ns")]
        require(all(type(t) is int for t in (start, handler, commit, complete)) and
                start + duration <= handler <= commit <= complete,
                "Artificial CPU/SQLite service ordering impossible")
        require(offer.get("db_service_ns") == commit - handler and offer.get("db_committed") is True,
                "SQLite commit span or success fabricated")
        device = int(src["device_id"].split("_")[1])
        rule = (("TAMPER_DISABLED" if device % 5 == 0 else "TAMPER_REVIEW")
                if src["tamper"] else ("LOW_BATTERY" if src["battery_pct"] < 20 else "HEALTHY"))
        result_json = canonical({"event_id": eid, "zone": f"zone_{device % 4}", "rule": rule})
        require(offer.get("db_rule_result") == rule and offer.get("db_result_json") == result_json,
                "Incorrect deterministic SQL context/rule/result")
        expected_db[eid] = (src["device_id"], cls, rule, result_json)

        decision = offer.get("dispatch_reason")
        decision_ns = offer.get("dispatch_choice_ns")
        snapshot = offer.get("dispatch_snapshot")
        require(decision in {"direct_admission", "queued_policy_selection"} and
                type(decision_ns) is int and offer["offer_ns"] <= decision_ns <= start and
                isinstance(snapshot, list), "Invalid online dispatch decision record")
        if decision == "direct_admission":
            require(snapshot == [], "Direct admission must not inspect a waiting queue")
        else:
            waiting = sorted((item for item in admitted if
                              item["offer_ns"] <= decision_ns <= item["start_ns"]),
                             key=lambda item: item["offer_ns"])
            expected_snapshot = [{"event_id": item["event_id"],
                                  "trusted_class": item["trusted_class"]} for item in waiting]
            require(snapshot == expected_snapshot, "Decision snapshot differs from actual waiting jobs")
            chosen = (snapshot[0] if policy == "fifo" else
                      next((item for item in snapshot if item["trusted_class"] == "URGENT"),
                           snapshot[0]))
            require(chosen["event_id"] == eid, "Policy choice was not FIFO/strict urgent-first")

    require(len(expected_db) == base["admitted"] == m.get("db_rows_reopened"),
            "Reopened database admission count differs")
    require(sqlite_path.is_file(), "Separate SQLite backup is required")
    digest = hashlib.sha256(sqlite_path.read_bytes()).hexdigest()
    require(digest == m.get("sqlite_backup_sha256"), "SQLite backup hash mismatch")
    con = sqlite3.connect(sqlite_path.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        require(con.execute("PRAGMA integrity_check").fetchone()[0] == "ok",
                "SQLite integrity check failed")
        require(con.execute("SELECT COUNT(*) FROM device_context").fetchone()[0] == 16,
                "Unexpected device-context table")
        rows_db = {row[0]: tuple(row[1:]) for row in con.execute(
            "SELECT event_id, device_id, trusted_class, rule_result, result_json FROM handled_alerts")}
    finally:
        con.close()
    require(rows_db == expected_db, "SQLite persisted contents differ from independently rebuilt ledger")
    return {"status": "PASS_STAGE7_SYNTHETIC_ACCOUNTING_ONLY", "policy": policy,
            "transport": transport, "offered": base["offered_unique"],
            "committed": base["admitted"], "rejected": base["rejected"],
            "U_artificial_debug_only": base["urgent_failure_U_bounds"]["exact"],
            "R_artificial_debug_only": base["routine_timely_start_R_bounds"]["exact"],
            "source_fixture_sha256": fixture_manifest["offer_sha256"],
            "hidden_fixture_sha256": fixture_manifest["hidden_work_sha256"]}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ledger", type=Path, required=True)
    p.add_argument("--sqlite", type=Path, required=True)
    p.add_argument("--fixture-dir", type=Path, required=True)
    p.add_argument("--require-mqtt", action="store_true")
    args = p.parse_args()
    rows = [json.loads(line) for line in args.ledger.read_text().splitlines() if line.strip()]
    print(json.dumps(audit_run(rows, args.sqlite, args.fixture_dir, require_mqtt=args.require_mqtt),
                     sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
