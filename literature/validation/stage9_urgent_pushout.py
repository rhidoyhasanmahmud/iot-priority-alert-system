#!/usr/bin/env python3
"""Experimental, NON-NOVEL urgent push-out admission with strict urgent dispatch.

This explicitly changes *admission* relative to Stage 8, so it is not evidence
that a scheduling-only change dominates unchanged-admission FIFO/priority.
All cancelled routine offers remain failures in the offered-population R metric.
The Stage 8 frozen study and auditors are never modified.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import uuid

from stage5e_gateway_pilot import mqtt_publisher_and_receiver, now, publish_schedule
from stage5g_reference_handler import canonical, validate_source
from stage5k2_independent_audit import audit as fixture_audit
from stage7_controlled_replay import PolicyGateway, source_payload


CANDIDATE = "urgent_pushout_strict"
ADMISSION_RULE = "FULL_URGENT_REPLACES_NEWEST_WAITING_ROUTINE_NONPREEMPTIVE"


class UrgentPushoutGateway(PolicyGateway):
    """Urgent-space protection; no interrupt of active/nonpreemptive service."""

    def __init__(self, *, db_path: Path, run_id: str, K: int,
                 hidden_work: list[dict], iterations_per_unit: int,
                 urgent_deadline_ns: int, routine_tau_ns: int):
        super().__init__(db_path=db_path, run_id=run_id, K=K,
                         policy="strict_urgent_first", hidden_work=hidden_work,
                         iterations_per_unit=iterations_per_unit,
                         urgent_deadline_ns=urgent_deadline_ns,
                         routine_tau_ns=routine_tau_ns)

    def receive(self, raw: bytes) -> None:
        callback_ns = now()
        attempt_id = "attempt_" + uuid.uuid4().hex
        try:
            source = json.loads(raw)
            trusted_class = validate_source(source)
            event_id = source["event_id"]
        except (ValueError, TypeError, UnicodeDecodeError):
            with self.condition:
                self.attempts.append({"type": "attempt", "run_id": self.run_id,
                                      "attempt_id": attempt_id, "event_id": None,
                                      "callback_ns": callback_ns,
                                      "validation_end_ns": now(), "disposition": "INVALID"})
                self.condition.notify_all()
            return

        with self.condition:
            if self.closed:
                raise RuntimeError("Synthetic gateway callback after shutdown")
            if event_id in self.seen:
                self.attempts.append({"type": "attempt", "run_id": self.run_id,
                                      "attempt_id": attempt_id, "event_id": event_id,
                                      "callback_ns": callback_ns,
                                      "validation_end_ns": now(), "disposition": "DUPLICATE"})
                self.condition.notify_all()
                return
            self.seen.add(event_id)
            validation_end_ns = now()
            offer_ns = now()
            active_id = self.active[0]["event_id"] if self.active is not None else None
            waiting_snapshot = [pair[0]["event_id"] for pair in self.waiting]
            full = self.active is not None and len(self.waiting) >= self.K
            victim_id = None
            if not full:
                action = "ADMIT"
            elif trusted_class == "URGENT":
                candidate_victims = [i for i, (row, _) in enumerate(self.waiting)
                                     if row["trusted_class"] == "ROUTINE"]
                if candidate_victims:
                    # Right-most is youngest; protect older routine waiting age.
                    victim_index = candidate_victims[-1]
                    victim, _ = self.waiting[victim_index]
                    del self.waiting[victim_index]
                    victim["terminal"] = "CANCELLED"
                    victim["eviction_ns"] = now()
                    victim["evicted_by_id"] = event_id
                    victim_id = victim["event_id"]
                    action = "PUSHOUT_ADMIT"
                else:
                    action = "REJECT_FULL"
            else:
                action = "REJECT_FULL"

            row = {"type": "offer", "run_id": self.run_id,
                   "event_id": event_id, "attempt_id": attempt_id,
                   "trusted_class": trusted_class, "validated_source": source,
                   "offer_ns": offer_ns, "running_at_offer": active_id is not None,
                   "waiting_at_offer": len(waiting_snapshot),
                   "admission_active_id": active_id,
                   "admission_waiting_ids": waiting_snapshot,
                   "admission_action": action,
                   "pushout_victim_id": victim_id,
                   "urgent_deadline_ns": (offer_ns + self.urgent_offset
                                          if trusted_class == "URGENT" else None),
                   "terminal": "REJECTED" if action == "REJECT_FULL" else "UNRESOLVED",
                   "start_ns": None, "complete_ns": None}
            self.attempts.append({"type": "attempt", "run_id": self.run_id,
                                  "attempt_id": attempt_id, "event_id": event_id,
                                  "callback_ns": callback_ns,
                                  "validation_end_ns": validation_end_ns,
                                  "disposition": "OFFERED"})
            self.offers.append(row)
            if action != "REJECT_FULL":
                job = (row, source)
                if self.active is None:
                    self.active = job
                else:
                    self.waiting.append(job)
            self.condition.notify_all()


def run_case(*, fixture_dir: Path, transport: str, K: int,
             iterations_per_unit: int, urgent_deadline_ms: float,
             routine_tau_ms: float, sqlite_output: Path,
             host: str = "127.0.0.1", port: int = 1883,
             timeout_s: float = 35.0) -> tuple[list[dict], dict]:
    if type(K) is not int or K < 0 or iterations_per_unit <= 0:
        raise ValueError("Invalid nonnegative K or artificial CPU scale")
    if urgent_deadline_ms <= 0 or routine_tau_ms <= 0 or timeout_s <= 0:
        raise ValueError("Artificial timing bounds must be positive")
    fixture = fixture_audit(fixture_dir)
    offers, hidden = fixture["offers"], fixture["hidden"]
    source = [source_payload(item) for item in offers]
    offsets = [item["planned_offer_offset_ns"] for item in offers]
    gaps = [offsets[0], *(b - a for a, b in zip(offsets, offsets[1:]))]
    run_id = "s9-" + uuid.uuid4().hex[:16]
    with tempfile.TemporaryDirectory(prefix="stage9-synthetic-") as tmp:
        database = Path(tmp) / "alerts.sqlite"
        gateway = UrgentPushoutGateway(
            db_path=database, run_id=run_id, K=K, hidden_work=hidden,
            iterations_per_unit=iterations_per_unit,
            urgent_deadline_ns=int(urgent_deadline_ms * 1e6),
            routine_tau_ns=int(routine_tau_ms * 1e6))
        try:
            if transport == "inproc":
                published = publish_schedule(gateway, source, gaps, deliver=gateway.receive)
                receiver_complete = True
            elif transport == "mqtt":
                published, receiver_complete, _ = mqtt_publisher_and_receiver(
                    gateway, source, gaps, host, port, timeout_s)
            else:
                raise ValueError("Unsupported synthetic transport")
        finally:
            drained, attempts, audited_offers, cutoff = gateway.shutdown_and_drain(timeout_s=timeout_s)
        if not drained or not receiver_complete:
            raise RuntimeError("Incomplete Stage 9 trial")
        source_by_id = {item["event_id"]: item for item in source}
        for item in published:
            item["source"] = source_by_id[item["event_id"]]
        con = sqlite3.connect(database)
        try:
            saved = {item[0]: item[1:] for item in con.execute(
                "SELECT event_id, trusted_class, rule_result, result_json FROM handled_alerts")}
        finally:
            con.close()
        expected = {row["event_id"]: (row["trusted_class"], row["db_rule_result"],
                                       row["db_result_json"])
                    for row in audited_offers if row["terminal"] == "COMPLETED"}
        if saved != expected:
            raise RuntimeError("Persisted SQLite rows disagree with completed offers")
        with sqlite_output.open("xb"):
            pass
        src_db, dst_db = sqlite3.connect(database), sqlite3.connect(sqlite_output)
        try:
            src_db.backup(dst_db)
        finally:
            dst_db.close()
            src_db.close()

    fixture_manifest = json.loads((fixture_dir / "manifest.json").read_text())
    manifest = {
        "type": "manifest", "run_id": run_id, "policy_id": CANDIDATE,
        "scenario_id": "stage9_synthetic_" + transport,
        "study_status": "STAGE9_ARTIFICIAL_CANDIDATE_NO_NOVELTY_OR_FIELD_CLAIM",
        "trace_provenance": "STAGE5K2_FICTIONAL_UNAPPROVED_" + fixture["shape"],
        "source_sha256": hashlib.sha256(canonical(source).encode()).hexdigest(),
        "schedule_sha256": hashlib.sha256(canonical(gaps).encode()).hexdigest(),
        "offer_fixture_sha256": fixture_manifest["offer_sha256"],
        "hidden_work_sha256": fixture_manifest["hidden_work_sha256"],
        "fixture_id": fixture_manifest["fixture_id"],
        "planned_source_horizon_ns": offsets[-1] - offsets[0],
        "synthetic_iterations_per_work_unit": iterations_per_unit,
        "admission_rule": ADMISSION_RULE,
        "dispatch_rule": "STRICT_URGENT_FIRST_ON_WAITING_QUEUE",
        "admission_changes_vs_baselines": True,
        "work_model": "PBKDF2_SHA256_ILLUSTRATIVE_CPU_PLUS_SQLITE_WAL_FULL",
        "planned_unique": len(source), "K": K,
        "routine_tau_ns": int(routine_tau_ms * 1e6),
        "urgent_deadline_offset_ns": int(urgent_deadline_ms * 1e6),
        "observation_end_ns": cutoff,
        "clock_domain": "single_gateway_process_monotonic_ns",
        "dedup_cache_reset": True, "publisher_log_complete": True,
        "receiver_capture_complete": receiver_complete,
        "db_rows_reopened": len(saved), "db_reopen_exact": True,
        "sqlite_backup_sha256": hashlib.sha256(sqlite_output.read_bytes()).hexdigest(),
        "worker_handler": "STAGE7_ARTIFICIAL_CPU_PLUS_STAGE5G_SQLITE",
        "completion_boundary": "post_SQLite_commit_return",
    }
    rows = [manifest, *published, *attempts, *audited_offers]
    # Self-check only; independent audit is mandatory for every frozen trial.
    unique_offers = [r for r in rows if r["type"] == "offer"]
    if len(unique_offers) != len(source) or any(r["terminal"] == "UNRESOLVED" for r in unique_offers):
        raise RuntimeError("Incomplete offered population")
    completed = sum(r["terminal"] == "COMPLETED" for r in unique_offers)
    rejected = sum(r["terminal"] == "REJECTED" for r in unique_offers)
    cancelled = sum(r["terminal"] == "CANCELLED" for r in unique_offers)
    urgent = [r for r in unique_offers if r["trusted_class"] == "URGENT"]
    routine = [r for r in unique_offers if r["trusted_class"] == "ROUTINE"]
    U = sum(r["terminal"] != "COMPLETED" or
            r["complete_ns"] > r["urgent_deadline_ns"] for r in urgent) / len(urgent)
    R = sum(r["terminal"] == "COMPLETED" and
            r["start_ns"] <= r["offer_ns"] + int(routine_tau_ms * 1e6)
            for r in routine) / len(routine)
    return rows, {"offered": len(source), "committed": completed,
                  "rejected_full": rejected, "cancelled_pushout": cancelled,
                  "dropped_total": rejected + cancelled, "U": U, "R": R}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--fixture-dir", type=Path, required=True)
    p.add_argument("--transport", choices=["inproc", "mqtt"], default="inproc")
    p.add_argument("--K", type=int, default=3)
    p.add_argument("--iterations-per-unit", type=int, default=10000)
    p.add_argument("--urgent-deadline-ms", type=float, default=50.0)
    p.add_argument("--routine-tau-ms", type=float, default=20.0)
    p.add_argument("--sqlite-output", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=1883)
    p.add_argument("--timeout-s", type=float, default=35.0)
    args = p.parse_args()
    rows, summary = run_case(
        fixture_dir=args.fixture_dir, transport=args.transport, K=args.K,
        iterations_per_unit=args.iterations_per_unit,
        urgent_deadline_ms=args.urgent_deadline_ms,
        routine_tau_ms=args.routine_tau_ms, sqlite_output=args.sqlite_output,
        host=args.host, port=args.port, timeout_s=args.timeout_s)
    with args.output.open("x", encoding="utf-8") as out:
        for row in rows:
            out.write(canonical(row) + "\n")
    print(json.dumps({"status": "STAGE9_ARTIFICIAL_ONLY", **summary}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
