#!/usr/bin/env python3
"""Independent offline checker for Stage 5G *synthetic reference handler* JSONL.

Does not import the emitter or trust its reported service durations, class,
rule outcome, source digest, or declared row count. Cannot attest hardware
durability, field representativeness, MQTT timing, or domain deadlines.
"""

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import statistics


class AuditError(ValueError):
    pass


def check(condition, message):
    if not condition:
        raise AuditError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def quantile(values, fraction):
    ordered = sorted(values)
    return ordered[max(0, math.ceil(len(ordered) * fraction) - 1)]


def audit(rows):
    check(len(rows) > 1 and rows[0].get("type") == "manifest", "missing first manifest")
    m = rows[0]
    check(sum(row.get("type") == "manifest" for row in rows) == 1, "multiple manifests")
    check(m.get("scenario") == "stage5g_synthetic_sqlite_reference", "unverified handler scenario")
    check(m.get("clock_domain") == "single_process_monotonic_ns", "mixed clocks")
    check(m.get("journal_mode") == "WAL" and m.get("synchronous") == "FULL",
          "SQLite commit configuration not declared")
    check(m.get("worker_count") == 1 and m.get("completion_boundary") == "sqlite_commit_return",
          "wrong single worker or completion boundary")
    check(m.get("handler") == "context_SQL_lookup + deterministic_rule + one_SQLite_INSERT + commit",
          "unexpected application work contract")
    seed, planned = m.get("seed"), m.get("planned_unique")
    check(type(seed) is int and seed >= 0 and type(planned) is int and planned >= 8,
          "invalid seed or planned population")
    check(type(m.get("reopen_rows_verified")) is int and m["reopen_rows_verified"] == planned,
          "emitter did not report complete close/reopen records")
    events = rows[1:]
    check(len(events) == planned and all(row.get("type") == "handled" for row in events),
          "missing/extra handler records")

    by_class = {"URGENT": [], "ROUTINE": []}
    sources, seen = [], set()
    prev_end = None
    for i, row in enumerate(events):
        src = row.get("source")
        check(isinstance(src, dict) and set(src) == {
            "event_id", "device_id", "kind", "tamper", "battery_pct"
        }, "bad synthetic input schema")
        eid = f"s5g_{seed}_{i:05d}"
        check(src["event_id"] == eid and row.get("event_id") == eid and eid not in seen,
              "source ordering, ID or uniqueness violation")
        seen.add(eid)
        check(src["kind"] in ("tamper", "health") and
              src["kind"] == ("tamper" if i % 4 == 0 else "health") and
              type(src["tamper"]) is bool and src["tamper"] == (i % 4 == 0),
              "unexpected synthetic class sequence")
        battery = src["battery_pct"]
        check(type(battery) is int and 0 <= battery <= 100, "invalid battery input")
        device = src["device_id"]
        check(isinstance(device, str) and device.startswith("device_") and
              len(device) == 9 and device[7:].isdigit() and 0 <= int(device[7:]) <= 15,
              "unknown device for fictional context table")
        device_idx = int(device[7:])
        cls = "URGENT" if i % 4 == 0 else "ROUTINE"
        rule = ("TAMPER_DISABLED" if device_idx % 5 == 0 else "TAMPER_REVIEW") if cls == "URGENT" else (
            "LOW_BATTERY" if battery < 20 else "HEALTHY")
        expected_result = canonical({"event_id": eid, "zone": f"zone_{device_idx % 4}",
                                     "rule": rule})
        check(row.get("trusted_class") == cls and row.get("rule_result") == rule and
              row.get("result_json") == expected_result, "class/rule/context mismatch")
        check(row.get("committed") is True, "uncommitted handler record")
        start, end, service = (row.get("work_start_ns"), row.get("commit_return_ns"),
                               row.get("service_ns"))
        check(all(type(x) is int for x in (start, end, service)), "invalid service clock type")
        check(start >= 0 and end > start and service == end - start,
              "nonpositive or dishonest handler service interval")
        check(prev_end is None or start >= prev_end, "worker intervals overlap")
        prev_end = end
        by_class[cls].append(service)
        sources.append(src)

    check(all(by_class.values()), "at least one class is missing")
    check(hashlib.sha256(canonical(sources).encode()).hexdigest() == m.get("trace_sha256"),
          "synthetic source provenance digest mismatch")
    result = {
        "status": "SYNTHETIC_SQLITE_LAB_LEDGER_PASS",
        "seed": seed, "records": planned,
        "source_sha256": m["trace_sha256"],
        "classes": {},
        "boundary": "work_start to SQLite commit return, excluding validation/MQTT/queue",
        "warning": "single-machine mock device context; not operator field/service calibration or SLA evidence",
    }
    for cls, times in by_class.items():
        result["classes"][cls] = {
            "n": len(times), "min_ns": min(times), "median_ns": statistics.median(times),
            "p90_ns": quantile(times, .90), "p95_ns": quantile(times, .95),
            "p99_ns": quantile(times, .99), "max_ns": max(times),
            "mean_ns": round(statistics.mean(times), 2),
        }
    return result


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def self_test():
    seed = 101
    events = []
    sources = []
    for i in range(8):
        src = {"event_id": f"s5g_{seed}_{i:05d}", "device_id": "device_01",
               "kind": "tamper" if i % 4 == 0 else "health",
               "tamper": i % 4 == 0, "battery_pct": 50}
        sources.append(src)
        rule = "TAMPER_REVIEW" if i % 4 == 0 else "HEALTHY"
        events.append({"type": "handled", "event_id": src["event_id"], "source": src,
                       "trusted_class": "URGENT" if i % 4 == 0 else "ROUTINE",
                       "rule_result": rule,
                       "result_json": canonical({"event_id": src["event_id"],
                                                 "zone": "zone_1", "rule": rule}),
                       "work_start_ns": 100 + i * 50,
                       "commit_return_ns": 125 + i * 50,
                       "service_ns": 25, "committed": True})
    m = {"type": "manifest", "scenario": "stage5g_synthetic_sqlite_reference",
         "clock_domain": "single_process_monotonic_ns", "worker_count": 1,
         "journal_mode": "WAL", "synchronous": "FULL",
         "completion_boundary": "sqlite_commit_return", "seed": seed,
         "handler": "context_SQL_lookup + deterministic_rule + one_SQLite_INSERT + commit",
         "planned_unique": 8, "reopen_rows_verified": 8,
         "trace_sha256": hashlib.sha256(canonical(sources).encode()).hexdigest()}
    good = [m, *events]
    assert audit(good)["classes"]["URGENT"]["n"] == 2
    attacks = (
        ("fake_service_duration", 1, "service_ns", 0),
        ("incorrect_rule", 2, "rule_result", "TAMPER_REVIEW"),
        ("overlapping_worker", 3, "work_start_ns", 110),
        ("duplicate_logical_event", 4, "event_id", "s5g_101_00000"),
        ("false_reopen_count", 0, "reopen_rows_verified", 7),
        ("wrong_scenario", 0, "scenario", "stage5e_inproc_base"),
    )
    for name, idx, field, wrong in attacks:
        bad = copy.deepcopy(good)
        bad[idx][field] = wrong
        try:
            audit(bad)
        except AuditError:
            print("PASS rejected", name)
        else:
            raise AssertionError("accepted malformed ledger: " + name)
    print("PASS independent fictional 8-row service ledger + 6/6 deliberate negatives")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("jsonl", nargs="*", type=Path)
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    try:
        if args.self_test:
            self_test()
        else:
            if not args.jsonl:
                p.error("pass one or more Stage 5G JSONL traces, or --self-test")
            runs = [audit(read_jsonl(path)) for path in args.jsonl]
            seeds = [x["seed"] for x in runs]
            check(len(seeds) == len(set(seeds)), "duplicate run seeds; not independent inputs")
            print(json.dumps({"gate": "LAB_ONLY", "independent_seed_traces": len(runs),
                              "runs": runs}, indent=2, sort_keys=True))
    except (AuditError, OSError, ValueError) as exc:
        p.exit(2, "STAGE5G SERVICE AUDIT FAIL: " + str(exc) + "\n")


if __name__ == "__main__":
    main()
