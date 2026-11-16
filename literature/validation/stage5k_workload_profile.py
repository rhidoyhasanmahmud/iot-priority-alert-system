#!/usr/bin/env python3
"""Stage 5K: descriptive workload evidence profile, NOT field calibration.

Requires the entire raw Stage 5J batch (JSONL, SQLite and child logs). Before
describing any measurements, its independent Stage 5J gate checks the source,
paired design, all saved SQLite effects and SHA-256 integrity.

Measured handler durations are available ONLY for *admitted* jobs. The missing
counterfactual service demands of rejected jobs cannot be inferred, especially
when varying K or the scheduling policy. No empirical SLA/novelty is claimed.
"""

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import statistics
import tempfile

from stage5j_batch_audit import audit_batch
from stage5d_lifecycle_audit import AuditError, require


CLASSES = ("URGENT", "ROUTINE")


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def nearest_rank(values, p):
    if not values:
        return None
    ordered = sorted(values)
    return ordered[max(0, math.ceil(p * len(ordered)) - 1)]


def duration_stats_ns(values):
    if not values:
        return {"n_committed_only": 0, "min_ns": None, "mean_ns": None,
                "median_ns": None, "p95_ns": None, "max_ns": None, "cv": None}
    mean = statistics.fmean(values)
    return {"n_committed_only": len(values), "min_ns": min(values),
            "mean_ns": mean, "median_ns": statistics.median(values),
            "p95_ns": nearest_rank(values, .95), "max_ns": max(values),
            "cv": statistics.pstdev(values) / mean if mean > 0 else None}


def make_profile(batch, directory, *, manifest_sha256):
    """Fail closed on raw evidence; never upgrade synthetic to representative."""
    technical = audit_batch(batch, directory)
    require(technical["technical_audit"] == "PASS", "Stage5J audit did not pass")
    require(technical["field_calibration"] == "NOT_AVAILABLE", "unexpected field claim")
    directory = Path(directory)
    output_runs = []
    by_shape_K = {}
    for row in batch["runs"]:
        path = directory / row["ledger_path"]
        with path.open(encoding="utf-8") as f:
            trace = [json.loads(line) for line in f if line.strip()]
        offers = [r for r in trace if r["type"] == "offer"]
        admitted = [r for r in offers if r["terminal"] == "COMPLETED"]
        rejected = [r for r in offers if r["terminal"] == "REJECTED"]
        require(len(offers) == row["offered_unique"] and
                len(admitted) == row["admitted"] and
                len(rejected) == row["rejected"],
                "class counts must reconcile with independently audited offers")

        offered_by_class = {c: sum(o["trusted_class"] == c for o in offers)
                            for c in CLASSES}
        admitted_by_class = {c: sum(o["trusted_class"] == c for o in admitted)
                             for c in CLASSES}
        rejected_by_class = {c: sum(o["trusted_class"] == c for o in rejected)
                             for c in CLASSES}
        require(sum(offered_by_class.values()) == len(offers) and
                sum(admitted_by_class.values()) == len(admitted) and
                sum(rejected_by_class.values()) == len(rejected),
                "unsupported/invalid trusted class label")
        require(all(offered_by_class[c] == admitted_by_class[c] + rejected_by_class[c]
                    for c in CLASSES), "offered-class reconciliation failed")
        for o in admitted:
            require(type(o["db_service_ns"]) is int and o["db_service_ns"] > 0,
                    "only positive measured committed durations may be profiled")
        values = [o["db_service_ns"] for o in admitted]
        class_stats = {c: duration_stats_ns([o["db_service_ns"] for o in admitted
                                            if o["trusted_class"] == c])
                       for c in CLASSES}
        result = {
            "seed": row["seed"], "K": row["K"], "shape": row["shape"],
            "raw_ledger_sha256": row["ledger_sha256"],
            "raw_sqlite_sha256": row["db_sha256"],
            "source_sha256": row["source_sha256"],
            "offered_unique": len(offers), "committed": len(admitted),
            "rejected": len(rejected), "offered_by_class": offered_by_class,
            "committed_by_class": admitted_by_class,
            "rejected_by_class": rejected_by_class,
            "committed_service_ns": duration_stats_ns(values),
            "committed_service_by_class_ns": class_stats,
            "planned_source_horizon_ns": row["source_horizon_ns"],
            "observed_offer_span_ns": row["observed_offer_span_ns"],
            "sampled_rss_max_bytes": row["sampled_rss_max_bytes"],
            "child_user_cpu_s": row["child_user_cpu_s"],
            "child_system_cpu_s": row["child_system_cpu_s"],
        }
        output_runs.append(result)
        group = by_shape_K.setdefault((row["shape"], row["K"]),
                                      {"runs": 0, "offered": 0, "committed": 0,
                                       "rejected": 0})
        for key, value in (("runs", 1), ("offered", len(offers)),
                           ("committed", len(admitted)), ("rejected", len(rejected))):
            group[key] += value

    total_offered = sum(r["offered_unique"] for r in output_runs)
    total_committed = sum(r["committed"] for r in output_runs)
    total_rejected = sum(r["rejected"] for r in output_runs)
    require((total_offered, total_committed, total_rejected) ==
            (technical["total_synthetic_offers"],
             technical["total_committed_lab_sqlite_rows"],
             technical["total_full_buffer_rejects"]),
            "profile and independently audited batch totals disagree")
    return {
        "schema_version": "stage5k.synthetic-descriptive.v1",
        "stage": "5K", "status": "DESCRIPTIVE_AUDIT_ONLY_NOT_CALIBRATED",
        "input_batch_sha256": manifest_sha256,
        "input_stage5j_transport": technical["transport"],
        "independent_raw_evidence_audit": "PASS",
        "seeds": technical["seeds"], "run_count": len(output_runs),
        "host_fingerprint": batch["manifest"]["host"],
        "source_provenance": "DETERMINISTIC_SYNTHETIC_STAGE5G_ONLY",
        "handler_provenance": "FICTIONAL_SQLITE_CONTEXT_RULE_COMMIT_ONLY",
        "timing_targets_status": "ARTIFICIAL_DEBUG_ONLY_NOT_OWNER_APPROVED",
        "field_representativeness": "NOT_ESTABLISHED",
        "new_policy_evidence": "NOT_PERFORMED_FIFO_ONLY",
        "offered_work_demand": "UNKNOWN_FOR_REJECTED_OFFERS",
        "service_sampling_bias": ("Service duration observed only for committed/admitted "
                                  "jobs. Rejected offers have no measured counterfactual "
                                  "processing duration; do not infer offered-work distributions "
                                  "or compare conditional service quantiles as causal effects."),
        "resource_bias": "10ms sampled RSS is not peak; child CPU includes startup/teardown",
        "scientific_inference": "NOT_AUTHORIZED_SYNTHETIC_SMALL_LAB_AND_DEPENDENT_EVENTS",
        "stage6_research_ready": False,
        "blocking_decisions": [
            "supervisor_approval_of_controlled_synthetic_scope",
            "defensible_arrival_and_class_mix_assumptions_or_external_trace",
            "representative_handler_service_workload_or_justified_sensitivity_model",
            "operator_or_explicitly_nonoperational_deadline_epsilon_tau_gamma_K",
            "held_out_independent_runs_and_fixed_resource_envelope",
            "stage4b_novelty_comparison_and_supervisor_decision",
            "stage6_preregistered_policy_baselines_and_statistical_protocol",
        ],
        "totals_accounting_only": {"offered": total_offered,
                                   "committed": total_committed,
                                   "rejected": total_rejected},
        "by_shape_and_K_accounting_only": [
            {"shape": shape, "K": K, **entry}
            for (shape, K), entry in sorted(by_shape_K.items())],
        "per_run_diagnostics_no_independent_event_inference": output_runs,
    }


def profile_file(batch_path):
    batch_path = Path(batch_path)
    batch = json.loads(batch_path.read_text(encoding="utf-8"))
    return make_profile(batch, batch_path.parent, manifest_sha256=digest(batch_path))


def self_test():
    from stage5j_controlled_pilot import run_batch
    with tempfile.TemporaryDirectory(prefix="stage5k-profile-test-") as temp:
        dest = Path(temp) / "batch"
        batch = run_batch(output_dir=dest, transport="inproc", seeds=(41, 42),
                          events=12, capacities=(0, 1), shuffle_seed=81)
        result = profile_file(dest / "batch.json")
        assert result["run_count"] == 12
        assert result["totals_accounting_only"]["offered"] == 144
        assert sum(x["n_committed_only"] for r in result[
            "per_run_diagnostics_no_independent_event_inference"]
                   for x in [r["committed_service_ns"]]) == result[
                       "totals_accounting_only"]["committed"]
        assert not result["stage6_research_ready"]
        print("PASS Stage5K 12-run positive descriptive smoke; no field readiness")
        wrong = copy.deepcopy(batch)
        wrong["manifest"]["workload_kind"] = "real_telemetry"
        try:
            make_profile(wrong, dest, manifest_sha256="debug")
        except AuditError:
            print("PASS rejected synthetic source relabelled as real")
        else:
            raise AssertionError("fake provenance passed")
        wrong = copy.deepcopy(batch)
        wrong["runs"][0]["admitted"] += 1
        try:
            make_profile(wrong, dest, manifest_sha256="debug")
        except AuditError:
            print("PASS rejected a forged completed count")
        else:
            raise AssertionError("fake count passed")
        with (dest / batch["runs"][0]["ledger_path"]).open("a", encoding="utf-8") as f:
            f.write("{}\n")
        try:
            profile_file(dest / "batch.json")
        except AuditError:
            print("PASS rejected tampered raw ledger")
        else:
            raise AssertionError("tampered ledger passed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if args.batch is None or args.output is None:
        parser.error("--batch and --output required; raw files are mandatory")
    report = profile_file(args.batch)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)
        f.write("\n")
    print("PASS Stage5K descriptive integrity gate; scientific calibration NOT established")


if __name__ == "__main__":
    main()
