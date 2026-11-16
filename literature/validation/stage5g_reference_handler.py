#!/usr/bin/env python3
"""Stage 5G: provisional *laboratory* IoT alert handler service-time probe.

One worker, validated fictional tamper/health input, deterministic context lookup,
rule evaluation and an individual SQLite WAL/FULL transaction per alert. Not
real device input, security classification, SLA calibration or scheduling data.

The worker interval starts immediately before context lookup and ends after
Connection.commit() returns. It excludes MQTT/validation/queue/publisher time.
"""

import argparse
import hashlib
import json
from pathlib import Path
import platform
import random
import sqlite3
import sys
import tempfile
import time


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def fixture_events(seed, count):
    rng = random.Random(seed)
    records = []
    for i in range(count):
        tamper = i % 4 == 0
        records.append({
            "event_id": f"s5g_{seed}_{i:05d}",
            "device_id": f"device_{rng.randrange(16):02d}",
            "kind": "tamper" if tamper else "health",
            "tamper": tamper,
            "battery_pct": rng.randrange(101),
        })
    return records


def validate_source(value):
    if not isinstance(value, dict) or set(value) != {
        "event_id", "device_id", "kind", "tamper", "battery_pct"
    }:
        raise ValueError("unexpected trusted-fixture schema")
    if not isinstance(value["event_id"], str) or not value["event_id"]:
        raise ValueError("invalid event ID")
    if not isinstance(value["device_id"], str) or not value["device_id"]:
        raise ValueError("invalid device ID")
    if value["kind"] not in ("tamper", "health"):
        raise ValueError("unexpected alert kind")
    if type(value["tamper"]) is not bool or value["tamper"] != (value["kind"] == "tamper"):
        raise ValueError("inconsistent class flag")
    if type(value["battery_pct"]) is not int or not 0 <= value["battery_pct"] <= 100:
        raise ValueError("invalid battery percent")
    return "URGENT" if value["kind"] == "tamper" else "ROUTINE"


def open_db(path):
    con = sqlite3.connect(path, timeout=10, isolation_level=None)
    mode = con.execute("PRAGMA journal_mode=WAL").fetchone()[0]
    con.execute("PRAGMA synchronous=FULL")
    sync = con.execute("PRAGMA synchronous").fetchone()[0]
    if mode.lower() != "wal" or sync != 2:
        con.close()
        raise RuntimeError(f"unexpected SQLite durability configuration: {mode}, {sync}")
    con.executescript("""
        CREATE TABLE device_context (
            device_id TEXT PRIMARY KEY, site_zone TEXT NOT NULL,
            alert_enabled INTEGER NOT NULL
        );
        CREATE TABLE handled_alerts (
            event_id TEXT PRIMARY KEY, device_id TEXT NOT NULL,
            trusted_class TEXT NOT NULL, rule_result TEXT NOT NULL,
            result_json TEXT NOT NULL
        );
    """)
    con.executemany(
        "INSERT INTO device_context VALUES (?, ?, ?)",
        [(f"device_{i:02d}", f"zone_{i % 4}", 0 if i % 5 == 0 else 1)
         for i in range(16)],
    )
    return con


def process_one(con, source):
    """Process one already validated event; interval includes transactional commit."""
    cls = validate_source(source)  # explicitly outside the timed worker interval
    start = time.monotonic_ns()
    con.execute("BEGIN IMMEDIATE")
    try:
        context = con.execute(
            "SELECT site_zone, alert_enabled FROM device_context WHERE device_id=?",
            (source["device_id"],),
        ).fetchone()
        if context is None:
            raise ValueError("unknown fictional device context")
        zone, enabled = context
        if cls == "URGENT":
            rule = "TAMPER_REVIEW" if enabled else "TAMPER_DISABLED"
        else:
            rule = "LOW_BATTERY" if source["battery_pct"] < 20 else "HEALTHY"
        result = canonical({"event_id": source["event_id"], "zone": zone, "rule": rule})
        con.execute("INSERT INTO handled_alerts VALUES (?, ?, ?, ?, ?)",
                    (source["event_id"], source["device_id"], cls, rule, result))
        con.commit()
    except Exception:
        con.rollback()
        raise
    complete = time.monotonic_ns()
    return {
        "type": "handled", "event_id": source["event_id"], "source": source,
        "trusted_class": cls, "rule_result": rule, "result_json": result,
        "work_start_ns": start, "commit_return_ns": complete,
        "service_ns": complete - start, "committed": True,
    }


def run_one(seed, count):
    events = fixture_events(seed, count)
    trace_hash = hashlib.sha256(canonical(events).encode()).hexdigest()
    with tempfile.TemporaryDirectory(prefix="s5g-sqlite-") as tmp:
        db = Path(tmp) / "alerts.sqlite"
        con = open_db(db)
        try:
            records = []
            for event in events:
                records.append(process_one(con, event))
        finally:
            con.close()

        # Reopen and verify, outside the measured service windows. This is a
        # normal close/reopen check, NOT a crash/power-loss durability test.
        con = sqlite3.connect(db)
        try:
            persisted = con.execute("SELECT event_id, trusted_class, rule_result, result_json "
                                    "FROM handled_alerts ORDER BY event_id").fetchall()
            expected = sorted((r["event_id"], r["trusted_class"], r["rule_result"],
                               r["result_json"]) for r in records)
            if persisted != expected:
                raise RuntimeError("reopened SQLite records differ from handled ledger")
        finally:
            con.close()

    manifest = {
        "type": "manifest", "scenario": "stage5g_synthetic_sqlite_reference",
        "seed": seed, "planned_unique": count, "trace_sha256": trace_hash,
        "clock_domain": "single_process_monotonic_ns", "worker_count": 1,
        "journal_mode": "WAL", "synchronous": "FULL",
        "completion_boundary": "sqlite_commit_return",
        "reopen_rows_verified": len(records),
        "handler": "context_SQL_lookup + deterministic_rule + one_SQLite_INSERT + commit",
        "host": {"python": platform.python_version(), "sqlite": sqlite3.sqlite_version,
                 "platform": platform.system(), "release": platform.release(),
                 "logical_cpus": __import__("os").cpu_count()},
        "claim_scope": "one-machine illustrative lab handler only; NO field/SLA calibration",
    }
    return [manifest, *records]


def self_test():
    with tempfile.TemporaryDirectory(prefix="s5g-handler-selftest-") as tmp:
        db = Path(tmp) / "test.sqlite"
        con = open_db(db)
        try:
            cases = [
                {"event_id": "u1", "device_id": "device_01", "kind": "tamper",
                 "tamper": True, "battery_pct": 90},
                {"event_id": "r1", "device_id": "device_02", "kind": "health",
                 "tamper": False, "battery_pct": 10},
                {"event_id": "r2", "device_id": "device_05", "kind": "health",
                 "tamper": False, "battery_pct": 90},
            ]
            result = [process_one(con, x) for x in cases]
            assert [x["rule_result"] for x in result] == ["TAMPER_REVIEW", "LOW_BATTERY", "HEALTHY"]
            try:
                process_one(con, cases[0])
            except sqlite3.IntegrityError:
                pass
            else:
                raise AssertionError("duplicate not rejected")
            bad = dict(cases[1], event_id="bad", battery_pct=True)
            try:
                process_one(con, bad)
            except ValueError:
                pass
            else:
                raise AssertionError("bool percentage passed validation")
            unknown = dict(cases[1], event_id="unknown", device_id="device_99")
            try:
                process_one(con, unknown)
            except ValueError:
                pass
            else:
                raise AssertionError("unknown device not rejected")
            assert con.execute("SELECT COUNT(*) FROM handled_alerts").fetchone()[0] == 3
        finally:
            con.close()
        con = sqlite3.connect(db)
        try:
            assert con.execute("SELECT COUNT(*) FROM handled_alerts").fetchone()[0] == 3
        finally:
            con.close()
    for seed in (101, 202):
        rows = run_one(seed, 12)
        assert len(rows) == 13 and rows[0]["reopen_rows_verified"] == 12
    print("PASS handler: 3 rule cases, transactional duplicate/invalid/unknown rollback")
    print("PASS SQLite close/reopen persistence, WAL/FULL, two seed traces; NO crash test")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--seeds", type=int, nargs="+", default=[101, 202, 303])
    p.add_argument("--events", type=int, default=120)
    p.add_argument("--output-dir", type=Path)
    args = p.parse_args()
    if args.self_test:
        self_test()
        return
    if args.output_dir is None or not 8 <= args.events <= 10000:
        p.error("provide --output-dir and 8<=--events<=10000")
    if len(args.seeds) != len(set(args.seeds)) or any(s < 0 for s in args.seeds):
        p.error("seeds must be distinct nonnegative integers")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for seed in args.seeds:
        rows = run_one(seed, args.events)
        out = args.output_dir / f"stage5g_sqlite_seed{seed}.jsonl"
        # No implicit overwrite of existing experimental evidence.
        with out.open("x", encoding="utf-8") as file:
            for row in rows:
                file.write(canonical(row) + "\n")
        print(f"Saved SYNTHETIC ONLY, {len(rows)-1} completed handler calls: {out}")
    print("NOT a field service-time distribution or research result")


if __name__ == "__main__":
    main()
