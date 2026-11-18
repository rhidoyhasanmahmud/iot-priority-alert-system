#!/usr/bin/env python3
"""Stage 5H: joint *synthetic lab* MQTT -> finite-K FIFO -> SQLite commit pilot.

Uses the Stage 5G fictional device/context handler and Stage 5E MQTT publisher
helper without modifying earlier experiment modules. This does NOT measure a
real security service, device-origin latency, or a new scheduling algorithm.
"""

import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import time
import uuid

from stage5d_lifecycle_audit import audit
from stage5e_gateway_pilot import (PilotGateway, mqtt_publisher_and_receiver,
                                  now, publish_schedule, scheduled_gaps_ns)
from stage5g_reference_handler import (canonical, fixture_events, open_db,
                                       process_one, validate_source)


class JointGateway(PilotGateway):
    """Same K-waiting-plus-one-active nonpreemptive FIFO with DB-owned worker."""

    def __init__(self, *, db_path, run_id, K, tau_ns, urgent_deadline_offset_ns):
        # Parent constructor starts self._serve on the worker thread.
        self.db_path = db_path
        super().__init__(run_id=run_id, K=K, tau_ns=tau_ns,
                         urgent_deadline_offset_ns=urgent_deadline_offset_ns)

    def receive(self, raw):
        callback = now()  # first statement of gateway callback entry
        aid = "attempt_" + uuid.uuid4().hex
        try:
            source = json.loads(raw)
            cls = validate_source(source)
            eid = source["event_id"]
        except (ValueError, TypeError, UnicodeDecodeError):
            with self.condition:
                self.attempts.append({"type": "attempt", "run_id": self.run_id,
                                      "attempt_id": aid, "event_id": None,
                                      "callback_ns": callback,
                                      "validation_end_ns": now(), "disposition": "INVALID"})
                self.condition.notify_all()
            return

        with self.condition:
            if self.closed:
                raise RuntimeError("callback after joint gateway was closed")
            if eid in self.seen:
                self.attempts.append({"type": "attempt", "run_id": self.run_id,
                                      "attempt_id": aid, "event_id": eid,
                                      "callback_ns": callback,
                                      "validation_end_ns": now(), "disposition": "DUPLICATE"})
                self.condition.notify_all()
                return
            self.seen.add(eid)
            valid_end = now()
            offer_ns = now()  # after validation/dedup, before capacity decision
            busy = self.active is not None
            waiting = len(self.waiting)
            reject = busy and waiting >= self.K
            row = {"type": "offer", "run_id": self.run_id,
                   "event_id": eid, "attempt_id": aid, "trusted_class": cls,
                   "validated_source": source, "offer_ns": offer_ns,
                   "running_at_offer": busy, "waiting_at_offer": waiting,
                   "urgent_deadline_ns": (offer_ns + self.urgent_offset
                                          if cls == "URGENT" else None),
                   "terminal": "REJECTED" if reject else "UNRESOLVED",
                   "start_ns": None, "complete_ns": None}
            self.attempts.append({"type": "attempt", "run_id": self.run_id,
                                  "attempt_id": aid, "event_id": eid,
                                  "callback_ns": callback,
                                  "validation_end_ns": valid_end, "disposition": "OFFERED"})
            self.offers.append(row)
            if not reject:
                job = (row, source)
                if self.active is None:
                    self.active = job
                else:
                    self.waiting.append(job)
            self.condition.notify_all()

    def _serve(self):
        con = None
        try:
            # Connection is created, used and closed in *this* worker thread;
            # no check_same_thread bypass or concurrent SQLite access.
            con = open_db(self.db_path)
            while True:
                with self.condition:
                    while self.active is None:
                        if self.closed:
                            return
                        self.condition.wait()
                    row, source = self.active
                    row["start_ns"] = now()
                result = process_one(con, source)  # lookup/rule/INSERT/commit
                with self.condition:
                    row["db_handler_start_ns"] = result["work_start_ns"]
                    row["db_commit_return_ns"] = result["commit_return_ns"]
                    row["db_service_ns"] = result["service_ns"]
                    row["db_rule_result"] = result["rule_result"]
                    row["db_result_json"] = result["result_json"]
                    row["db_committed"] = result["committed"]
                    row["complete_ns"] = now()
                    row["terminal"] = "COMPLETED"
                    self.active = self.waiting.popleft() if self.waiting else None
                    self.condition.notify_all()
        except Exception as exc:
            with self.condition:
                self.worker_errors.append(repr(exc))
                self.closed = True
                self.condition.notify_all()
        finally:
            if con is not None:
                con.close()


def run_joint(*, transport, shape, count, seed, K, urgent_deadline_ms,
              routine_tau_ms, host="127.0.0.1", port=1883, timeout_s=20,
              sqlite_output=None):
    if not (8 <= count <= 10_000 and 0 <= K <= 10000 and seed >= 0 and
            urgent_deadline_ms > 0 and routine_tau_ms > 0 and timeout_s > 0):
        raise ValueError("invalid synthetic count/K/seed or timing argument")
    run_id = "s5h-" + uuid.uuid4().hex[:14]
    events = fixture_events(seed, count)
    gaps = scheduled_gaps_ns(count, shape)
    source_digest = hashlib.sha256(canonical(events).encode()).hexdigest()
    schedule_digest = hashlib.sha256(canonical(gaps).encode()).hexdigest()
    with tempfile.TemporaryDirectory(prefix="stage5h-joint-") as temp:
        db_path = Path(temp) / "joint.sqlite"
        gateway = JointGateway(db_path=db_path, run_id=run_id, K=K,
                               tau_ns=int(routine_tau_ms * 1e6),
                               urgent_deadline_offset_ns=int(urgent_deadline_ms * 1e6))
        try:
            if transport == "inproc":
                published = publish_schedule(gateway, events, gaps, deliver=gateway.receive)
                receiver_complete = True
                callback_expected = count + count // 13 + 1
            elif transport == "mqtt":
                published, receiver_complete, callback_expected = mqtt_publisher_and_receiver(
                    gateway, events, gaps, host, port, timeout_s)
            else:
                raise ValueError("transport must be inproc or mqtt")
        finally:
            drained, attempts, offers, cutoff = gateway.shutdown_and_drain(timeout_s=timeout_s)

        # Match the publisher's *intended* synthetic inputs to source IDs. The
        # publisher listing is a separate record from receiver-side validation.
        event_by_id = {event["event_id"]: event for event in events}
        for row in published:
            row["source"] = event_by_id[row["event_id"]]

        # A normal reopen after worker close, deliberately outside service spans.
        # Not a power-loss, broker-crash or fsync/hardware durability test.
        con = sqlite3.connect(db_path)
        try:
            saved = {row[0]: row[1:] for row in con.execute(
                "SELECT event_id, trusted_class, rule_result, result_json FROM handled_alerts")}
        finally:
            con.close()
        expected = {row["event_id"]: (row["trusted_class"], row["db_rule_result"],
                                      row["db_result_json"])
                    for row in offers if row["terminal"] == "COMPLETED"}
        db_reopen_exact = saved == expected

        # Explicit, opt-in evidence export for a SECOND process to inspect.
        # SQLite backup API copies a consistent DB image after the handler
        # finishes. Never overwrite existing evidence; this is not crash recovery.
        db_backup_sha256 = None
        if sqlite_output is not None:
            sqlite_output = Path(sqlite_output)
            with sqlite_output.open("xb"):
                pass
            source_con = sqlite3.connect(db_path)
            backup_con = sqlite3.connect(sqlite_output)
            try:
                source_con.backup(backup_con)
            finally:
                backup_con.close()
                source_con.close()
            db_backup_sha256 = hashlib.sha256(sqlite_output.read_bytes()).hexdigest()

    manifest = {"type": "manifest", "run_id": run_id, "policy_id": "fifo",
                "scenario_id": f"stage5h_{transport}_{shape}",
                "trace_provenance": "synthetic_stage5g_fixture_sha256=" + source_digest,
                "source_sha256": source_digest, "schedule_sha256": schedule_digest,
                "seed": seed, "planned_unique": count, "K": K,
                "routine_tau_ns": int(routine_tau_ms * 1e6),
                "observation_end_ns": cutoff,
                "clock_domain": "single_gateway_process_monotonic_ns",
                "dedup_cache_reset": True, "publisher_log_complete": True,
                "receiver_capture_complete": receiver_complete,
                "db_rows_reopened": len(saved), "db_reopen_exact": db_reopen_exact,
                "sqlite_backup_sha256": db_backup_sha256,
                "worker_handler": "stage5g_reference_sqlite_WAL_FULL",
                "completion_boundary": "post_SQLite_commit_return",
                "warning": "synthetic IoT fixture, not real service/deadline calibration"}
    rows = [manifest, *published, *attempts, *offers]
    summary = audit(rows)
    summary.update({"transport": transport, "shape": shape, "source_sha256": source_digest,
                    "drained": drained, "receiver_capture_complete": receiver_complete,
                    "callback_expected": callback_expected,
                    "callback_observed": len(attempts),
                    "db_rows_reopened": len(saved), "db_reopen_exact": db_reopen_exact})
    return rows, summary


def self_test():
    for K in (0, 3):
        for shape in ("base", "burst", "overload"):
            rows, s = run_joint(transport="inproc", shape=shape, count=36,
                                seed=101, K=K, urgent_deadline_ms=50, routine_tau_ms=50)
            assert s["drained"] and s["db_reopen_exact"] and s["offered_unique"] == 36
            assert s["published_unique"] == 36 and s["delivery_attempts"] == 39
            assert s["duplicates"] == 2 and s["invalid_attempts"] == 1
            assert s["db_rows_reopened"] == s["admitted"]
            assert s["unresolved_offers"] == 0
            print(f"PASS joint INPROC K={K} {shape}: offered=36 completed={s['admitted']} "
                  f"rejected={s['rejected']} SQLite rows={s['db_rows_reopened']}")
    print("PASS 6/6 joint in-process SQLite lifecycle smoke; MQTT NOT EXECUTED HERE")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--transport", choices=("inproc", "mqtt"), default="inproc")
    p.add_argument("--shape", choices=("base", "burst", "overload"), default="burst")
    p.add_argument("--events", type=int, default=60)
    p.add_argument("--seed", type=int, default=101)
    p.add_argument("--queue-capacity", type=int, default=3)
    p.add_argument("--urgent-deadline-ms", type=float, default=50)
    p.add_argument("--routine-tau-ms", type=float, default=50)
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=1883)
    p.add_argument("--timeout-s", type=float, default=20)
    p.add_argument("--output", type=Path)
    p.add_argument("--sqlite-output", type=Path,
                   help="independent auditor DB evidence; must not exist")
    args = p.parse_args()
    if args.self_test:
        self_test()
        return
    if args.output is None:
        p.error("--output is required for a recorded pilot")
    rows, summary = run_joint(transport=args.transport, shape=args.shape,
                              count=args.events, seed=args.seed, K=args.queue_capacity,
                              urgent_deadline_ms=args.urgent_deadline_ms,
                              routine_tau_ms=args.routine_tau_ms,
                              host=args.host, port=args.port, timeout_s=args.timeout_s,
                              sqlite_output=args.sqlite_output)
    with args.output.open("x", encoding="utf-8") as file:
        for row in rows:
            file.write(canonical(row) + "\n")
    print(json.dumps({"output": str(args.output), **summary}, indent=2, sort_keys=True))
    if not summary["drained"] or not summary["db_reopen_exact"] or (args.transport == "mqtt" and not summary["receiver_capture_complete"]):
        p.exit(2, "INCOMPLETE joint pilot: diagnostic ledger only; DO NOT treat as passed\n")


if __name__ == "__main__":
    main()
