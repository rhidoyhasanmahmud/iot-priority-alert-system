#!/usr/bin/env python3
"""Stage 7 exploratory *fictional* workload replay, MQTT/inproc -> SQLite.

Candidate conventional FIFO/strict-urgent-first policies share the same
post-validation admission rule, source payloads, hidden ex-ante work per event,
single worker, K-waiting capacity, and SQLite WAL/FULL handler. Actual CPU work
is injected BEFORE the SQLite handler, AFTER a policy has selected a job.

No real IoT workload, owner SLA, calibrated physical service distribution,
novel scheduler, registered study, or publishable scientific finding is claimed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import time
import uuid

from stage5d_lifecycle_audit import audit as lifecycle_audit
from stage5e_gateway_pilot import mqtt_publisher_and_receiver, now, publish_schedule
from stage5g_reference_handler import canonical, open_db, process_one
from stage5h_joint_gateway import JointGateway
from stage5k2_independent_audit import audit as fixture_audit


POLICIES = {"fifo", "strict_urgent_first"}


def source_payload(offer: dict) -> dict:
    """Deterministic fictional payload, separate from hidden work units."""
    eid = offer["event_id"]
    device = hashlib.sha256(f"stage7|{eid}|device".encode()).digest()[0] % 16
    battery = hashlib.sha256(f"stage7|{eid}|battery".encode()).digest()[0] % 101
    urgent = offer["trusted_class"] == "urgent"
    return {"event_id": eid, "device_id": f"device_{device:02d}",
            "kind": "tamper" if urgent else "health", "tamper": urgent,
            "battery_pct": battery}


class PolicyGateway(JointGateway):
    """Live process-internal admission/worker; policy sees only visible queue."""

    def __init__(self, *, db_path: Path, run_id: str, K: int,
                 policy: str, hidden_work: list[dict], iterations_per_unit: int,
                 urgent_deadline_ns: int, routine_tau_ns: int):
        if policy not in POLICIES or not 1 <= iterations_per_unit <= 1_000_000:
            raise ValueError("Invalid conventional policy or synthetic work scaling")
        self.policy = policy
        self.iterations_per_unit = iterations_per_unit
        self.synthetic_work_by_id = {
            row["event_id"]: row["synthetic_required_work_units"] for row in hidden_work
        }
        super().__init__(db_path=db_path, run_id=run_id, K=K,
                         tau_ns=routine_tau_ns,
                         urgent_deadline_offset_ns=urgent_deadline_ns)

    def _select_next(self):
        """Called only after completion, under the queue lock. Never reads work."""
        snapshot = [{"event_id": row["event_id"], "trusted_class": row["trusted_class"]}
                    for row, _ in self.waiting]
        if self.policy == "fifo":
            index = 0
        else:
            index = next((i for i, row in enumerate(snapshot)
                          if row["trusted_class"] == "URGENT"), 0)
        selected = self.waiting[index]
        del self.waiting[index]
        selected[0]["dispatch_snapshot"] = snapshot
        selected[0]["dispatch_reason"] = "queued_policy_selection"
        selected[0]["dispatch_choice_ns"] = now()
        return selected

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
                # Only the service executor (never the dispatcher) reads this
                # full offered-population work map, after dispatch selection.
                units = self.synthetic_work_by_id[row["event_id"]]
                cpu_start = now()
                digest = hashlib.pbkdf2_hmac(
                    "sha256", row["event_id"].encode("utf-8"),
                    b"STAGE7-ARTIFICIAL-WORK-NOT-AN-IOT-PROFILE",
                    units * self.iterations_per_unit,
                )
                cpu_end = now()
                if len(digest) != 32:
                    raise RuntimeError("Synthetic CPU work failed")
                result = process_one(con, source)
                with self.condition:
                    row["synthetic_work_units_post_dispatch"] = units
                    row["synthetic_cpu_iterations"] = units * self.iterations_per_unit
                    row["synthetic_cpu_service_ns"] = cpu_end - cpu_start
                    row["db_handler_start_ns"] = result["work_start_ns"]
                    row["db_commit_return_ns"] = result["commit_return_ns"]
                    row["db_service_ns"] = result["service_ns"]
                    row["db_rule_result"] = result["rule_result"]
                    row["db_result_json"] = result["result_json"]
                    row["db_committed"] = result["committed"]
                    row["complete_ns"] = now()
                    row["terminal"] = "COMPLETED"
                    self.active = self._select_next() if self.waiting else None
                    self.condition.notify_all()
        except Exception as exc:
            with self.condition:
                self.worker_errors.append(repr(exc))
                self.closed = True
                self.condition.notify_all()
        finally:
            if con is not None:
                con.close()


def run_case(*, fixture_dir: Path, transport: str, policy: str, K: int,
             iterations_per_unit: int, urgent_deadline_ms: float,
             routine_tau_ms: float, sqlite_output: Path,
             host: str = "127.0.0.1", port: int = 1883,
             timeout_s: float = 30.0) -> tuple[list[dict], dict]:
    if (policy not in POLICIES or type(K) is not int or K < 0 or
            iterations_per_unit <= 0):
        raise ValueError("Invalid policy, K, or positive CPU work scale")
    if urgent_deadline_ms <= 0 or routine_tau_ms <= 0 or timeout_s <= 0:
        raise ValueError("Debug deadlines and timeout must be positive")
    fixture = fixture_audit(fixture_dir)
    offers, hidden = fixture["offers"], fixture["hidden"]
    source = [source_payload(row) for row in offers]
    offsets = [row["planned_offer_offset_ns"] for row in offers]
    gaps = [offsets[0]] + [b - a for a, b in zip(offsets, offsets[1:])]
    source_sha256 = hashlib.sha256(canonical(source).encode()).hexdigest()
    source_schedule_sha256 = hashlib.sha256(canonical(gaps).encode()).hexdigest()
    run_id = "s7-" + uuid.uuid4().hex[:16]

    with tempfile.TemporaryDirectory(prefix="stage7-synthetic-") as temp:
        db = Path(temp) / "alerts.sqlite"
        gateway = PolicyGateway(
            db_path=db, run_id=run_id, K=K, policy=policy,
            hidden_work=hidden, iterations_per_unit=iterations_per_unit,
            urgent_deadline_ns=int(urgent_deadline_ms * 1e6),
            routine_tau_ns=int(routine_tau_ms * 1e6),
        )
        try:
            if transport == "inproc":
                published = publish_schedule(gateway, source, gaps, deliver=gateway.receive)
                receiver_complete = True
            elif transport == "mqtt":
                published, receiver_complete, _ = mqtt_publisher_and_receiver(
                    gateway, source, gaps, host, port, timeout_s)
            else:
                raise ValueError("transport must be inproc or mqtt")
        finally:
            drained, attempts, offered, cutoff = gateway.shutdown_and_drain(timeout_s=timeout_s)
        if not drained or not receiver_complete:
            raise RuntimeError("Incomplete synthetic trial; not auditable as a complete run")

        by_id = {record["event_id"]: record for record in source}
        for row in published:
            row["source"] = by_id[row["event_id"]]
        con = sqlite3.connect(db)
        try:
            saved = {r[0]: r[1:] for r in con.execute(
                "SELECT event_id, trusted_class, rule_result, result_json FROM handled_alerts")}
        finally:
            con.close()
        expected = {row["event_id"]: (row["trusted_class"], row["db_rule_result"],
                                      row["db_result_json"])
                    for row in offered if row["terminal"] == "COMPLETED"}
        if saved != expected:
            raise RuntimeError("SQLite stored rows differ from completed ledger")

        with sqlite_output.open("xb"):
            pass
        s, t = sqlite3.connect(db), sqlite3.connect(sqlite_output)
        try:
            s.backup(t)
        finally:
            t.close()
            s.close()
    db_sha = hashlib.sha256(sqlite_output.read_bytes()).hexdigest()
    manifest = {
        "type": "manifest", "run_id": run_id, "policy_id": policy,
        "scenario_id": "stage7_exploratory_" + transport,
        "trace_provenance": "STAGE5K2_FICTIONAL_UNAPPROVED_" + fixture["shape"],
        "source_sha256": source_sha256,
        "schedule_sha256": source_schedule_sha256,
        "offer_fixture_sha256": json.loads((fixture_dir / "manifest.json").read_text())["offer_sha256"],
        "hidden_work_sha256": json.loads((fixture_dir / "manifest.json").read_text())["hidden_work_sha256"],
        "fixture_id": offers[0]["fixture_id"],
        "planned_source_horizon_ns": offsets[-1] - offsets[0],
        "synthetic_iterations_per_work_unit": iterations_per_unit,
        "work_model": "PBKDF2_SHA256_ILLUSTRATIVE_CPU_PLUS_SQLITE_WAL_FULL",
        "study_status": "ENGINEERING_PILOT_UNREGISTERED_NOT_SCIENTIFIC_RESULTS",
        "planned_unique": len(source), "K": K,
        "routine_tau_ns": int(routine_tau_ms * 1e6),
        "urgent_deadline_offset_ns": int(urgent_deadline_ms * 1e6),
        "observation_end_ns": cutoff,
        "clock_domain": "single_gateway_process_monotonic_ns",
        "dedup_cache_reset": True, "publisher_log_complete": True,
        "receiver_capture_complete": receiver_complete,
        "db_rows_reopened": len(saved), "db_reopen_exact": True,
        "sqlite_backup_sha256": db_sha,
        "worker_handler": "STAGE7_ARTIFICIAL_CPU_PLUS_STAGE5G_SQLITE",
        "completion_boundary": "post_SQLite_commit_return",
    }
    rows = [manifest, *published, *attempts, *offered]
    summary = lifecycle_audit(rows)
    if (summary["published_unique"] != len(source) or
            summary["offered_unique"] != len(source) or
            summary["unresolved_offers"] != 0):
        raise RuntimeError("Incomplete source/offer lifecycle")
    return rows, summary


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--fixture-dir", type=Path, required=True)
    p.add_argument("--policy", choices=sorted(POLICIES), required=True)
    p.add_argument("--transport", choices=["inproc", "mqtt"], default="inproc")
    p.add_argument("--K", type=int, default=3)
    p.add_argument("--iterations-per-unit", type=int, default=10_000)
    p.add_argument("--urgent-deadline-ms", type=float, default=20.0)
    p.add_argument("--routine-tau-ms", type=float, default=20.0)
    p.add_argument("--sqlite-output", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=1883)
    p.add_argument("--timeout-s", type=float, default=30.0)
    args = p.parse_args()
    rows, summary = run_case(
        fixture_dir=args.fixture_dir, policy=args.policy, transport=args.transport,
        K=args.K, iterations_per_unit=args.iterations_per_unit,
        urgent_deadline_ms=args.urgent_deadline_ms,
        routine_tau_ms=args.routine_tau_ms, sqlite_output=args.sqlite_output,
        host=args.host, port=args.port, timeout_s=args.timeout_s,
    )
    with args.output.open("x", encoding="utf-8") as f:
        for row in rows:
            f.write(canonical(row) + "\n")
    print(json.dumps({"status": "SYNTHETIC_EXPLORATORY_ONLY", **summary}, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
