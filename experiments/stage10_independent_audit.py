#!/usr/bin/env python3
"""Independent Stage 10 tuning-only queue, service and durable-overflow auditor.

Uses no Stage 10 emitter or gateway imports. Reconstructs the K+B capacity
transitions, independently reproduces service order from observed timestamps,
checks persisted main and deferred SQLite rows, and includes all offered IDs.
Not a claim of actual crash-restart recovery or a frozen scientific outcome.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sqlite3

from stage5k2_independent_audit import audit as audit_fixture
from stage9_independent_audit import independent_source, canonical


POLICIES = {"pushout_slack", "fifo_deferred", "strict_deferred",
            "pushout_deferred", "pushout_reserved_deferred", "pushout_slack_deferred"}


def require(ok, message):
    if not ok:
        raise ValueError("STAGE10 INDEPENDENT AUDIT FAILURE: "+message)


def read_db(path: Path, expected_sha: str, query: str) -> list[tuple]:
    require(path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == expected_sha,
            "SQLite digest mismatch or missing database")
    con = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        require(con.execute("PRAGMA integrity_check").fetchone()[0] == "ok",
                "SQLite integrity check failed")
        return con.execute(query).fetchall()
    finally:
        con.close()


def audit_run(records: list[dict], worker_db: Path, spool_db: Path,
              fixture_dir: Path, *, require_mqtt: bool = False) -> dict:
    fixture = audit_fixture(fixture_dir)
    require(len([x for x in records if x.get("type") == "manifest"]) == 1,
            "Expected exactly one manifest")
    man = next(x for x in records if x["type"] == "manifest")
    policy, K, B, run_id = (man[x] for x in ("policy_id", "K", "B", "run_id"))
    phase = man.get("evidence_phase", "development")  # Old reserved tuning ledgers.
    require(policy in POLICIES and type(K) is int and K >= 0
            and type(B) is int and B >= 0,
            "Unexpected policy or invalid explicit capacity")
    require((B == 0) == (policy == "pushout_slack") and
            man["additional_capacity_declared"] == (B > 0) and
            phase in {"development", "frozen_holdout"} and
            man["study_status"] == (
                "STAGE10_FROZEN_HELDOUT_SYNTHETIC_NOT_FIELD_CALIBRATED"
                if phase == "frozen_holdout" else "STAGE10_TUNING_ONLY_NO_INFERENCE") and
            man["field_calibrated"] is False and
            man["algorithm_novelty_verified"] is False,
            "Invalid pilot provenance or unreported extra storage")
    require(man["transport"] in {"mqtt", "inproc"} and
            (not require_mqtt or man["transport"] == "mqtt") and
            (phase != "frozen_holdout" or
             (require_mqtt and man["transport"] == "mqtt")) and
            man["scenario_id"] == (
                "stage10_holdout_mqtt" if phase == "frozen_holdout"
                else "stage10_pilot_"+man["transport"]),
            "Transport substituted")
    require(man["slack_guard_ns"] == 3_000_000 and
            man["slack_estimator"] == "PREVIOUS_COMPLETED_CLASS_SERVICE_P90_16_WINDOW_15MS_WARMUP",
            "Unregistered slack estimator")
    # Pre-reservation development ledgers did not yet carry this explicit zero
    # field. Accept *only* their zero-equivalent; reserve variant requires it.
    require(man.get("new_routine_overflow_limit", 0) ==
            (B//2 if policy == "pushout_reserved_deferred" else 0),
            "Undeclared spool reservation policy")
    scale = man["synthetic_iterations_per_work_unit"]
    require(type(scale) is int and 1 <= scale <= 1_000_000,
            "Invalid synthetic CPU work scale")
    offered_expected = [independent_source(x) for x in fixture["offers"]]
    source_by_id = {x["event_id"]: x for x in offered_expected}
    hidden_by_id = {x["event_id"]: x["synthetic_required_work_units"] for x in fixture["hidden"]}
    fmanifest = json.loads((fixture_dir / "manifest.json").read_text())
    require(man["fixture_id"] == fmanifest["fixture_id"] and
            man["offer_fixture_sha256"] == fmanifest["offer_sha256"] and
            man["hidden_work_sha256"] == fmanifest["hidden_work_sha256"] and
            man["source_sha256"] == hashlib.sha256(canonical(offered_expected).encode()).hexdigest(),
            "Source/hidden fixture identity mismatch")
    offsets = [x["planned_offer_offset_ns"] for x in fixture["offers"]]
    gaps = [offsets[0], *(b-a for a,b in zip(offsets, offsets[1:]))]
    require(man["schedule_sha256"] == hashlib.sha256(canonical(gaps).encode()).hexdigest(),
            "Scheduled source timing changed")
    cutoff = man["observation_end_ns"]
    require(type(cutoff) is int and cutoff > 0 and
            man["urgent_deadline_offset_ns"] == 50_000_000 and
            man["routine_tau_ns"] == 20_000_000,
            "Invalid observation boundary or artificial timing parameters")
    require(all(x.get("run_id") == run_id and x.get("type") in
                {"manifest", "published", "attempt", "offer"} for x in records),
            "Wrong run identity or unexpected raw record")
    published = [x for x in records if x["type"] == "published"]
    require([x["event_id"] for x in published] == [x["event_id"] for x in offered_expected]
            and all(x["source"] == source_by_id[x["event_id"]] for x in published),
            "Publisher payload/IDs mismatch source")
    offers = [x for x in records if x["type"] == "offer"]
    require(len(offers) == len(offered_expected) and
            set(x["event_id"] for x in offers) == set(source_by_id) and
            len({x["event_id"] for x in offers}) == len(offers),
            "Offered source population changed")
    by_id = {x["event_id"]: x for x in offers}
    attempts = [x for x in records if x["type"] == "attempt"]
    attempt_by_id = {x["attempt_id"]: x for x in attempts}
    require(len(attempt_by_id) == len(attempts), "Duplicate callback IDs")
    matched, invalid, duplicate = set(), 0, 0
    for a in attempts:
        require(a["disposition"] in {"OFFERED", "DUPLICATE", "INVALID"}
                and a["callback_ns"] <= a["validation_end_ns"] <= cutoff,
                "Invalid callback lifecycle")
        if a["disposition"] == "INVALID":
            invalid += 1
            require(a["event_id"] is None, "Malformed callback attached to valid offer")
        elif a["disposition"] == "DUPLICATE":
            duplicate += 1
            require(a["event_id"] in by_id, "Duplicate callback unmatched")
        else:
            eid = a["event_id"]
            require(eid in by_id and eid not in matched and
                    a["attempt_id"] == by_id[eid]["attempt_id"],
                    "Offered callback not unique or matched")
            matched.add(eid)
    require(matched == set(by_id) and invalid >= 1 and
            duplicate >= len(offers)//13,
            "Original/duplicate/invalid population not complete")

    # Replay offer/worker completion transitions independently of the emitter.
    timeline = [(x["offer_ns"], 1, "offer", x["event_id"]) for x in offers]
    timeline += [(x["complete_ns"], 0, "complete", x["event_id"])
                 for x in offers if x["terminal"] == "COMPLETED"]
    require(all(type(t) is int and 0 < t <= cutoff for t, _, _, _ in timeline),
            "Invalid local clock timestamps")
    timeline.sort()
    active = None
    waiting: list[str] = []
    deferred: list[str] = []
    completed, rejected, cancelled = set(), set(), set()
    queued_spool: dict[str, tuple] = {}
    history: list[tuple[str, int]] = []
    spool_peak = 0

    def estimate(cls: str) -> int:
        xs = sorted([x[1] for x in history if x[0] == cls][-16:])
        return xs[int((len(xs)-1)*0.90)] if len(xs) >= 3 else 15_000_000

    for stamp, _, typ, eid in timeline:
        row = by_id[eid]
        if typ == "complete":
            require(active == eid and row["start_ns"] <= stamp and
                    eid not in completed and row["terminal"] == "COMPLETED",
                    "Invalid active-worker or duplicate completion")
            completed.add(eid)
            history.append((row["trusted_class"],
                            row["synthetic_cpu_service_ns"]+row["db_service_ns"]))
            if waiting:
                urgents = [x for x in waiting if by_id[x]["trusted_class"] == "URGENT"]
                routines = [x for x in waiting if by_id[x]["trusted_class"] == "ROUTINE"]
                if policy == "fifo_deferred":
                    chosen, reason = waiting[0], "fifo_policy_selection"
                elif "slack" in policy and urgents and routines:
                    # Among all outstanding waiting jobs, the one dispatched
                    # now has the earliest recorded choice timestamp. Other
                    # jobs may already contain *future* dispatch timestamps
                    # in this finalized ledger; those are not current choices.
                    choices = [by_id[x]["dispatch_choice_ns"] for x in waiting
                               if by_id[x].get("dispatch_choice_ns") is not None]
                    # Some waiting jobs will later be evicted and therefore
                    # legitimately never receive a dispatch timestamp.
                    require(bool(choices), "No currently waiting job dispatched")
                    decision = min(choices)
                    require(decision >= stamp, "Dispatch predates worker completion")
                    deadline = min(by_id[x]["urgent_deadline_ns"] for x in urgents)
                    choose_routine = deadline - decision - estimate("ROUTINE") - estimate("URGENT") - 3_000_000 > 0
                    chosen = routines[0] if choose_routine else urgents[0]
                    reason = "slack_policy_selection"
                else:
                    chosen = urgents[0] if urgents else waiting[0]
                    reason = "strict_urgent_policy_selection"
                snapshot = [{"event_id": x, "trusted_class": by_id[x]["trusted_class"]}
                            for x in waiting]
                picked = by_id[chosen]
                require(picked["dispatch_reason"] == reason and
                        picked["dispatch_snapshot"] == snapshot and
                        stamp <= picked["dispatch_choice_ns"] <= picked["start_ns"],
                        "Main-queue dispatch violates registered order")
                waiting.remove(chosen)
                active = chosen
            elif deferred:
                if policy == "fifo_deferred":
                    chosen = deferred[0]
                else:
                    chosen = next((x for x in deferred if by_id[x]["trusted_class"] == "URGENT"),
                                  deferred[0])
                picked = by_id[chosen]
                snapshot = [{"event_id": x} for x in deferred]
                require(picked["dispatch_reason"] == "deferred_recovery" and
                        picked["dispatch_snapshot"] == snapshot and
                        stamp <= picked["dispatch_choice_ns"] <= picked["start_ns"],
                        "Deferred dispatch/priority/snapshot mismatch")
                deferred.remove(chosen)
                active = chosen
            else:
                active = None
            continue

        require(row["validated_source"] == source_by_id[eid] and
                row["trusted_class"] == ("URGENT" if source_by_id[eid]["tamper"] else "ROUTINE")
                and row["urgent_deadline_ns"] == (
                    stamp + man["urgent_deadline_offset_ns"] if row["trusted_class"] == "URGENT"
                    else None), "Source/class/artificial deadline mismatched")
        attempt = attempt_by_id[row["attempt_id"]]
        require(attempt["disposition"] == "OFFERED" and
                attempt["validation_end_ns"] <= stamp <= cutoff and
                row["running_at_offer"] == (active is not None) and
                row["waiting_at_offer"] == len(waiting) and
                row["deferred_at_offer"] == len(deferred) and
                row["admission_active_id"] == active and
                row["admission_waiting_ids"] == waiting and
                row["admission_deferred_ids"] == deferred,
                "Admission snapshot does not match offline queue replay")
        require(len(waiting) <= K and len(deferred) <= B,
                "K+B capacity overrun")
        full = active is not None and len(waiting) >= K
        pushout = policy.startswith("pushout_")
        victim = None
        if not full:
            action = "ADMIT_MAIN"
        elif pushout and row["trusted_class"] == "URGENT":
            routines = [x for x in waiting if by_id[x]["trusted_class"] == "ROUTINE"]
            if routines:
                victim = routines[-1]
                waiting.remove(victim)
                if B == 0 or len(deferred) >= B:
                    action = "PUSHOUT_DROP_ADMIT"
                    cancelled.add(victim)
                    vr = by_id[victim]
                    require(vr["terminal"] == "CANCELLED" and
                            vr["evicted_by_id"] == eid and
                            stamp <= vr["eviction_ns"] <= cutoff,
                            "Unaccounted pushout cancellation")
                else:
                    action = "PUSHOUT_DEFER_ADMIT"
                    vr = by_id[victim]
                    require(vr["defer_reason"] == "URGENT_PUSHOUT" and
                            vr["was_deferred"] is True and
                            vr["evicted_by_id"] == eid and
                            stamp <= vr["defer_ns"] <= cutoff,
                            "Evicted routine not durably accounted")
                    deferred.append(victim)
                    queued_spool[victim] = ("URGENT_PUSHOUT", vr["defer_ns"])
            else:
                action = "REJECT_CAPACITY"
        elif pushout:
            if policy == "pushout_reserved_deferred" and len(deferred) < B//2:
                action = "DEFER_NEW"
                require(row["defer_reason"] == "BUFFER_OVERFLOW" and
                        row["was_deferred"] is True and
                        stamp <= row["defer_ns"] <= cutoff,
                        "Reserved overflow offer not persisted")
                deferred.append(eid)
                queued_spool[eid] = ("BUFFER_OVERFLOW", row["defer_ns"])
            else:
                action = "REJECT_CAPACITY"
        elif len(deferred) < B:
            action = "DEFER_NEW"
            require(row["defer_reason"] == "BUFFER_OVERFLOW" and
                    row["was_deferred"] is True and
                    stamp <= row["defer_ns"] <= cutoff,
                    "Overflow offer not persisted")
            deferred.append(eid)
            queued_spool[eid] = ("BUFFER_OVERFLOW", row["defer_ns"])
        else:
            action = "REJECT_CAPACITY"
        require(row["admission_action"] == action and
                row["pushout_victim_id"] == victim,
                "Admitting policy differs from independently derived state")
        if action == "REJECT_CAPACITY":
            require(row["terminal"] == "REJECTED", "Rejected offer later serviced")
            rejected.add(eid)
        elif action in {"ADMIT_MAIN", "PUSHOUT_DROP_ADMIT", "PUSHOUT_DEFER_ADMIT"}:
            # A job admitted *now* can legitimately be cancelled by a later
            # urgent pushout. Its cancellation is audited at that later offer.
            require(row["terminal"] in {"COMPLETED", "CANCELLED"},
                    "Admitted job has an impossible final status")
            if active is None:
                require(row["dispatch_reason"] == "direct_admission" and
                        row["dispatch_snapshot"] == [] and
                        stamp <= row["dispatch_choice_ns"] <= row["start_ns"],
                        "Direct dispatch incorrect")
                active = eid
            else:
                waiting.append(eid)
        elif action == "DEFER_NEW":
            require(row["terminal"] == "COMPLETED", "Deferred offer not serviced")
        spool_peak = max(spool_peak, len(deferred))
    require(active is None and not waiting and not deferred and
            len(completed)+len(cancelled)+len(rejected) == len(offers) and
            completed.isdisjoint(cancelled | rejected) and
            cancelled.isdisjoint(rejected),
            "Unresolved/double-counted terminal population")
    require(spool_peak == man["spool_peak"] and
            len(queued_spool) == man["spool_total_inserted"] == man["spool_total_completed"],
            "Spool peak/inserted/completed counts diverge")

    expected_db = {}
    for eid, row in by_id.items():
        if eid not in completed:
            require(row["start_ns"] is None and row["complete_ns"] is None and
                    all(row.get(k) is None for k in (
                        "synthetic_work_units_post_dispatch", "synthetic_cpu_iterations",
                        "db_committed", "db_rule_result", "db_result_json")),
                    "Fabricated work for non-completed offer")
            continue
        src = source_by_id[eid]
        units = hidden_by_id[eid]
        start, handler, commit, finish = (row[k] for k in
                                          ("start_ns", "db_handler_start_ns",
                                           "db_commit_return_ns", "complete_ns"))
        require(row["synthetic_work_units_post_dispatch"] == units and
                row["synthetic_cpu_iterations"] == units*scale and
                start + row["synthetic_cpu_service_ns"] <= handler <= commit <= finish <= cutoff and
                row["db_service_ns"] == commit - handler and row["db_committed"] is True,
                "Hidden work or handler timing inconsistent")
        device = int(src["device_id"].split("_")[1])
        rule = (("TAMPER_DISABLED" if device%5 == 0 else "TAMPER_REVIEW") if src["tamper"] else
                ("LOW_BATTERY" if src["battery_pct"]<20 else "HEALTHY"))
        result_json = canonical({"event_id":eid,"zone":f"zone_{device%4}","rule":rule})
        require(row["db_rule_result"] == rule and row["db_result_json"] == result_json,
                "Unexpected persisted reference handler output")
        expected_db[eid] = (src["device_id"], row["trusted_class"], rule, result_json)
    stored = read_db(worker_db, man["worker_sqlite_sha256"],
                     "SELECT event_id,device_id,trusted_class,rule_result,result_json FROM handled_alerts")
    require({x[0]: tuple(x[1:]) for x in stored} == expected_db,
            "Physical main SQLite differs from independently inferred service")
    spool_rows = read_db(spool_db, man["spool_sqlite_sha256"],
                         "SELECT event_id,trusted_class,reason,defer_ns,claim_ns,completed_ns,state "
                         "FROM deferred_alerts")
    actual_spool = {x[0]: x[1:] for x in spool_rows}
    require(set(actual_spool) == set(queued_spool), "Missing/extra stored deferral rows")
    for eid, (cls, reason, d_ns, c_ns, end_ns, state) in actual_spool.items():
        row = by_id[eid]
        require((reason, d_ns) == queued_spool[eid] and
                cls == row["trusted_class"] and
                (reason != "URGENT_PUSHOUT" or cls == "ROUTINE"),
                "Stored deferred class/reason does not match source")
        require(state == "COMPLETED" and
                d_ns <= c_ns <= row["start_ns"] <= end_ns <= row["complete_ns"] and
                row["was_deferred"] is True,
                "Deferred claim/completion not durably tracked")
    urgent = [x for x in offers if x["trusted_class"] == "URGENT"]
    routine = [x for x in offers if x["trusted_class"] == "ROUTINE"]
    return {"status": "PASS_STAGE10_INDEPENDENT_K_PLUS_B_SQLITE_QUEUE_AUDIT",
            "policy":policy,"K":K,"B":B,"offered":len(offers),
            "completed":len(completed),"rejected":len(rejected),"cancelled":len(cancelled),
            "U":sum(x["terminal"] != "COMPLETED" or
                    x["complete_ns"] > x["urgent_deadline_ns"] for x in urgent)/len(urgent),
            "R":sum(x["terminal"] == "COMPLETED" and
                    x["start_ns"] <= x["offer_ns"] + man["routine_tau_ns"]
                    for x in routine)/len(routine),
            "C":sum(x["terminal"] == "COMPLETED" for x in routine)/len(routine),
            "spool_peak":spool_peak,"spool_inserted":len(queued_spool)}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ledger",type=Path,required=True)
    p.add_argument("--sqlite",type=Path,required=True)
    p.add_argument("--spool",type=Path,required=True)
    p.add_argument("--fixture-dir",type=Path,required=True)
    p.add_argument("--require-mqtt",action="store_true")
    a=p.parse_args()
    rows=[json.loads(x) for x in a.ledger.read_text().splitlines() if x.strip()]
    print(json.dumps(audit_run(rows,a.sqlite,a.spool,a.fixture_dir,
                               require_mqtt=a.require_mqtt),sort_keys=True,indent=2))


if __name__ == "__main__":
    main()
