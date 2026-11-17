#!/usr/bin/env python3
"""Independent raw event/queue/SQLite auditor for Stage 9 urgent push-out.

Does not import or trust the Stage 9 publisher, queue implementation, or its
reported metrics. Reconstructs admission and service transitions from timestamps
and the fixed source/hidden-work fixtures. This is laboratory evidence only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sqlite3

from stage5d_lifecycle_audit import require
from stage5k2_independent_audit import audit as audit_fixture


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def independent_source(offer: dict) -> dict:
    eid = offer["event_id"]
    device = hashlib.sha256(f"stage7|{eid}|device".encode()).digest()[0] % 16
    battery = hashlib.sha256(f"stage7|{eid}|battery".encode()).digest()[0] % 101
    urgent = offer["trusted_class"] == "urgent"
    return {"event_id": eid, "device_id": f"device_{device:02d}",
            "kind": "tamper" if urgent else "health", "tamper": urgent,
            "battery_pct": battery}


def audit_run(records: list[dict], sqlite_path: Path, fixture_dir: Path,
              *, require_mqtt: bool = False) -> dict:
    fixture = audit_fixture(fixture_dir)
    manifest_file = json.loads((fixture_dir / "manifest.json").read_text())
    require(len([x for x in records if x.get("type") == "manifest"]) == 1,
            "Exactly one manifest is required")
    m = next(x for x in records if x.get("type") == "manifest")
    require(m["policy_id"] == "urgent_pushout_strict" and
            m["admission_rule"] == "FULL_URGENT_REPLACES_NEWEST_WAITING_ROUTINE_NONPREEMPTIVE"
            and m["dispatch_rule"] == "STRICT_URGENT_FIRST_ON_WAITING_QUEUE"
            and m["admission_changes_vs_baselines"] is True,
            "Undeclared or altered admission/dispatch policy")
    require(m["study_status"] == "STAGE9_ARTIFICIAL_CANDIDATE_NO_NOVELTY_OR_FIELD_CLAIM"
            and m["work_model"] == "PBKDF2_SHA256_ILLUSTRATIVE_CPU_PLUS_SQLITE_WAL_FULL"
            and m["completion_boundary"] == "post_SQLite_commit_return",
            "Missing artificial provenance or completion semantics")
    transport = m["scenario_id"].removeprefix("stage9_synthetic_")
    require(transport in {"inproc", "mqtt"} and (not require_mqtt or transport == "mqtt"),
            "Invalid or substituted transport")
    require(m["trace_provenance"] == "STAGE5K2_FICTIONAL_UNAPPROVED_" + fixture["shape"],
            "Wrong synthetic scenario provenance")
    for f, h in [("offer_fixture_sha256", "offer_sha256"),
                 ("hidden_work_sha256", "hidden_work_sha256"),
                 ("fixture_id", "fixture_id")]:
        require(m[f] == manifest_file[h], "Fixture/provenance mismatch: " + f)
    scale = m["synthetic_iterations_per_work_unit"]
    require(type(scale) is int and 1 <= scale <= 1_000_000, "Invalid CPU work scale")
    K, tau, deadline_offset = m["K"], m["routine_tau_ns"], m["urgent_deadline_offset_ns"]
    require(type(K) is int and 0 <= K <= 100 and type(tau) is int and tau > 0
            and type(deadline_offset) is int and deadline_offset > 0,
            "Invalid queue capacity or artificial bounds")
    cutoff = m["observation_end_ns"]
    require(type(cutoff) is int and cutoff > 0 and m["clock_domain"] ==
            "single_gateway_process_monotonic_ns" and m["dedup_cache_reset"] is True,
            "Missing local clock or reset guarantee")
    require(m["publisher_log_complete"] is True and
            m["receiver_capture_complete"] is True and m["db_reopen_exact"] is True,
            "Incomplete producer/receiver/SQLite evidence")
    expected_sources = [independent_source(offer) for offer in fixture["offers"]]
    expected_source_by_id = {x["event_id"]: x for x in expected_sources}
    expected_hidden_by_id = {x["event_id"]: x["synthetic_required_work_units"]
                             for x in fixture["hidden"]}
    offsets = [x["planned_offer_offset_ns"] for x in fixture["offers"]]
    gaps = [offsets[0], *(b-a for a,b in zip(offsets, offsets[1:]))]
    require(m["source_sha256"] == hashlib.sha256(canonical(expected_sources).encode()).hexdigest()
            and m["schedule_sha256"] == hashlib.sha256(canonical(gaps).encode()).hexdigest()
            and m["planned_source_horizon_ns"] == offsets[-1]-offsets[0],
            "Source payload or schedule changed")
    run_id = m["run_id"]
    require(all(x.get("run_id") == run_id and x.get("type") in
                {"manifest", "attempt", "published", "offer"} for x in records),
            "Invalid record type/run identity")
    published = [x for x in records if x["type"] == "published"]
    attempts = [x for x in records if x["type"] == "attempt"]
    offers = [x for x in records if x["type"] == "offer"]
    require([x["event_id"] for x in published] == [x["event_id"] for x in expected_sources]
            and all(x["source"] == expected_source_by_id[x["event_id"]] for x in published),
            "Publisher IDs/content differ from fixture")
    require(len(offers) == len(expected_sources) and
            {x["event_id"] for x in offers} == set(expected_source_by_id) and
            len({x["event_id"] for x in offers}) == len(offers),
            "Missing, duplicate, or unexpected offered IDs")
    by_id = {x["event_id"]: x for x in offers}
    attempts_by_id = {x["attempt_id"]: x for x in attempts}
    require(len(attempts_by_id) == len(attempts), "Duplicate attempt ID")
    duplicates, invalid, matched = 0, 0, set()
    for a in attempts:
        require(a["disposition"] in {"INVALID", "DUPLICATE", "OFFERED"} and
                type(a["callback_ns"]) is int and type(a["validation_end_ns"]) is int and
                a["callback_ns"] <= a["validation_end_ns"] <= cutoff,
                "Invalid attempt lifecycle")
        if a["disposition"] == "INVALID":
            invalid += 1
            require(a["event_id"] is None, "Invalid callback linked to valid ID")
        elif a["disposition"] == "DUPLICATE":
            duplicates += 1
            require(a["event_id"] in by_id, "Duplicate without canonical offer")
        else:
            require(a["event_id"] in by_id and a["attempt_id"] ==
                    by_id[a["event_id"]]["attempt_id"] and a["event_id"] not in matched,
                    "OFFERED attempt not matched one-to-one")
            matched.add(a["event_id"])
    require(matched == set(by_id) and duplicates >= len(offers)//13 and invalid >= 1,
            "Expected original/duplicate/invalid callbacks missing")

    # Offline state machine: only observed offer and completion timestamps
    # determine admission and dispatch; cancellations are consequences of offers.
    timeline = [(x["offer_ns"], 1, "offer", x["event_id"]) for x in offers]
    timeline.extend((x["complete_ns"], 0, "completion", x["event_id"])
                    for x in offers if x["terminal"] == "COMPLETED")
    require(all(type(t) is int and t > 0 for t, _, _, _ in timeline),
            "Invalid monotonic event timestamp")
    timeline.sort()
    active = None
    waiting: list[str] = []
    completed: set[str] = set()
    rejected: set[str] = set()
    cancelled: set[str] = set()
    total_pushouts = 0
    for t, _, kind, eid in timeline:
        row = by_id[eid]
        if kind == "completion":
            require(active == eid and row["start_ns"] <= t <= cutoff and eid not in completed,
                    "Service completion inconsistent with single active worker")
            completed.add(eid)
            if waiting:
                chosen = next((x for x in waiting if by_id[x]["trusted_class"] == "URGENT"),
                              waiting[0])
                snapshot = [{"event_id": x, "trusted_class": by_id[x]["trusted_class"]}
                            for x in waiting]
                selected = by_id[chosen]
                require(selected["dispatch_reason"] == "queued_policy_selection"
                        and selected["dispatch_snapshot"] == snapshot
                        and t <= selected["dispatch_choice_ns"] <= selected["start_ns"],
                        "Strict urgency dispatch/snapshot not independently reproduced")
                waiting.remove(chosen)
                active = chosen
            else:
                active = None
            continue
        require(row["validated_source"] == expected_source_by_id[eid] and
                row["trusted_class"] == ("URGENT" if expected_source_by_id[eid]["tamper"]
                                         else "ROUTINE"),
                "Trusted class/source payload mismatch")
        a = attempts_by_id[row["attempt_id"]]
        require(a["disposition"] == "OFFERED" and
                a["validation_end_ns"] <= t <= cutoff,
                "Offered timestamp precedes validated callback")
        require(row["running_at_offer"] == (active is not None) and
                row["waiting_at_offer"] == len(waiting) and
                row["admission_active_id"] == active and
                row["admission_waiting_ids"] == waiting,
                "Admission state differs from independent queue replay")
        require(len(waiting) <= K, "Queue violates frozen capacity")
        require(row["urgent_deadline_ns"] == (t+deadline_offset if
                row["trusted_class"] == "URGENT" else None),
                "Deadline differs from local post-validation offer")
        full = active is not None and len(waiting) >= K
        victim = None
        if not full:
            action = "ADMIT"
        elif row["trusted_class"] == "URGENT":
            routines = [x for x in waiting if by_id[x]["trusted_class"] == "ROUTINE"]
            if routines:
                victim = routines[-1]
                waiting.remove(victim)
                cancelled.add(victim)
                total_pushouts += 1
                action = "PUSHOUT_ADMIT"
                v = by_id[victim]
                require(v["terminal"] == "CANCELLED" and v["evicted_by_id"] == eid and
                        t <= v["eviction_ns"] <= cutoff and
                        v["start_ns"] is None and v["complete_ns"] is None,
                        "Incorrect victim identity, reason, or timing")
            else:
                action = "REJECT_FULL"
        else:
            action = "REJECT_FULL"
        require(row["admission_action"] == action and row["pushout_victim_id"] == victim,
                "Recorded admission choice disagrees with declared push-out algorithm")
        if action == "REJECT_FULL":
            rejected.add(eid)
            require(row["terminal"] == "REJECTED", "Rejected job later admitted")
        else:
            require(row["terminal"] in {"COMPLETED", "CANCELLED"},
                    "Admitted job has unexpected final status")
            if active is None:
                active = eid
                require(row["dispatch_reason"] == "direct_admission" and
                        row["dispatch_snapshot"] == [] and
                        t <= row["dispatch_choice_ns"] <= row["start_ns"],
                        "Direct admission dispatch not accounted")
            else:
                waiting.append(eid)
    require(active is None and not waiting and
            len(completed) + len(cancelled) + len(rejected) == len(offers) and
            completed.isdisjoint(cancelled | rejected) and cancelled.isdisjoint(rejected),
            "Terminal population or queue residual is inconsistent")

    expected_db = {}
    for eid, row in by_id.items():
        if eid not in completed:
            require(row["start_ns"] is None and row["complete_ns"] is None and
                    all(row.get(k) is None for k in (
                        "synthetic_work_units_post_dispatch", "synthetic_cpu_iterations",
                        "db_committed", "db_rule_result", "db_result_json")),
                    "Dropped job fabricated service/SQLite work")
            continue
        src = expected_source_by_id[eid]
        units = expected_hidden_by_id[eid]
        start, handler, commit, finish = (row[x] for x in
                                          ("start_ns", "db_handler_start_ns",
                                           "db_commit_return_ns", "complete_ns"))
        require(row["synthetic_work_units_post_dispatch"] == units and
                row["synthetic_cpu_iterations"] == units*scale and
                type(row["synthetic_cpu_service_ns"]) is int and
                start + row["synthetic_cpu_service_ns"] <= handler <= commit <= finish <= cutoff and
                row["db_service_ns"] == commit-handler and row["db_committed"] is True,
                "Required ex-ante work or CPU/SQLite order changed")
        device_id = int(src["device_id"].split("_")[1])
        rule = (("TAMPER_DISABLED" if device_id%5 == 0 else "TAMPER_REVIEW") if
                src["tamper"] else ("LOW_BATTERY" if src["battery_pct"]<20 else "HEALTHY"))
        result_json = canonical({"event_id": eid, "zone": f"zone_{device_id%4}", "rule": rule})
        require(row["db_rule_result"] == rule and row["db_result_json"] == result_json,
                "Source/rule/SQLite context output mismatch")
        expected_db[eid] = (src["device_id"], row["trusted_class"], rule, result_json)
    require(m["db_rows_reopened"] == len(completed) and
            sqlite_path.is_file() and
            hashlib.sha256(sqlite_path.read_bytes()).hexdigest() == m["sqlite_backup_sha256"],
            "Persisted DB identity or row count mismatch")
    con = sqlite3.connect(sqlite_path.resolve().as_uri()+"?mode=ro", uri=True)
    try:
        require(con.execute("PRAGMA integrity_check").fetchone()[0] == "ok" and
                con.execute("SELECT COUNT(*) FROM device_context").fetchone()[0] == 16,
                "SQLite integrity/context invalid")
        actual_db = {r[0]: tuple(r[1:]) for r in con.execute(
            "SELECT event_id, device_id, trusted_class, rule_result, result_json FROM handled_alerts")}
    finally:
        con.close()
    require(actual_db == expected_db, "Persisted SQLite rows differ from independently rebuilt expected")
    urgent = [x for x in offers if x["trusted_class"] == "URGENT"]
    routine = [x for x in offers if x["trusted_class"] == "ROUTINE"]
    U = sum(x["terminal"] != "COMPLETED" or
            x["complete_ns"] > x["urgent_deadline_ns"] for x in urgent)/len(urgent)
    R = sum(x["terminal"] == "COMPLETED" and
            x["start_ns"] <= x["offer_ns"] + tau for x in routine)/len(routine)
    return {"status": "PASS_STAGE9_INDEPENDENT_PUSHOUT_QUEUE_AND_SQLITE_AUDIT",
            "policy": m["policy_id"], "transport": transport,
            "offered": len(offers), "committed": len(completed),
            "rejected_full": len(rejected), "cancelled_pushout": len(cancelled),
            "dropped_total": len(rejected)+len(cancelled),
            "pushouts": total_pushouts, "U": U, "R": R,
            "source_fixture_sha256": manifest_file["offer_sha256"],
            "hidden_fixture_sha256": manifest_file["hidden_work_sha256"]}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ledger", type=Path, required=True)
    p.add_argument("--sqlite", type=Path, required=True)
    p.add_argument("--fixture-dir", type=Path, required=True)
    p.add_argument("--require-mqtt", action="store_true")
    a = p.parse_args()
    rows = [json.loads(x) for x in a.ledger.read_text().splitlines() if x.strip()]
    print(json.dumps(audit_run(rows, a.sqlite, a.fixture_dir,
                               require_mqtt=a.require_mqtt), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
