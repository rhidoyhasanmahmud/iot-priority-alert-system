#!/usr/bin/env python3
"""Reopen every development ledger + physical DB; reject tampering or missing trials.

This re-audit is descriptive and does not convert development/tuning into
held-out statistical evidence. Does not import any Stage 10 emitter code.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from stage9_independent_audit import audit_run as audit_stage9
from stage10_independent_audit import audit_run as audit_stage10


def verify_dir(root: Path) -> dict:
    summary = json.loads((root / "pilot_summary.json").read_text())
    with (root / "pilot_metrics.csv").open(newline="") as f:
        metrics = list(csv.DictReader(f))
    assert len(metrics) == summary["total_independently_audited_runs"]
    assert len({(x["seed"], x["cell"], x["policy"]) for x in metrics}) == len(metrics)
    all_summaries = set()
    for row in metrics:
        seed, cell, policy = int(row["seed"]), row["cell"], row["policy"]
        assert seed in summary["seeds"] and cell in summary["cells"]
        assert row["audit_passed"] == "True"
        fixture = root / "fixtures" / f"s{seed}_{cell}"
        prefix = root / "runs" / f"s{seed}_{cell}_{policy}"
        ledger = prefix.with_suffix(".jsonl")
        worker = prefix.with_suffix(".sqlite")
        spool = root / "runs" / f"s{seed}_{cell}_{policy}_spool.sqlite"
        assert hashlib.sha256(ledger.read_bytes()).hexdigest() == row["ledger_sha256"]
        records = [json.loads(line) for line in ledger.read_text().splitlines() if line.strip()]
        if policy == "stage9_pushout_strict":
            result = audit_stage9(records, worker, fixture,
                                  require_mqtt=summary.get("transport") == "mqtt")
            assert result["status"] == "PASS_STAGE9_INDEPENDENT_PUSHOUT_QUEUE_AND_SQLITE_AUDIT"
            all_offers = [x for x in records if x.get("type") == "offer"]
            routine = [x for x in all_offers if x["trusted_class"] == "ROUTINE"]
            C = sum(x["terminal"] == "COMPLETED" for x in routine)/len(routine)
        else:
            result = audit_stage10(records, worker, spool, fixture,
                                   require_mqtt=summary.get("transport") == "mqtt")
            C = result["C"]
        for metric, observed in (("U",result["U"]),("R",result["R"]),("C",C)):
            assert abs(float(row[metric])-observed) < 1e-12, (
                f"{prefix} altered aggregate {metric}")
        all_summaries.add((cell, policy))
    assert all_summaries == {(c,p) for c in summary["cells"] for p in
                            {x["policy"] for x in metrics}}
    return {"pilot":str(root),"run_count":len(metrics),
            "cells":summary["cells"],"seeds":summary["seeds"],
            "status":"INDEPENDENT_RAW_AND_DB_REAUDIT_PASS_NO_INFERENCE"}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pilot-dir",type=Path,required=True,nargs="+")
    a=p.parse_args()
    out=[verify_dir(path) for path in a.pilot_dir]
    seen=set()
    for batch in out:
        assert not seen.intersection(batch["seeds"]), "Overlapping development seed batches"
        seen.update(batch["seeds"])
    print(json.dumps({"status":"ALL_STAGE10_DEVELOPMENT_EVIDENCE_REAUDITED",
                      "total_runs":sum(x["run_count"] for x in out),
                      "batches":out},sort_keys=True,indent=2))


if __name__ == "__main__":
    main()
