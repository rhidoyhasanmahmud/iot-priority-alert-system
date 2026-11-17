#!/usr/bin/env python3
"""Stage 10 ENGINEERING PILOT: bounded priority recovery vs matched baselines.

Separate, post-Stage9 experimental ideas. Neither the Stage9 frozen algorithm
nor its held-out observations are modified. This uses an explicitly additional
SQLite-backed overflow capacity B. Persisting/replaying a displaced alert is
NOT a free same-capacity scheduling win, nor a crash-restart demonstration.
"""
from __future__ import annotations

import argparse
from collections import deque
import hashlib
import json
from pathlib import Path
import sqlite3
import statistics
import tempfile
import uuid

from stage5e_gateway_pilot import mqtt_publisher_and_receiver, now, publish_schedule
from stage5g_reference_handler import canonical, open_db, process_one, validate_source
from stage5k2_independent_audit import audit as fixture_audit
from stage7_controlled_replay import PolicyGateway, source_payload


POLICIES = {
    "pushout_slack",          # K3 + one worker, NO extra capacity; victim cancelled
    "fifo_deferred",          # K3 + B, equal extra buffer comparator
    "strict_deferred",        # K3 + B, equal extra buffer comparator
    "pushout_deferred",       # K3 + B, victim preserved to durable overflow
    "pushout_reserved_deferred", # K3 + B, up to B//2 new routines + displaced victims
    "pushout_slack_deferred", # K3 + B, both interventions
}


class Stage10Gateway(PolicyGateway):
    """A strictly bounded B overflow + K waiting, with one actual worker.

    The parent starts the worker thread. Initialize every extra field before
    invoking it; all mutable queue state is subsequently condition-protected.
    """

    def __init__(self, *, db_path: Path, spool_path: Path, run_id: str,
                 K: int, B: int, policy: str, hidden_work: list[dict],
                 iterations_per_unit: int, urgent_deadline_ns: int,
                 routine_tau_ns: int, slack_guard_ns: int = 3_000_000):
        if policy not in POLICIES or K < 0 or B < 0 or slack_guard_ns < 0:
            raise ValueError("Invalid Stage 10 pilot policy or capacities")
        if policy == "pushout_slack" and B != 0:
            raise ValueError("The no-extra-capacity ablation requires B=0")
        if policy != "pushout_slack" and B == 0:
            raise ValueError("Deferred variants require explicitly positive bounded B")
        self.stage10_policy = policy
        self.B = B
        self.spool_path = spool_path
        self.deferred: deque[tuple[dict, dict]] = deque()
        self.spool_peak = 0
        self.slack_guard_ns = slack_guard_ns
        self.history: list[tuple[str, int]] = []
        self.spool_count_all = 0
        self.spool_count_completed = 0
        spool_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(spool_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=FULL")
            conn.execute("""CREATE TABLE deferred_alerts (
                event_id TEXT PRIMARY KEY, trusted_class TEXT NOT NULL,
                reason TEXT NOT NULL, defer_ns INTEGER NOT NULL,
                claim_ns INTEGER, completed_ns INTEGER,
                state TEXT NOT NULL CHECK (state IN ('PENDING','CLAIMED','COMPLETED'))
            )""")
        super().__init__(db_path=db_path, run_id=run_id, K=K,
                         policy="strict_urgent_first", hidden_work=hidden_work,
                         iterations_per_unit=iterations_per_unit,
                         urgent_deadline_ns=urgent_deadline_ns,
                         routine_tau_ns=routine_tau_ns)

    def _persist_deferred(self, job: tuple[dict, dict], *, reason: str) -> None:
        """Durable INSERT *before* in-memory state changes or MQTT ack."""
        if len(self.deferred) >= self.B:
            raise RuntimeError("Bounded overflow full; cannot defer")
        row = job[0]
        stamp = now()
        with sqlite3.connect(self.spool_path, timeout=5.0) as conn:
            conn.execute("INSERT INTO deferred_alerts VALUES (?,?,?,?,?,?,?)",
                         (row["event_id"], row["trusted_class"], reason,
                          stamp, None, None, "PENDING"))
        row["defer_reason"] = reason
        row["defer_ns"] = stamp
        row["was_deferred"] = True
        self.deferred.append(job)
        self.spool_count_all += 1
        self.spool_peak = max(self.spool_peak, len(self.deferred))

    def receive(self, raw: bytes) -> None:
        callback = now()
        attempt_id = "attempt_" + uuid.uuid4().hex
        try:
            source = json.loads(raw)
            cls = validate_source(source)
            eid = source["event_id"]
        except (ValueError, TypeError, UnicodeDecodeError):
            with self.condition:
                self.attempts.append({"type": "attempt", "run_id": self.run_id,
                                      "attempt_id": attempt_id, "event_id": None,
                                      "callback_ns": callback,
                                      "validation_end_ns": now(), "disposition": "INVALID"})
                self.condition.notify_all()
            return
        with self.condition:
            if self.closed:
                raise RuntimeError("Callback after Stage 10 gateway closed")
            if eid in self.seen:
                self.attempts.append({"type": "attempt", "run_id": self.run_id,
                                      "attempt_id": attempt_id, "event_id": eid,
                                      "callback_ns": callback,
                                      "validation_end_ns": now(), "disposition": "DUPLICATE"})
                self.condition.notify_all()
                return
            self.seen.add(eid)
            validation_end = now()
            offered = now()
            waiting_ids = [row["event_id"] for row, _ in self.waiting]
            deferred_ids = [row["event_id"] for row, _ in self.deferred]
            active_id = self.active[0]["event_id"] if self.active else None
            full = self.active is not None and len(self.waiting) >= self.K
            pushout = self.stage10_policy.startswith("pushout_")
            victim = None
            if not full:
                action = "ADMIT_MAIN"
            elif pushout and cls == "URGENT":
                routine_indexes = [i for i, (row, _) in enumerate(self.waiting)
                                   if row["trusted_class"] == "ROUTINE"]
                if routine_indexes:
                    idx = routine_indexes[-1]
                    victim_job = self.waiting[idx]
                    victim = victim_job[0]["event_id"]
                    if self.B == 0 or len(self.deferred) >= self.B:
                        # Keep the Stage 9 urgent admission decision when the
                        # bounded recovery resource is exhausted. Every lost
                        # routine remains an offered-population failure.
                        victim_job[0]["terminal"] = "CANCELLED"
                        victim_job[0]["eviction_ns"] = now()
                        victim_job[0]["evicted_by_id"] = eid
                        action = "PUSHOUT_DROP_ADMIT"
                    else:
                        self._persist_deferred(victim_job, reason="URGENT_PUSHOUT")
                        victim_job[0]["evicted_by_id"] = eid
                        action = "PUSHOUT_DEFER_ADMIT"
                    del self.waiting[idx]
                else:
                    action = "REJECT_CAPACITY"
            elif pushout:
                # Reservation ablation: accept some overflow routines while
                # retaining at least half of B for future urgent pushouts.
                # Once B fills, later urgent pushout still cancels victims.
                if (self.stage10_policy == "pushout_reserved_deferred" and
                        len(self.deferred) < self.B // 2):
                    action = "DEFER_NEW"
                else:
                    action = "REJECT_CAPACITY"
            elif len(self.deferred) < self.B:
                action = "DEFER_NEW"
            else:
                action = "REJECT_CAPACITY"

            row = {"type": "offer", "run_id": self.run_id, "event_id": eid,
                   "attempt_id": attempt_id, "trusted_class": cls,
                   "validated_source": source, "offer_ns": offered,
                   "running_at_offer": active_id is not None,
                   "waiting_at_offer": len(waiting_ids),
                   "deferred_at_offer": len(deferred_ids),
                   "admission_active_id": active_id,
                   "admission_waiting_ids": waiting_ids,
                   "admission_deferred_ids": deferred_ids,
                   "admission_action": action,
                   "pushout_victim_id": victim,
                   "urgent_deadline_ns": offered + self.urgent_offset if cls == "URGENT" else None,
                   "terminal": "REJECTED" if action == "REJECT_CAPACITY" else "UNRESOLVED",
                   "was_deferred": False, "start_ns": None, "complete_ns": None}
            self.attempts.append({"type": "attempt", "run_id": self.run_id,
                                  "attempt_id": attempt_id, "event_id": eid,
                                  "callback_ns": callback, "validation_end_ns": validation_end,
                                  "disposition": "OFFERED"})
            self.offers.append(row)
            if action in {"ADMIT_MAIN", "PUSHOUT_DROP_ADMIT", "PUSHOUT_DEFER_ADMIT"}:
                if self.active is None:
                    self.active = (row, source)
                else:
                    self.waiting.append((row, source))
            elif action == "DEFER_NEW":
                self._persist_deferred((row, source), reason="BUFFER_OVERFLOW")
            self.condition.notify_all()

    def _estimate_ns(self, cls: str) -> int:
        durations = [d for c, d in self.history if c == cls]
        if len(durations) < 3:
            return 15_000_000  # fixed conservative warm-up assumption, not hidden work
        values = sorted(durations[-16:])
        return values[int((len(values) - 1) * 0.90)]

    def _select_next(self):
        stamp = now()
        if self.waiting:
            snapshot = [{"event_id": row["event_id"], "trusted_class": row["trusted_class"]}
                        for row, _ in self.waiting]
            urgent_indexes = [i for i, (row, _) in enumerate(self.waiting)
                              if row["trusted_class"] == "URGENT"]
            routine_indexes = [i for i, (row, _) in enumerate(self.waiting)
                               if row["trusted_class"] == "ROUTINE"]
            if self.stage10_policy == "fifo_deferred":
                idx = 0
                reason = "fifo_policy_selection"
            elif "slack" in self.stage10_policy and urgent_indexes and routine_indexes:
                earliest = min(self.waiting[i][0]["urgent_deadline_ns"] for i in urgent_indexes)
                estimate = self._estimate_ns("ROUTINE") + self._estimate_ns("URGENT")
                slack = earliest - stamp - estimate - self.slack_guard_ns
                idx = routine_indexes[0] if slack > 0 else urgent_indexes[0]
                reason = "slack_policy_selection"
            else:
                idx = urgent_indexes[0] if urgent_indexes else 0
                reason = "strict_urgent_policy_selection"
            job = self.waiting[idx]
            del self.waiting[idx]
            job[0]["dispatch_snapshot"] = snapshot
            job[0]["dispatch_reason"] = reason
            job[0]["dispatch_choice_ns"] = stamp
            return job
        if self.deferred:
            # A recovered job gets service only after the main waiting queue
            # empties; B is an actual extra capacity, not free priority.
            idx = 0
            if self.stage10_policy != "fifo_deferred":
                idx = next((i for i, (row, _) in enumerate(self.deferred)
                            if row["trusted_class"] == "URGENT"), 0)
            snapshot = [row["event_id"] for row, _ in self.deferred]
            job = self.deferred[idx]
            del self.deferred[idx]
            row = job[0]
            with sqlite3.connect(self.spool_path, timeout=5.0) as conn:
                updated = conn.execute(
                    "UPDATE deferred_alerts SET state='CLAIMED', claim_ns=? "
                    "WHERE event_id=? AND state='PENDING'", (stamp, row["event_id"])).rowcount
            if updated != 1:
                raise RuntimeError("Deferred row could not be claimed exactly once")
            row["dispatch_reason"] = "deferred_recovery"
            row["dispatch_snapshot"] = [{"event_id": x} for x in snapshot]
            row["dispatch_choice_ns"] = stamp
            return job
        return None

    def _serve(self):
        con = None
        try:
            con = open_db(self.db_path)
            while True:
                with self.condition:
                    while self.active is None:
                        if self.closed:
                            return
                        self.condition.wait()
                    row, source = self.active
                    if "dispatch_reason" not in row:
                        row["dispatch_reason"] = "direct_admission"
                        row["dispatch_snapshot"] = []
                        row["dispatch_choice_ns"] = now()
                    row["start_ns"] = now()
                # Only the worker may read hidden required work, AFTER dispatch.
                units = self.synthetic_work_by_id[row["event_id"]]
                started = now()
                digest = hashlib.pbkdf2_hmac(
                    "sha256", row["event_id"].encode(),
                    b"STAGE7-ARTIFICIAL-WORK-NOT-AN-IOT-PROFILE",
                    units * self.iterations_per_unit)
                elapsed_cpu = now() - started
                if len(digest) != 32:
                    raise RuntimeError("Synthetic CPU work failed")
                result = process_one(con, source)
                with self.condition:
                    if row["was_deferred"]:
                        stamp = now()
                        with sqlite3.connect(self.spool_path, timeout=5.0) as spool:
                            changed = spool.execute(
                                "UPDATE deferred_alerts SET state='COMPLETED', completed_ns=? "
                                "WHERE event_id=? AND state='CLAIMED'",
                                (stamp, row["event_id"])).rowcount
                        if changed != 1:
                            raise RuntimeError("Deferred recovery not completed exactly once")
                        self.spool_count_completed += 1
                    row["synthetic_work_units_post_dispatch"] = units
                    row["synthetic_cpu_iterations"] = units * self.iterations_per_unit
                    row["synthetic_cpu_service_ns"] = elapsed_cpu
                    row["db_handler_start_ns"] = result["work_start_ns"]
                    row["db_commit_return_ns"] = result["commit_return_ns"]
                    row["db_service_ns"] = result["service_ns"]
                    row["db_rule_result"] = result["rule_result"]
                    row["db_result_json"] = result["result_json"]
                    row["db_committed"] = result["committed"]
                    row["complete_ns"] = now()
                    row["terminal"] = "COMPLETED"
                    self.history.append((row["trusted_class"], elapsed_cpu + result["service_ns"]))
                    self.active = self._select_next()
                    self.condition.notify_all()
        except Exception as exc:
            with self.condition:
                self.worker_errors.append(repr(exc))
                self.closed = True
                self.condition.notify_all()
        finally:
            if con is not None:
                con.close()


def _backup_db(src_path: Path, dst_path: Path) -> str:
    with dst_path.open("xb"):
        pass
    src, dst = sqlite3.connect(src_path), sqlite3.connect(dst_path)
    try:
        src.backup(dst)
    finally:
        dst.close()
        src.close()
    return hashlib.sha256(dst_path.read_bytes()).hexdigest()


def run_case(*, fixture_dir: Path, policy: str, B: int, K: int,
             iterations_per_unit: int, urgent_deadline_ms: float,
             routine_tau_ms: float, sqlite_output: Path, spool_output: Path,
             transport: str = "inproc", timeout_s: float = 35.0,
             host: str = "127.0.0.1", port: int = 1883):
    fixture = fixture_audit(fixture_dir)
    sources = [source_payload(x) for x in fixture["offers"]]
    offsets = [x["planned_offer_offset_ns"] for x in fixture["offers"]]
    gaps = [offsets[0], *(b-a for a,b in zip(offsets, offsets[1:]))]
    run_id = "s10-" + uuid.uuid4().hex[:16]
    with tempfile.TemporaryDirectory(prefix="stage10-pilot-") as temp:
        workdb, spooldb = Path(temp) / "handled.sqlite", Path(temp) / "spool.sqlite"
        gateway = Stage10Gateway(db_path=workdb, spool_path=spooldb,
                                 run_id=run_id, K=K, B=B, policy=policy,
                                 hidden_work=fixture["hidden"],
                                 iterations_per_unit=iterations_per_unit,
                                 urgent_deadline_ns=int(urgent_deadline_ms * 1e6),
                                 routine_tau_ns=int(routine_tau_ms * 1e6))
        try:
            if transport == "inproc":
                published = publish_schedule(gateway, sources, gaps, deliver=gateway.receive)
                receiver_complete = True
            elif transport == "mqtt":
                published, receiver_complete, _ = mqtt_publisher_and_receiver(
                    gateway, sources, gaps, host, port, timeout_s)
            else:
                raise ValueError("Invalid transport")
        finally:
            drained, attempts, offered, cutoff = gateway.shutdown_and_drain(timeout_s=timeout_s)
        if not drained or not receiver_complete or gateway.deferred:
            raise RuntimeError("Stage10 trial incomplete; deferred not drained")
        with sqlite3.connect(workdb) as db:
            stored = {r[0]: tuple(r[1:]) for r in db.execute(
                "SELECT event_id, trusted_class, rule_result, result_json FROM handled_alerts")}
        expected = {r["event_id"]: (r["trusted_class"], r["db_rule_result"], r["db_result_json"])
                    for r in offered if r["terminal"] == "COMPLETED"}
        if stored != expected:
            raise RuntimeError("Stage10 handler DB differs from completed jobs")
        worker_sha = _backup_db(workdb, sqlite_output)
        spool_sha = _backup_db(spooldb, spool_output)

    by_id = {x["event_id"]: x for x in sources}
    for p in published:
        p["source"] = by_id[p["event_id"]]
    fmanifest = json.loads((fixture_dir / "manifest.json").read_text())
    rows = [{"type": "manifest", "run_id": run_id,
             "policy_id": policy, "scenario_id": "stage10_pilot_"+transport,
             "study_status": "STAGE10_TUNING_ONLY_NO_INFERENCE",
             "K": K, "B": B,
             "source_sha256": hashlib.sha256(canonical(sources).encode()).hexdigest(),
             "schedule_sha256": hashlib.sha256(canonical(gaps).encode()).hexdigest(),
             "fixture_id": fmanifest["fixture_id"],
             "offer_fixture_sha256": fmanifest["offer_sha256"],
             "hidden_work_sha256": fmanifest["hidden_work_sha256"],
             "synthetic_iterations_per_work_unit": iterations_per_unit,
             "urgent_deadline_offset_ns": int(urgent_deadline_ms * 1e6),
             "routine_tau_ns": int(routine_tau_ms * 1e6),
             "worker_sqlite_sha256": worker_sha, "spool_sqlite_sha256": spool_sha,
             "spool_peak": gateway.spool_peak,
             "spool_total_inserted": gateway.spool_count_all,
             "spool_total_completed": gateway.spool_count_completed,
             "new_routine_overflow_limit": (B // 2 if policy == "pushout_reserved_deferred" else 0),
             "observation_end_ns": cutoff,
             "additional_capacity_declared": B > 0,
             "slack_guard_ns": gateway.slack_guard_ns,
             "slack_estimator": "PREVIOUS_COMPLETED_CLASS_SERVICE_P90_16_WINDOW_15MS_WARMUP",
             "transport": transport,
             "field_calibrated": False,
             "algorithm_novelty_verified": False},
            *published, *attempts, *offered]
    urgent = [r for r in offered if r["trusted_class"] == "URGENT"]
    routine = [r for r in offered if r["trusted_class"] == "ROUTINE"]
    summary = {
        "policy": policy, "K": K, "B": B,
        "offered": len(offered),
        "completed": len(expected),
        "rejected": sum(x["terminal"] == "REJECTED" for x in offered),
        "cancelled": sum(x["terminal"] == "CANCELLED" for x in offered),
        "U": sum(x["terminal"] != "COMPLETED" or
                 x["complete_ns"] > x["urgent_deadline_ns"] for x in urgent)/len(urgent),
        "R": sum(x["terminal"] == "COMPLETED" and
                 x["start_ns"] <= x["offer_ns"] + int(routine_tau_ms*1e6)
                 for x in routine)/len(routine),
        "C": sum(x["terminal"] == "COMPLETED" for x in routine)/len(routine),
        "spool_peak": gateway.spool_peak,
        "spool_inserted": gateway.spool_count_all,
        "spool_completed": gateway.spool_count_completed,
    }
    return rows, summary


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--fixture-dir", type=Path, required=True)
    p.add_argument("--policy", required=True, choices=sorted(POLICIES))
    p.add_argument("--K", type=int, default=3)
    p.add_argument("--B", type=int, default=8)
    p.add_argument("--transport", choices=["inproc", "mqtt"], default="inproc")
    p.add_argument("--iterations-per-unit", type=int, default=10000)
    p.add_argument("--urgent-deadline-ms", type=float, default=50)
    p.add_argument("--routine-tau-ms", type=float, default=20)
    p.add_argument("--timeout-s", type=float, default=35)
    p.add_argument("--sqlite-output", type=Path, required=True)
    p.add_argument("--spool-output", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    rows, result = run_case(fixture_dir=a.fixture_dir, policy=a.policy,
                            K=a.K, B=a.B, transport=a.transport,
                            iterations_per_unit=a.iterations_per_unit,
                            urgent_deadline_ms=a.urgent_deadline_ms,
                            routine_tau_ms=a.routine_tau_ms,
                            sqlite_output=a.sqlite_output, spool_output=a.spool_output,
                            timeout_s=a.timeout_s)
    with a.output.open("x", encoding="utf-8") as out:
        for row in rows:
            out.write(canonical(row)+"\n")
    print(json.dumps({"status":"STAGE10_RESERVED_PILOT_ONLY",**result},sort_keys=True))


if __name__ == "__main__":
    main()
