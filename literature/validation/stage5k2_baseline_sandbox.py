#!/usr/bin/env python3
"""Two conventional non-preemptive *toy* dispatch baselines for invariant tests.

Consumes an already-generated *fictional* fixture. Does not model real MQTT,
SQLite execution time, instrument a deployment, or produce scientific results.
No deadline semantics, statistical treatment, or novel scheduler is claimed.
"""

from __future__ import annotations

from dataclasses import dataclass


POLICIES = frozenset({"fifo", "strict_urgent_first"})


@dataclass(frozen=True)
class VisibleJob:
    event_id: str
    trusted_class: str
    planned_offer_offset_ns: int


def select_waiting(visible_queue: list[VisibleJob], policy: str) -> int:
    """Only already-offered *visible* fields are available at selection time."""
    if policy not in POLICIES:
        raise ValueError(f"Unknown baseline: {policy}")
    if not visible_queue:
        raise ValueError("Cannot select from empty waiting queue")
    if policy == "fifo":
        return 0
    return next((i for i, j in enumerate(visible_queue) if j.trusted_class == "urgent"), 0)


def simulate_contract(
    offers: list[dict], hidden_work: list[dict], *, policy: str,
    waiting_capacity: int, illustrative_ns_per_unit: int = 1_000_000,
) -> list[dict]:
    """Pure discrete-event bookkeeping under one hypothetical service model.

    Arrival source offsets are *assumed* to be local offers solely for this
    sandbox. No online policy sees future arrivals, work units or finish time.
    Waiting_capacity K excludes the single running slot.
    """
    if policy not in POLICIES:
        raise ValueError(f"Unknown policy: {policy}")
    if type(waiting_capacity) is not int or waiting_capacity < 0:
        raise ValueError("Waiting capacity K must be a nonnegative integer")
    if type(illustrative_ns_per_unit) is not int or illustrative_ns_per_unit <= 0:
        raise ValueError("Synthetic work-unit duration must be positive")
    ids = [item.get("event_id") for item in offers]
    work_ids = [item.get("event_id") for item in hidden_work]
    if not ids or len(ids) != len(set(ids)) or ids != work_ids:
        raise ValueError("Require exact unique, ordered offered/hidden IDs")
    if any(set(item) != {"fixture_id", "event_id", "trusted_class", "planned_offer_offset_ns"}
           for item in offers):
        raise ValueError("Invalid visible offer schema (potential hidden-work leak)")
    if any(set(item) != {"event_id", "synthetic_required_work_units"} for item in hidden_work):
        raise ValueError("Invalid hidden-work schema")

    offsets = [item["planned_offer_offset_ns"] for item in offers]
    if any(type(t) is not int or t < 0 for t in offsets) or offsets != sorted(offsets):
        raise ValueError("Offers must be ordered by local-source time")
    if any(item["trusted_class"] not in {"urgent", "routine"} for item in offers):
        raise ValueError("Unknown class")
    work_units = {item["event_id"]: item["synthetic_required_work_units"] for item in hidden_work}
    if any(type(n) is not int or n <= 0 for n in work_units.values()):
        raise ValueError("Invalid synthetic work units")

    visible = [VisibleJob(item["event_id"], item["trusted_class"],
                          item["planned_offer_offset_ns"]) for item in offers]
    ledger = {
        job.event_id: {"event_id": job.event_id, "trusted_class": job.trusted_class,
                       "planned_offer_offset_ns": job.planned_offer_offset_ns,
                       "status": None, "start_offset_ns": None, "complete_offset_ns": None}
        for job in visible
    }
    waiting: list[VisibleJob] = []
    running: tuple[VisibleJob, int] | None = None

    def start_job(job: VisibleJob, now: int) -> tuple[VisibleJob, int]:
        # Hidden work is looked up only after the *visible* dispatch choice.
        ledger[job.event_id]["start_offset_ns"] = now
        return (job, now + work_units[job.event_id] * illustrative_ns_per_unit)

    def advance_to(now: int | None) -> None:
        nonlocal running
        # Completion at exactly an offer instant frees capacity *before* offer.
        while running is not None and (now is None or running[1] <= now):
            finished, finish_ns = running
            ledger[finished.event_id]["complete_offset_ns"] = finish_ns
            ledger[finished.event_id]["status"] = "completed_synthetic"
            running = None
            if waiting:
                next_job = waiting.pop(select_waiting(waiting, policy))
                running = start_job(next_job, finish_ns)

    for job in visible:
        advance_to(job.planned_offer_offset_ns)
        if running is None:
            running = start_job(job, job.planned_offer_offset_ns)
        elif len(waiting) < waiting_capacity:
            waiting.append(job)
        else:
            ledger[job.event_id]["status"] = "rejected_full_synthetic"

    advance_to(None)
    if waiting or running is not None or any(row["status"] is None for row in ledger.values()):
        raise AssertionError("Synthetic lifecycle did not terminate cleanly")
    return [ledger[event_id] for event_id in ids]


def verify_simulated_lifecycle(rows: list[dict], *, waiting_capacity: int) -> dict:
    """Independently check outcome conservation and single-worker intervals.

    This deliberately does NOT recalculate policy choices or timing model.
    """
    if len({row["event_id"] for row in rows}) != len(rows):
        raise AssertionError("Duplicate event outcomes")
    intervals = []
    accepted = 0
    rejected = 0
    for row in rows:
        if row["status"] == "rejected_full_synthetic":
            rejected += 1
            if row["start_offset_ns"] is not None or row["complete_offset_ns"] is not None:
                raise AssertionError("A rejected job has simulated service")
        elif row["status"] == "completed_synthetic":
            accepted += 1
            start, finish = row["start_offset_ns"], row["complete_offset_ns"]
            if not (type(start) is int and type(finish) is int and
                    row["planned_offer_offset_ns"] <= start < finish):
                raise AssertionError("Invalid non-preemptive service interval")
            intervals.append((start, finish))
        else:
            raise AssertionError("Unknown or missing synthetic outcome")
    for (_, previous_end), (next_start, _) in zip(sorted(intervals), sorted(intervals)[1:]):
        if next_start < previous_end:
            raise AssertionError("Two jobs overlap on the single worker")
    if accepted + rejected != len(rows) or waiting_capacity < 0:
        raise AssertionError("Conservation/capacity violation")

    # Reconstruct system occupancy from all accepted jobs still in the system.
    # Count queued jobs too: their service starts after the current instant.
    for row in rows:
        t = row["planned_offer_offset_ns"]
        in_system = sum(
            1 for candidate in rows
            if candidate["status"] == "completed_synthetic"
            and candidate["planned_offer_offset_ns"] <= t
            and t < candidate["complete_offset_ns"]
        )
        if in_system > waiting_capacity + 1:
            raise AssertionError("Running + waiting capacity exceeded")
        if row["status"] == "rejected_full_synthetic" and in_system != waiting_capacity + 1:
            raise AssertionError("A full-buffer rejection occurred without a full buffer")
    return {"status": "PASS_SYNTHETIC_LIFECYCLE_ONLY", "offered": len(rows),
            "completed_synthetic": accepted, "rejected_full_synthetic": rejected}
