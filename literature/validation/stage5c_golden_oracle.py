"""Stage 5C: tiny deterministic measurement oracle, NOT a novel scheduler.

One non-preemptive worker; K waiting slots, plus one possible running job.
At equal times: complete -> admit in (arrival, id) order -> dispatch.
All accepted jobs drain. The tiny event sets are **illustrative only**.
"""

from dataclasses import dataclass
from fractions import Fraction
from math import inf
from collections import defaultdict
import random


@dataclass(frozen=True)
class Job:
    id: int
    arrival: int
    cls: str
    duration: int
    deadline: int | None = None
    tau: int | None = None

    def __post_init__(self):
        assert self.id >= 0 and self.arrival >= 0 and self.duration > 0
        assert self.cls in ("urgent", "routine")
        assert (self.deadline is not None) == (self.cls == "urgent")
        assert (self.tau is not None) == (self.cls == "routine")
        if self.cls == "urgent":
            assert self.deadline >= self.arrival
        else:
            assert self.tau >= 0


def evaluate(jobs: list[Job], waiting_capacity: int, policy: str):
    """Return exact offered-population U and R(tau) with golden traces.

    Selection sees only class, arrival and id, never unstarted duration.
    """
    assert isinstance(waiting_capacity, int) and waiting_capacity >= 0
    assert policy in ("fifo", "priority")
    assert len({job.id for job in jobs}) == len(jobs)
    offered = sorted(jobs, key=lambda j: (j.arrival, j.id))
    waiting: list[Job] = []
    admitted: set[int] = set()
    rejected: set[int] = set()
    started: dict[int, int] = {}
    finished: dict[int, int] = {}
    active: Job | None = None
    finish_at = inf
    next_index = 0
    max_waiting = 0

    while next_index < len(offered) or waiting or active is not None:
        next_arrival = (offered[next_index].arrival
                        if next_index < len(offered) else inf)
        clock = min(next_arrival, finish_at)
        assert clock < inf

        # Event-time tie rule: first release the completed running job.
        if active is not None and finish_at <= clock:
            finished[active.id] = clock
            active, finish_at = None, inf

        # Reserve the idle worker's service slot for this timestamp's batch.
        limit = waiting_capacity + int(active is None)
        while next_index < len(offered) and offered[next_index].arrival <= clock:
            job = offered[next_index]
            if len(waiting) < limit:
                waiting.append(job)
                admitted.add(job.id)
            else:
                rejected.add(job.id)
            next_index += 1

        if active is None and waiting:
            if policy == "priority":
                chosen = min(waiting, key=lambda j: (j.cls != "urgent", j.arrival, j.id))
            else:
                chosen = min(waiting, key=lambda j: (j.arrival, j.id))
            waiting.remove(chosen)
            started[chosen.id] = clock
            active, finish_at = chosen, clock + chosen.duration

        max_waiting = max(max_waiting, len(waiting))
        assert len(waiting) <= waiting_capacity

    assert admitted.isdisjoint(rejected)
    assert len(admitted) + len(rejected) == len(offered)
    assert set(started) == set(finished) == admitted

    urgent = [j for j in offered if j.cls == "urgent"]
    routine = [j for j in offered if j.cls == "routine"]
    urgent_met = sum(j.id in finished and finished[j.id] <= j.deadline for j in urgent)
    routine_met = sum(j.id in started and started[j.id] <= j.arrival + j.tau
                      for j in routine)
    return {
        "U": Fraction(len(urgent) - urgent_met, len(urgent)) if urgent else None,
        "R": Fraction(routine_met, len(routine)) if routine else None,
        "offered": len(offered),
        "admitted": len(admitted),
        "rejected": sorted(rejected),
        "started": started,
        "finished": finished,
        "max_waiting": max_waiting,
    }


def main():
    U, R = "urgent", "routine"
    cases = [
        # Case A: same workload, an explicit priority-vs-FIFO trade-off.
        ("A_FIFO", 2, "fifo", [Job(1, 0, U, 2, deadline=3),
         Job(2, 0, R, 1, tau=2), Job(3, 0, U, 1, deadline=3)],
         Fraction(1, 2), Fraction(1), [], {1: 0, 2: 2, 3: 3}),
        ("A_PRIORITY", 2, "priority", [Job(1, 0, U, 2, deadline=3),
         Job(2, 0, R, 1, tau=2), Job(3, 0, U, 1, deadline=3)],
         Fraction(0), Fraction(0), [], {1: 0, 3: 2, 2: 3}),
        # Case B: simultaneous admission is class-neutral; one urgent drops.
        ("B_FIFO", 1, "fifo", [Job(1, 0, R, 4, tau=1),
         Job(2, 0, U, 1, deadline=2), Job(3, 0, U, 1, deadline=2)],
         Fraction(1), Fraction(1), [3], {1: 0, 2: 4}),
        ("B_PRIORITY", 1, "priority", [Job(1, 0, R, 4, tau=1),
         Job(2, 0, U, 1, deadline=2), Job(3, 0, U, 1, deadline=2)],
         Fraction(1, 2), Fraction(1), [3], {2: 0, 1: 1}),
        # Case C: non-preemptive routine blocking makes urgent miss inevitable.
        ("C_BLOCK", 1, "priority", [Job(1, 0, R, 5, tau=1),
         Job(2, 1, U, 1, deadline=3)],
         Fraction(1), Fraction(1), [], {1: 0, 2: 5}),
        # Case D: equality at both deadline and waiting threshold counts success.
        ("D_EQUAL", 1, "priority", [Job(1, 0, U, 2, deadline=2),
         Job(2, 0, R, 1, tau=2)],
         Fraction(0), Fraction(1), [], {1: 0, 2: 2}),
        # Case E: empty classes yield undefined, not zero or one.
        ("E_NO_URGENT", 0, "fifo", [Job(1, 0, R, 1, tau=0)],
         None, Fraction(1), [], {1: 0}),
        ("E_NO_ROUTINE", 0, "fifo", [Job(1, 0, U, 1, deadline=1)],
         Fraction(0), None, [], {1: 0}),
        # Case F: completion at same timestamp as new arrival frees capacity.
        ("F_TIE", 0, "priority", [Job(1, 0, U, 1, deadline=1),
         Job(2, 1, U, 1, deadline=2)],
         Fraction(0), None, [], {1: 0, 2: 1}),
    ]
    for name, capacity, policy, jobs, expected_u, expected_r, drops, starts in cases:
        result = evaluate(jobs, capacity, policy)
        assert result["U"] == expected_u, (name, "U", result)
        assert result["R"] == expected_r, (name, "R", result)
        assert result["rejected"] == drops, (name, "rejected", result)
        assert result["started"] == starts, (name, "started", result)
        print(f"{name}: K={capacity}, policy={policy}, offered={result['offered']}, "
              f"rejected={len(drops)}, U={result['U']}, R(tau)={result['R']}, "
              f"start={dict(sorted(starts.items()))}")
    print(f"PASS: {len(cases)} deterministic golden cases")


def small_synthetic_smoke():
    """Engineering smoke only. Paired two-class generated traces, not field data.

    'clustered' moves gap-time out of a 20% event-index window, keeping
    the same total arrival horizon, class mix and total offered service work.
    It is NOT a model of a measured IoT arrival distribution.
    """
    rows = defaultdict(list)
    runs = 0
    for seed in range(1, 7):
        rng = random.Random(seed)
        count = 120
        gaps = [rng.choice((0, 1, 2, 3, 4)) for _ in range(count)]
        cls = ["urgent" if rng.randrange(4) == 0 else "routine"
               for _ in range(count)]
        duration = [rng.choice((1, 2, 3)) for _ in range(count)]
        assert "urgent" in cls and "routine" in cls

        for shape in ("normal", "clustered"):
            g = gaps.copy()
            if shape == "clustered":
                lo, hi = 48, 72
                removed = sum(g[lo:hi])
                g[lo:hi] = [0] * (hi-lo)
                outside = [i for i in range(count) if i < lo or i >= hi]
                for k in range(removed):
                    g[outside[k % len(outside)]] += 1
            assert sum(g) == sum(gaps)

            now, jobs = 0, []
            for i in range(count):
                now += g[i]
                jobs.append(Job(i, now, cls[i], duration[i],
                                deadline=now+5 if cls[i] == "urgent" else None,
                                tau=5 if cls[i] == "routine" else None))
            assert sum(j.duration for j in jobs) == sum(duration)

            for K in (2, 10):
                for policy in ("fifo", "priority"):
                    result = evaluate(jobs, K, policy)
                    assert result["offered"] == count
                    assert result["admitted"] + len(result["rejected"]) == count
                    rows[(shape, K, policy)].append(result)
                    runs += 1

    for key in sorted(rows):
        shape, K, policy = key
        samples = rows[key]
        u = sum(float(x["U"]) for x in samples)/len(samples)
        r = sum(float(x["R"]) for x in samples)/len(samples)
        drops = sum(len(x["rejected"]) for x in samples)
        print(f"SMOKE {shape:9s} K={K:2d} {policy:8s} seeds=6 "
              f"mean_seed_U={u:.4f} mean_seed_R={r:.4f} "
              f"all_policy_run_drops={drops}")
    print(f"PASS: {runs} paired synthetic smoke runs; no performance claim")


if __name__ == "__main__":
    main()
    small_synthetic_smoke()
