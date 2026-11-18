#!/usr/bin/env python3
"""Reserved tuning-only sanity pilot; NEVER promoted to held-out results."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import random
import statistics

from stage5k2_workload_fixture import save_fixture
from stage7_controlled_replay import run_case as run_baseline
from stage7_independent_replay_audit import audit_run as audit_baseline
from stage9_urgent_pushout import run_case as run_candidate
from stage9_independent_audit import audit_run as audit_candidate


POLICIES = ["fifo", "strict_urgent_first", "routine_wait_guard", "urgent_pushout_strict"]
SCENARIOS = {
    "burst": ("clustered", "flat", 1_000_000_000),
    "smooth": ("smooth", "flat", 1_000_000_000),
    "overload": ("smooth", "flat", 250_000_000),
    "variable": ("smooth", "variable", 1_000_000_000),
}
CELLS = [("burst", 3), ("smooth", 3), ("overload", 3),
         ("variable", 3), ("burst", 0)]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--seeds", nargs="+", type=int, default=[8001, 8002, 8003])
    p.add_argument("--primary-only", action="store_true")
    args = p.parse_args()
    if not args.seeds or len(args.seeds) != len(set(args.seeds)) or not set(args.seeds).issubset(range(8001, 8011)):
        raise ValueError("Pilot must use only preregistered 8001..8010 tuning seeds")
    args.output_dir.mkdir(parents=True, exist_ok=False)
    fixtures = args.output_dir / "fixtures"
    runs = args.output_dir / "runs"
    fixtures.mkdir()
    runs.mkdir()
    cells = CELLS[:1] if args.primary_only else CELLS
    for seed in args.seeds:
        for scenario in set(cell[0] for cell in cells):
            shape, dispersion, horizon_ns = SCENARIOS[scenario]
            save_fixture(fixtures/f"s{seed}_{scenario}", seed=seed, count=60,
                         urgent_count=15, shape=shape, dispersion=dispersion,
                         horizon_ns=horizon_ns)
    planned = [(seed, scenario, K, policy) for seed in args.seeds
               for scenario, K in cells for policy in POLICIES]
    random.Random(20261117).shuffle(planned)
    results = []
    for i, (seed, scenario, K, policy) in enumerate(planned, 1):
        fixture = fixtures/f"s{seed}_{scenario}"
        sqlite = runs/f"s{seed}_{scenario}_K{K}_{policy}.sqlite"
        ledger = runs/f"s{seed}_{scenario}_K{K}_{policy}.jsonl"
        kw = dict(fixture_dir=fixture, transport="inproc", K=K,
                  iterations_per_unit=10_000, urgent_deadline_ms=50,
                  routine_tau_ms=20, sqlite_output=sqlite, timeout_s=35)
        if policy == "urgent_pushout_strict":
            records, _ = run_candidate(**kw)
            outcome = audit_candidate(records, sqlite, fixture)
        else:
            records, _ = run_baseline(**kw, policy=policy)
            outcome = audit_baseline(records, sqlite, fixture)
        with ledger.open("x") as stream:
            for row in records:
                stream.write(json.dumps(row, sort_keys=True) + "\n")
        info = {"seed": seed, "scenario": scenario, "K": K,
                "policy": policy, "offered": outcome["offered"],
                "U": outcome.get("U", outcome.get("U_artificial_debug_only")),
                "R": outcome.get("R", outcome.get("R_artificial_debug_only")),
                "audit_status": outcome["status"]}
        results.append(info)
        print(f"RESERVED PILOT AUDITED {i}/{len(planned)} {seed} {scenario} K{K} {policy} "
              f"U={info['U']:.3f} R={info['R']:.3f}", flush=True)
    aggregate = {}
    for scenario, K in cells:
        key = f"{scenario}_K{K}"
        aggregate[key] = {
            policy: {"U": statistics.mean(x["U"] for x in results if x["scenario"] == scenario
                                         and x["K"] == K and x["policy"] == policy),
                     "R": statistics.mean(x["R"] for x in results if x["scenario"] == scenario
                                         and x["K"] == K and x["policy"] == policy)}
            for policy in POLICIES}
    summary = {"status": "RESERVED_TUNING_ONLY_NOT_SCIENTIFIC_EVIDENCE",
               "seeds": args.seeds, "trials": len(results), "aggregate": aggregate,
               "runs": results}
    with (args.output_dir/"pilot.json").open("x") as stream:
        json.dump(summary, stream, indent=2, sort_keys=True)
    print(json.dumps({"status": summary["status"], "aggregate": aggregate}, indent=2))


if __name__ == "__main__":
    main()
