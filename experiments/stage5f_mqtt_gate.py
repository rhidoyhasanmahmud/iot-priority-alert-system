#!/usr/bin/env python3
"""Stage 5F: offline acceptance gate for one broker-backed MQTT lab ledger.

This does not claim real IoT/security workloads, operational timing budgets,
or statistical results. It only checks a complete small local MQTT transport
reconciliation and reuses the independent Stage 5D lifecycle auditor.
"""

import argparse
import copy
import json
import math
from pathlib import Path

from stage5d_lifecycle_audit import AuditError, audit


def require(condition, message):
    if not condition:
        raise AuditError(message)


def nearest_rank(values, p):
    if not values:
        return None
    values = sorted(values)
    return values[max(0, math.ceil(p * len(values)) - 1)]


def gate(rows, require_mqtt=True):
    summary = audit(rows)  # Independent two-class offered-population ledger check.
    manifest = next(x for x in rows if x["type"] == "manifest")
    if require_mqtt:
        require(manifest["scenario_id"].startswith("stage5e_mqtt_"),
                "this is an in-process fixture, NOT a broker-backed MQTT capture")
    require(manifest["publisher_log_complete"] is True,
            "incomplete publisher log: source population cannot be audited")
    require(manifest["receiver_capture_complete"] is True,
            "missing/extra callbacks or timed-out receiver capture")
    require(summary["published_unique"] == summary["offered_unique"],
            "not all published logical IDs were offered locally")
    require(summary["published_ids_without_callback"] == 0,
            "source logical IDs missing from receiver callback ledger")
    require(summary["unresolved_offers"] == 0,
            "unresolved jobs cannot support a fully drained measurement")
    require(summary["offered_unique"] == summary["admitted"] + summary["rejected"],
            "admission conservation failed")
    require(summary["invalid_attempts"] >= 1, "invalid-input test callback absent")
    require(summary["duplicates"] >= summary["published_unique"] // 13,
            "expected deliberately republished logical events not seen")
    require(summary["urgent_failure_U_bounds"]["exact"] is not None,
            "no exact urgent rate (zero/unknown population)")
    require(summary["routine_timely_start_R_bounds"]["exact"] is not None,
            "no exact routine rate (zero/unknown population)")
    require(summary["measured_completed_service_n"] == summary["admitted"],
            "not all admitted jobs have completed handler durations")

    attempts = {x["attempt_id"]: x for x in rows if x["type"] == "attempt"}
    offered, validate, service, waiting = [], [], [], []
    classes = {"URGENT": 0, "ROUTINE": 0}
    for x in rows:
        if x["type"] != "offer":
            continue
        a = attempts[x["attempt_id"]]
        classes[x["trusted_class"]] += 1
        offered.append(x["offer_ns"] - a["callback_ns"])
        validate.append(x["offer_ns"] - a["validation_end_ns"])
        if x["start_ns"] is not None:
            waiting.append(x["start_ns"] - x["offer_ns"])
            service.append(x["complete_ns"] - x["start_ns"])
    require(all(x >= 0 for x in offered + validate + service + waiting),
            "negative same-process duration")
    require(all(x > 0 for x in service), "synthetic CPU handler has nonpositive duration")

    # Do not compute source->broker->callback latency: existing publisher rows
    # contain logical IDs, NOT a timestamp guaranteed comparable with callback.
    return {
        "status": "LAB_MQTT_LEDGER_GATE_PASS" if require_mqtt else "INPROC_ONLY_SELFTEST_PASS",
        "run_id": summary["run_id"],
        "scenario_id": manifest["scenario_id"],
        "source_unique": summary["published_unique"],
        "callback_attempts": summary["delivery_attempts"],
        "duplicates": summary["duplicates"],
        "invalid": summary["invalid_attempts"],
        "offered_unique": summary["offered_unique"],
        "admitted": summary["admitted"],
        "rejected": summary["rejected"],
        "offered_classes": classes,
        "urgent_U_debug_only": summary["urgent_failure_U_bounds"]["exact"],
        "routine_R_debug_only": summary["routine_timely_start_R_bounds"]["exact"],
        "callback_to_offer_p95_ns": nearest_rank(offered, .95),
        "validation_end_to_offer_p95_ns": nearest_rank(validate, .95),
        "queue_wait_for_completed_p95_ns": nearest_rank(waiting, .95),
        "synthetic_cpu_handler_service_p95_ns": nearest_rank(service, .95),
        "warning": "single lab run only; no MQTT network-latency separation, service realism, QoS guarantee, operational budget or research performance claim",
    }


def read_jsonl(path):
    return [json.loads(s) for s in path.read_text(encoding="utf-8").splitlines() if s.strip()]


def self_test(sample_path):
    rows = read_jsonl(sample_path)
    x = gate(rows, require_mqtt=False)
    assert x["offered_unique"] == 36 and x["callback_attempts"] == 39
    assert x["rejected"] == 9 and x["admitted"] == 27
    print("PASS offline in-process fixture general lifecycle checks")
    try:
        gate(rows, require_mqtt=True)
    except AuditError:
        print("PASS refused to relabel in-process fixture as broker-backed MQTT evidence")
    else:
        raise AssertionError("accepted non-MQTT fixture as MQTT evidence")

    damaged = copy.deepcopy(rows)
    for r in damaged:
        if r["type"] == "manifest":
            r["receiver_capture_complete"] = False
            break
    try:
        gate(damaged, require_mqtt=False)
    except AuditError:
        print("PASS refused an incomplete receiver capture")
    else:
        raise AssertionError("accepted incomplete receiver capture")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("jsonl", nargs="?", type=Path)
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--test-fixture", type=Path,
                   default=Path(__file__).parent / "fixtures" / "stage5e_inproc_burst_k3_debug.jsonl")
    args = p.parse_args()
    try:
        if args.self_test:
            self_test(args.test_fixture)
        else:
            if args.jsonl is None:
                p.error("pass a captured Stage 5E MQTT JSONL path or --self-test")
            print(json.dumps(gate(read_jsonl(args.jsonl), require_mqtt=True),
                             indent=2, sort_keys=True))
    except (AuditError, OSError, ValueError) as exc:
        p.exit(2, f"STAGE5F GATE FAIL: {exc}\n")


if __name__ == "__main__":
    main()
