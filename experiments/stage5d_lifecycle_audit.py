#!/usr/bin/env python3
"""Stage 5D: independent offline audit of a declared two-class gateway lifecycle.

No MQTT broker, production measurements, third-party dependencies, or scheduler
implementation are involved. The built-in fixture is explicitly fictional.
Run: python3 stage5d_lifecycle_audit.py --self-test
     python3 stage5d_lifecycle_audit.py gateway_records.jsonl
"""

import argparse
import copy
import json
from pathlib import Path


class AuditError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise AuditError(message)


def nonnegative_int(value, label):
    require(type(value) is int and value >= 0, f"{label} must be a nonnegative integer")
    return value


def exact_int(value, label):
    require(type(value) is int, f"{label} must be an integer")
    return value


def rate_bounds(good, bad, unknown):
    total = good + bad + unknown
    if not total:
        return {"denominator": 0, "lower": None, "upper": None, "exact": None}
    lower, upper = good / total, (good + unknown) / total
    return {"denominator": total, "lower": lower, "upper": upper,
            "exact": lower if unknown == 0 else None}


def audit(records):
    require(isinstance(records, list), "JSONL input must be a list of objects")
    require(all(isinstance(x, dict) for x in records), "every JSONL line must be an object")
    manifests = [r for r in records if r.get("type") == "manifest"]
    require(len(manifests) == 1, "exactly one manifest required")
    m = manifests[0]
    run_id = m.get("run_id")
    require(isinstance(run_id, str) and run_id, "manifest run_id missing")
    for field in ("policy_id", "scenario_id", "trace_provenance"):
        require(isinstance(m.get(field), str) and m[field], f"manifest {field} missing")
    require(m.get("clock_domain") == "single_gateway_process_monotonic_ns",
            "local ns comparisons require one declared gateway monotonic process clock")
    require(m.get("dedup_cache_reset") is True, "run must start with reset scoped dedup state")
    for field in ("publisher_log_complete", "receiver_capture_complete"):
        require(type(m.get(field)) is bool, f"manifest {field} must be boolean")
    cap = nonnegative_int(m.get("K"), "K")
    tau = nonnegative_int(m.get("routine_tau_ns"), "routine_tau_ns")
    cutoff = nonnegative_int(m.get("observation_end_ns"), "observation_end_ns")
    for r in records:
        require(r.get("type") in {"manifest", "published", "attempt", "offer"}, "unknown record type")
        require(r.get("run_id") == run_id, "all rows must share run_id")

    published = [r for r in records if r["type"] == "published"]
    attempts = [r for r in records if r["type"] == "attempt"]
    offers = [r for r in records if r["type"] == "offer"]
    source_ids = set()
    for p in published:
        eid = p.get("event_id")
        require(isinstance(eid, str) and eid and eid not in source_ids,
                "published event IDs must be unique and nonempty")
        source_ids.add(eid)
        require(isinstance(p.get("publisher_clock_note"), str) and p["publisher_clock_note"],
                "source timestamps must declare their separate clock; no ns cross-clock subtraction")

    by_attempt, canonical, received_ids = {}, {}, set()
    counts = {"OFFERED": 0, "DUPLICATE": 0, "INVALID": 0}
    for a in attempts:
        aid = a.get("attempt_id")
        require(isinstance(aid, str) and aid and aid not in by_attempt, "duplicate/empty attempt_id")
        cb = nonnegative_int(a.get("callback_ns"), f"{aid}.callback_ns")
        valid_end = nonnegative_int(a.get("validation_end_ns"), f"{aid}.validation_end_ns")
        require(cb <= valid_end <= cutoff, f"{aid} invalid callback/validation order")
        status = a.get("disposition")
        require(status in counts, f"{aid} invalid disposition")
        eid = a.get("event_id")
        if status != "INVALID":
            require(isinstance(eid, str) and eid, f"{aid} needs event_id")
        if eid is not None:
            require(isinstance(eid, str) and eid, f"{aid} invalid event_id")
            received_ids.add(eid)
            if m["publisher_log_complete"]:
                require(eid in source_ids, f"{aid} not present in complete publisher manifest")
        if status == "OFFERED":
            require(eid not in canonical, f"logical event offered twice: {eid}")
            canonical[eid] = a
        by_attempt[aid] = a
        counts[status] += 1

    for a in attempts:
        if a["disposition"] == "DUPLICATE":
            eid = a["event_id"]
            require(eid in canonical, f"duplicate without observed original: {eid}")
            require(canonical[eid]["callback_ns"] <= a["callback_ns"],
                    f"duplicate precedes first accepted delivery: {eid}")

    seen_offer_ids, seen_offer_attempts = set(), set()
    good_u = bad_u = unknown_u = good_r = bad_r = unknown_r = 0
    completed_durations, intervals = [], []
    rejects = 0
    for o in offers:
        eid, aid = o.get("event_id"), o.get("attempt_id")
        require(isinstance(eid, str) and eid and eid not in seen_offer_ids,
                "offer event ID must be nonempty and unique")
        require(isinstance(aid, str) and aid and aid not in seen_offer_attempts,
                "offer attempt ID must be nonempty and unique")
        require(aid in by_attempt and by_attempt[aid]["disposition"] == "OFFERED"
                and by_attempt[aid]["event_id"] == eid, f"unmatched offered attempt: {aid}")
        a = by_attempt[aid]
        cls = o.get("trusted_class")
        require(cls in ("URGENT", "ROUTINE"), f"{eid} must use two trusted classes")
        offered = nonnegative_int(o.get("offer_ns"), f"{eid}.offer_ns")
        require(a["validation_end_ns"] <= offered <= cutoff, f"{eid} offer before validation/end")
        waiting = nonnegative_int(o.get("waiting_at_offer"), f"{eid}.waiting_at_offer")
        active = o.get("running_at_offer")
        require(waiting <= cap and type(active) is bool, f"{eid} invalid capacity snapshot")
        status = o.get("terminal")
        require(status in ("COMPLETED", "REJECTED", "EXPIRED", "CANCELLED", "UNRESOLVED"),
                f"{eid} invalid terminal")
        start, complete = o.get("start_ns"), o.get("complete_ns")
        if start is not None:
            nonnegative_int(start, f"{eid}.start_ns")
            require(offered <= start <= cutoff, f"{eid} invalid service start")
        if complete is not None:
            nonnegative_int(complete, f"{eid}.complete_ns")
            require(start is not None and start <= complete <= cutoff, f"{eid} invalid completion")
        if status == "REJECTED":
            rejects += 1
            require(waiting == cap and active, f"{eid} rejection needs full waiting+running")
            require(start is None and complete is None, f"{eid} rejected but serviced")
        else:
            require(not (waiting == cap and active), f"{eid} admitted despite occupied full queue")
            if status == "COMPLETED":
                require(start is not None and complete is not None, f"{eid} completion timestamps absent")
                completed_durations.append(complete - start)
            elif status in ("EXPIRED", "CANCELLED"):
                require(start is None and complete is None,
                        f"{eid} pre-service termination cannot interrupt worker")
            else:
                require(complete is None, f"{eid} unresolved cannot already complete")
        if start is not None:
            intervals.append((start, complete if complete is not None else cutoff, eid))

        if cls == "URGENT":
            deadline = nonnegative_int(o.get("urgent_deadline_ns"), f"{eid}.deadline")
            require(deadline >= offered, f"{eid} deadline before offer")
            if status == "COMPLETED":
                good_u += complete <= deadline
                bad_u += complete > deadline
            elif status == "UNRESOLVED" and deadline > cutoff:
                unknown_u += 1
            else:
                bad_u += 1
            require(o.get("routine_tau_override_ns") is None,
                    f"{eid} urgent should not carry routine tau override")
        else:
            require(o.get("urgent_deadline_ns") is None,
                    f"{eid} routine must not have urgent deadline")
            threshold = offered + tau
            if start is not None:
                good_r += start <= threshold
                bad_r += start > threshold
            elif status == "UNRESOLVED" and threshold > cutoff:
                unknown_r += 1
            else:
                bad_r += 1
        seen_offer_ids.add(eid)
        seen_offer_attempts.add(aid)

    require(seen_offer_ids == set(canonical), "each OFFERED attempt needs exactly one offer row")
    for prev, nxt in zip(sorted(intervals), sorted(intervals)[1:]):
        require(prev[1] <= nxt[0], f"single non-preemptive worker overlap: {prev[2]} -> {nxt[2]}")
    # All rates are offered-population rates. Urgent is a failure rate (bounds reverse).
    u = rate_bounds(bad_u, good_u, unknown_u)
    r = rate_bounds(good_r, bad_r, unknown_r)
    missing = (len(source_ids - received_ids) if m["publisher_log_complete"]
               else None)
    return {
        "run_id": run_id, "policy_id": m["policy_id"],
        "publisher_log_complete": m["publisher_log_complete"],
        "receiver_capture_complete": m["receiver_capture_complete"],
        "published_unique": len(source_ids) if m["publisher_log_complete"] else None,
        "published_ids_without_callback": missing,
        "delivery_attempts": len(attempts), "duplicates": counts["DUPLICATE"],
        "invalid_attempts": counts["INVALID"], "offered_unique": len(offers),
        "admitted": len(offers) - rejects, "rejected": rejects,
        "urgent_failure_U_bounds": u, "routine_timely_start_R_bounds": r,
        "measured_completed_service_n": len(completed_durations),
        "unresolved_offers": sum(x.get("terminal") == "UNRESOLVED" for x in offers),
        "calibration_status": "NOT VALIDATED; lifecycle ledger alone is not representative workload evidence",
    }


def toy_records():
    # Invented small integer-ns fixture, not physically realistic nanosecond service.
    run = "fictional-golden-fixture"
    def row(kind, **kw):
        return {"type": kind, "run_id": run, **kw}
    rows = [row("manifest", policy_id="fifo", scenario_id="fixture_only",
                trace_provenance="invented_hand_check_not_empirical", K=1, routine_tau_ns=100,
                observation_end_ns=800, clock_domain="single_gateway_process_monotonic_ns",
                dedup_cache_reset=True, publisher_log_complete=True,
                receiver_capture_complete=True)]
    for eid in ("e1", "e2", "e3", "e4", "e5_unreceived"):
        rows.append(row("published", event_id=eid,
                        publisher_clock_note="publisher independent time; do not subtract"))
    rows += [
        row("attempt", attempt_id="a1", event_id="e1", callback_ns=100,
            validation_end_ns=110, disposition="OFFERED"),
        row("attempt", attempt_id="a2", event_id="e2", callback_ns=105,
            validation_end_ns=115, disposition="OFFERED"),
        row("attempt", attempt_id="a1_dup", event_id="e1", callback_ns=120,
            validation_end_ns=125, disposition="DUPLICATE"),
        row("attempt", attempt_id="a3", event_id="e3", callback_ns=130,
            validation_end_ns=140, disposition="OFFERED"),
        row("attempt", attempt_id="a_bad", event_id=None, callback_ns=150,
            validation_end_ns=160, disposition="INVALID"),
        row("attempt", attempt_id="a4", event_id="e4", callback_ns=280,
            validation_end_ns=290, disposition="OFFERED"),
        row("offer", attempt_id="a1", event_id="e1", trusted_class="URGENT",
            offer_ns=111, waiting_at_offer=0, running_at_offer=False, terminal="COMPLETED",
            urgent_deadline_ns=250, start_ns=112, complete_ns=210),
        row("offer", attempt_id="a2", event_id="e2", trusted_class="ROUTINE",
            offer_ns=116, waiting_at_offer=0, running_at_offer=True, terminal="COMPLETED",
            urgent_deadline_ns=None, start_ns=211, complete_ns=260),
        row("offer", attempt_id="a3", event_id="e3", trusted_class="URGENT",
            offer_ns=141, waiting_at_offer=1, running_at_offer=True, terminal="REJECTED",
            urgent_deadline_ns=300, start_ns=None, complete_ns=None),
        row("offer", attempt_id="a4", event_id="e4", trusted_class="ROUTINE",
            offer_ns=291, waiting_at_offer=0, running_at_offer=False, terminal="COMPLETED",
            urgent_deadline_ns=None, start_ns=292, complete_ns=350),
    ]
    return rows


def self_test():
    original = toy_records()
    summary = audit(original)
    assert summary["offered_unique"] == 4 and summary["admitted"] == 3
    assert summary["rejected"] == 1 and summary["duplicates"] == 1
    assert summary["published_ids_without_callback"] == 1
    assert summary["urgent_failure_U_bounds"]["exact"] == 0.5
    assert summary["routine_timely_start_R_bounds"]["exact"] == 1.0
    print("PASS positive hand-checked fictional ledger")

    tests = [
        ("offer before validation", lambda d: d[-4].update(offer_ns=109)),
        ("duplicate logical offer", lambda d: d[-1].update(event_id="e2")),
        ("rejected job cannot start", lambda d: d[-2].update(start_ns=180)),
        ("rejected job must be full", lambda d: d[-2].update(waiting_at_offer=0)),
        ("admitted job cannot exceed K", lambda d: d[-3].update(waiting_at_offer=2)),
        ("bad order", lambda d: d[-1].update(start_ns=280)),
        ("single-worker overlap", lambda d: d[-1].update(start_ns=240)),
        ("missing offer row", lambda d: d.pop()),
        ("wrong clock declaration", lambda d: d[0].update(clock_domain="system_wall_clock")),
        ("duplicate before canonical receipt", lambda d: d[8].update(callback_ns=90, validation_end_ns=100)),
    ]
    for name, modify in tests:
        trial = copy.deepcopy(original)
        modify(trial)
        try:
            audit(trial)
        except AuditError:
            print("PASS rejected malformed ledger:", name)
        else:
            raise AssertionError(f"audit failed to reject: {name}")

    # Explicitly verify conservative uncertainty bounds for unfinished offers.
    pending = copy.deepcopy(original)
    pending[0]["observation_end_ns"] = 500
    pending[-1].update(terminal="UNRESOLVED", start_ns=None, complete_ns=None,
                       offer_ns=450, waiting_at_offer=0, running_at_offer=False)
    pending[11]["callback_ns"] = 420
    pending[11]["validation_end_ns"] = 430
    result = audit(pending)
    assert result["routine_timely_start_R_bounds"]["lower"] == 0.5
    assert result["routine_timely_start_R_bounds"]["upper"] == 1.0
    assert result["routine_timely_start_R_bounds"]["exact"] is None
    print("PASS unresolved routine offer yields interval, not false exact rate")
    print(json.dumps(summary, sort_keys=True))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("jsonl", nargs="?", type=Path)
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.self_test or args.jsonl is None:
        self_test()
    else:
        rows = [json.loads(line) for line in args.jsonl.read_text(encoding="utf-8").splitlines()
                if line.strip()]
        print(json.dumps(audit(rows), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
