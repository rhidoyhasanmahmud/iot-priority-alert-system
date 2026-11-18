#!/usr/bin/env python3
"""Stage 5I: fail-closed evidence-readiness gate; never an SLA calibrator.

Validates the research evidence *packet*, independently audits a supplied Stage
5H SQLite/JSONL pair (or basic Stage 5D lifecycle), and lists exactly which
external evidentiary controls are still missing. No synthetic trace can pass
as a representative field trace merely by relabeling its metadata.

Examples (from repository root):
  python experiments/stage5i_evidence_gate.py --self-test
  python experiments/stage5i_evidence_gate.py \
    --packet experiments/fixtures/stage5i_evidence_register.json \
    --ledger run.jsonl --sqlite run.sqlite --output readiness.json
"""

import argparse
import copy
import json
from pathlib import Path
import re

from stage5d_lifecycle_audit import audit as lifecycle_audit
from stage5h_joint_audit import gate as stage5h_gate


class EvidenceError(ValueError):
    pass


REQUIRED_EVIDENCE = {
    "application_owner_approval": "application owner accepted actual scenario and completion effect",
    "privacy_authorization": "approved safe handling/anonymization and data-use scope",
    "device_source_provenance": "source deployment/device population and provenance",
    "source_sampling_design": "documented observation window, sampling and selection limits",
    "source_capture_completeness": "published/source counts and gap/censoring coverage",
    "pre_gateway_drop_accounting": "broker/upstream throttling, loss and drop accounting",
    "trusted_class_mapping": "reviewed trusted urgency/routine classification semantics",
    "clock_boundary_validation": "one measured clock domain per elapsed-time subtraction",
    "real_handler_design": "actual application processing/transaction completion path",
    "effect_commit_verification": "independent observed effect/equivalent persisted record",
    "handler_resource_profile": "measured CPU/RAM/storage/backend and load envelope",
    "service_sampling_design": "cold/warm, class, temporal repeats and failure sampling",
    "incident_failure_model": "outage/redelivery/retry/dedup and termination semantics",
    "operator_threshold_decision": "operator-backed local-offer deadline/failure/access/K evidence",
    "stage4b_novelty_signoff": "dated full-text/citation/supervisor novelty decision",
    "stage6_preregistration": "frozen matched baselines, workloads and statistical comparisons",
}


def check(condition, label):
    if not condition:
        raise EvidenceError(label)


def evidence_ref_valid(ref):
    if ref is None:
        return False
    check(isinstance(ref, dict) and set(ref) == {"uri", "sha256", "reviewer", "reviewed_at_utc"},
          "evidence reference must have exact uri/sha256/reviewer/reviewed_at_utc fields")
    check(isinstance(ref["uri"], str) and ref["uri"].strip(), "evidence URI missing")
    check(isinstance(ref["sha256"], str) and re.fullmatch(r"[0-9a-f]{64}", ref["sha256"]),
          "evidence SHA-256 must be a 64-character lower-case digest")
    check(isinstance(ref["reviewer"], str) and ref["reviewer"].strip(),
          "evidence reviewer missing")
    check(isinstance(ref["reviewed_at_utc"], str) and
          re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", ref["reviewed_at_utc"]),
          "evidence review timestamp needs ISO-8601 UTC seconds")
    return True


def validate_parameter_form(params):
    check(isinstance(params, dict), "parameter_proposals must be object")
    fields = {"urgent_deadline_ms", "epsilon_absolute", "routine_tau_ms",
              "gamma_minimum", "waiting_capacity_K", "deadline_origin"}
    check(set(params) == fields, "parameter_proposals fields not aligned with RQ")
    for key in ("urgent_deadline_ms", "routine_tau_ms"):
        value = params[key]
        check(value is None or (type(value) in (int, float) and 0 < value < 1e9),
              f"{key} must be absent or finite positive milliseconds")
    for key in ("epsilon_absolute", "gamma_minimum"):
        value = params[key]
        check(value is None or (type(value) in (int, float) and 0 <= value <= 1),
              f"{key} must be absent or a [0,1] fraction")
    value = params["waiting_capacity_K"]
    check(value is None or (type(value) is int and 0 <= value <= 1_000_000),
          "waiting_capacity_K must be absent or a nonnegative integer")
    check(params["deadline_origin"] == "local_offer",
          "primary RQ measures urgent completion relative to local offer, not publisher time")
    return [key for key in fields if key != "deadline_origin" and params[key] is None]


def assess(packet, ledger, *, sqlite_file=None):
    check(isinstance(packet, dict), "packet must be an object")
    check(packet.get("schema_version") == "stage5i.v1", "unknown evidence-packet schema")
    check(isinstance(packet.get("packet_id"), str) and packet["packet_id"],
          "packet_id required")
    origin = packet.get("capture_origin")
    check(origin in ("synthetic_lab", "controlled_testbed", "observed_deployment"),
          "capture_origin must explicitly declare where the workload arose")
    check(isinstance(packet.get("capture_scope"), str) and packet["capture_scope"].strip(),
          "capture_scope must disclose observation scope")
    evidence = packet.get("evidence")
    check(isinstance(evidence, dict) and set(evidence) == set(REQUIRED_EVIDENCE),
          "evidence register must contain exactly the required controls")

    missing = [key for key, value in evidence.items() if not evidence_ref_valid(value)]
    params_missing = validate_parameter_form(packet.get("parameter_proposals"))
    if any(packet["parameter_proposals"][k] is not None for k in (
            "urgent_deadline_ms", "epsilon_absolute", "routine_tau_ms",
            "gamma_minimum", "waiting_capacity_K")):
        check(evidence["operator_threshold_decision"] is not None,
              "numerical parameter declared without cited operator decision")

    check(isinstance(ledger, list) and ledger, "an actual ledger is mandatory")
    # Generic lifecycle audit is independent of the emitter. Stage5H requires
    # stronger source/commit validation and an ACTUAL SQLite backup.
    manifest = next((x for x in ledger if isinstance(x, dict) and x.get("type") == "manifest"), None)
    check(manifest is not None, "missing manifest")
    scenario = manifest.get("scenario_id", "")
    joint_fixture = isinstance(scenario, str) and scenario.startswith("stage5h_")
    if joint_fixture:
        check(sqlite_file is not None, "Stage5H requires independent SQLite backup")
        audit = stage5h_gate(ledger, sqlite_file)
        technical_level = "STAGE5H_SQLITE_SOURCE_AND_LIFECYCLE_VERIFIED"
    else:
        check(sqlite_file is None, "non-Stage5H DB must have its own independent effect verifier")
        audit = lifecycle_audit(ledger)
        technical_level = "BASIC_STAGE5D_LIFECYCLE_ONLY"

    blockers = []
    if origin == "synthetic_lab":
        blockers.append("origin_is_synthetic_lab")
    if joint_fixture:
        blockers.append("stage5h_manifest_is_deterministic_synthetic_fixture")
    if origin == "controlled_testbed":
        blockers.append("testbed_generalization_requires_manual_scope_approval")
    if technical_level == "BASIC_STAGE5D_LIFECYCLE_ONLY":
        blockers.append("effect_commit_not_independently_verified_by_this_gate")
    blockers.extend("missing_evidence:" + x for x in missing)
    blockers.extend("unset_parameter:" + x for x in params_missing)
    if audit.get("publisher_log_complete") is not True:
        blockers.append("publisher_log_incomplete")
    if audit.get("receiver_capture_complete") is not True:
        blockers.append("receiver_capture_incomplete")
    if audit.get("published_ids_without_callback") != 0:
        blockers.append("unreconciled_published_ids")
    if audit.get("unresolved_offers") != 0:
        blockers.append("unfinished_offer_population")

    return {
        "packet_id": packet["packet_id"], "schema_version": "stage5i.v1",
        "capture_origin_declared": origin,
        "technical_audit_level": technical_level,
        "technical_audit_passed": True,
        "published_unique": audit.get("published_unique"),
        "offered_unique": audit.get("offered_unique"),
        "admitted": audit.get("admitted"),
        "rejected": audit.get("rejected"),
        "independently_matched_db_rows": audit.get("db_rows_independently_matched"),
        "missing_evidence_controls": missing,
        "unset_operational_parameters": params_missing,
        "blockers": blockers,
        "eligible_for_manual_research_gate_review": len(blockers) == 0,
        "stage6_permission": "NEVER_AUTOMATIC_HUMAN_SIGNOFF_REQUIRED",
        "verdict": "NOT_READY" if blockers else "READY_FOR_INDEPENDENT_HUMAN_REVIEW_ONLY",
        "scope_warning": (
            "A SHA-256/URI in supplied metadata is an assertion, not independently verified "
            "ownership or authenticity. Only the cited evidence's reviewers can approve "
            "application representativeness, numeric budgets and novelty."),
    }


def self_test():
    import tempfile
    from stage5h_joint_gateway import run_joint

    blank = {
        "schema_version": "stage5i.v1", "packet_id": "selftest-fake-lab",
        "capture_origin": "synthetic_lab", "capture_scope": "in-process fictional lab",
        "evidence": {k: None for k in REQUIRED_EVIDENCE},
        "parameter_proposals": {
            "urgent_deadline_ms": None, "epsilon_absolute": None,
            "routine_tau_ms": None, "gamma_minimum": None,
            "waiting_capacity_K": None, "deadline_origin": "local_offer",
        },
    }
    with tempfile.TemporaryDirectory(prefix="stage5i-gate-test-") as tmp:
        db = Path(tmp) / "fixture.sqlite"
        rows, _ = run_joint(transport="inproc", shape="base", count=12, seed=101,
                            K=3, urgent_deadline_ms=50, routine_tau_ms=50,
                            sqlite_output=db)
        report = assess(blank, rows, sqlite_file=db)
        assert report["technical_audit_passed"]
        assert report["independently_matched_db_rows"] == report["admitted"]
        assert report["verdict"] == "NOT_READY"
        assert len(report["missing_evidence_controls"]) == len(REQUIRED_EVIDENCE)
        assert len(report["unset_operational_parameters"]) == 5
        print("PASS verified synthetic SQLite effect still NOT READY for field calibration")

        fake_refs = {k: {"uri": "internal://reviewed/" + k,
                         "sha256": "a" * 64, "reviewer": "test-only",
                         "reviewed_at_utc": "2026-11-16T00:00:00Z"}
                     for k in REQUIRED_EVIDENCE}
        forged = copy.deepcopy(blank)
        forged["capture_origin"] = "observed_deployment"
        forged["evidence"] = fake_refs
        forged["parameter_proposals"].update(urgent_deadline_ms=50,
                    epsilon_absolute=.2, routine_tau_ms=30,
                    gamma_minimum=.9, waiting_capacity_K=3)
        result = assess(forged, rows, sqlite_file=db)
        assert result["verdict"] == "NOT_READY" and any(
            "stage5h_manifest_is_deterministic" in x for x in result["blockers"])
        print("PASS forged deployment metadata CANNOT upgrade Stage5H synthetic trace")

        mutations = [
            ("missing evidence control", lambda x: x["evidence"].pop("privacy_authorization")),
            ("boolean K", lambda x: x["parameter_proposals"].update(waiting_capacity_K=True)),
            ("negative tau", lambda x: x["parameter_proposals"].update(routine_tau_ms=-10)),
            ("invalid epsilon", lambda x: x["parameter_proposals"].update(epsilon_absolute=1.1)),
            ("wrong deadline origin", lambda x: x["parameter_proposals"].update(deadline_origin="source_wall")),
            ("fake ref hash", lambda x: x["evidence"].update(privacy_authorization={
                "uri": "internal://fake", "sha256": "fake", "reviewer": "test",
                "reviewed_at_utc": "2026-11-16T00:00:00Z"})),
            ("numbers without owner decision", lambda x: x["parameter_proposals"].update(
                urgent_deadline_ms=50)),
        ]
        for label, change in mutations:
            trial = copy.deepcopy(blank)
            change(trial)
            try:
                assess(trial, rows, sqlite_file=db)
            except EvidenceError:
                print("PASS rejected invalid input:", label)
            else:
                raise AssertionError("Failed to reject " + label)
        try:
            assess(blank, rows)
        except EvidenceError:
            print("PASS rejected Stage5H ledger without independently inspectable SQLite")
        else:
            raise AssertionError("Stage5H without SQLite was accepted")
        print("PASS Stage 5I preliminary evidence gate: one positive audit, 9 safety cases")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--packet", type=Path)
    ap.add_argument("--ledger", type=Path)
    ap.add_argument("--sqlite", type=Path)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    if args.packet is None or args.ledger is None:
        ap.error("--packet and --ledger required; no readiness from an empty packet")
    packet = json.loads(args.packet.read_text(encoding="utf-8"))
    rows = [json.loads(s) for s in args.ledger.read_text(encoding="utf-8").splitlines()
            if s.strip()]
    result = assess(packet, rows, sqlite_file=args.sqlite)
    serialized = json.dumps(result, indent=2, sort_keys=True)
    if args.output is None:
        print(serialized)
    else:
        with args.output.open("x", encoding="utf-8") as out:
            out.write(serialized + "\n")
        print("Saved readiness diagnosis (not certification):", args.output)
    if result["verdict"] == "NOT_READY":
        print("BLOCKED: " + ", ".join(result["blockers"][:5]) +
              f"; total blockers={len(result['blockers'])}")
        # NOT_READY is a normal diagnostic output, not a malformed input error.


if __name__ == "__main__":
    main()
