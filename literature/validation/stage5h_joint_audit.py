#!/usr/bin/env python3
"""Independent Stage 5H synthetic MQTT -> finite-K -> SQLite evidence gate.

Unlike the emitter, this auditor does not import the joint gateway or SQLite
handler. It checks the publisher trace, callback/offer lifecycle, rule outcomes,
per-message commit spans, and *actual* separately exported SQLite rows.
The separate DB is a post-run backup, NOT proof of crash/power-loss durability.
"""

import argparse
import copy
import hashlib
import json
from pathlib import Path
import random
import sqlite3
import statistics
import tempfile

from stage5d_lifecycle_audit import AuditError, audit, nonnegative_int, require


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def expected_source(seed, count):
    rng = random.Random(seed)
    result = []
    for i in range(count):
        tamper = i % 4 == 0
        result.append({
            "event_id": f"s5g_{seed}_{i:05d}",
            "device_id": f"device_{rng.randrange(16):02d}",
            "kind": "tamper" if tamper else "health",
            "tamper": tamper,
            "battery_pct": rng.randrange(101),
        })
    return result


def expected_schedule(count, shape):
    gaps = [0] + [8_000_000] * (count - 1)
    if shape == "base":
        return gaps
    if shape == "overload":
        return [0] * count
    require(shape == "burst", "stage5h unknown source schedule")
    lo, hi = count // 3, 2 * count // 3
    removed = sum(gaps[lo:hi])
    for i in range(lo, hi):
        gaps[i] = 0
    outside = [i for i in range(1, count) if not lo <= i < hi]
    require(bool(outside), "burst has no outside slots")
    amount, remainder = divmod(removed, len(outside))
    for j, i in enumerate(outside):
        gaps[i] += amount + (j < remainder)
    return gaps


def quantile_ns(values, fraction):
    if not values:
        return None
    ordered = sorted(values)
    return ordered[max(0, int((len(ordered) * fraction) + .999999) - 1)]


def gate(rows, sqlite_file, *, require_mqtt=False):
    """Reject mismatched evidence; only return results for completed lab runs."""
    base = audit(rows)  # generic independent nonpreemptive lifecycle audit
    manifest = next(r for r in rows if r["type"] == "manifest")
    require(manifest.get("policy_id") == "fifo", "Stage5H must declare FIFO baseline")
    scenario = manifest.get("scenario_id", "")
    require(scenario.startswith("stage5h_"), "Stage5H scenario missing")
    parts = scenario.split("_")
    require(len(parts) == 3 and parts[1] in ("mqtt", "inproc") and
            parts[2] in ("base", "burst", "overload"), "bad Stage5H scenario")
    transport, shape = parts[1:]
    if require_mqtt:
        require(transport == "mqtt", "in-process transport cannot pass real MQTT gate")
    require(manifest.get("completion_boundary") == "post_SQLite_commit_return",
            "completion boundary must include SQLite commit return")
    require(manifest.get("worker_handler") == "stage5g_reference_sqlite_WAL_FULL",
            "unexpected Stage5H handler identity")
    require(manifest.get("db_reopen_exact") is True,
            "emitter reports failed in-run reopen comparison")
    require(manifest.get("receiver_capture_complete") is True,
            "receiver callbacks were incomplete")
    require(manifest.get("publisher_log_complete") is True,
            "publisher event list was incomplete")
    count = nonnegative_int(manifest.get("planned_unique"), "planned_unique")
    require(8 <= count <= 10_000, "unsupported Stage5H source count")
    seed = nonnegative_int(manifest.get("seed"), "fixture seed")
    expected = expected_source(seed, count)
    require(manifest.get("source_sha256") == hashlib.sha256(canonical(expected).encode()).hexdigest(),
            "source SHA-256 mismatch versus independently rebuilt fixture")
    schedule_hash = hashlib.sha256(canonical(expected_schedule(count, shape)).encode()).hexdigest()
    require(manifest.get("schedule_sha256") == schedule_hash,
            "schedule SHA-256 mismatch versus independent source schedule")
    require(manifest.get("trace_provenance") ==
            "synthetic_stage5g_fixture_sha256=" + manifest["source_sha256"],
            "trace provenance mismatch")
    require(base["published_unique"] == count and base["offered_unique"] == count,
            "not every unique published ID reached one validated gateway offer")
    require(base["published_ids_without_callback"] == 0,
            "unobserved published source ID")
    require(base["unresolved_offers"] == 0,
            "undrained lifecycle cannot be counted as final")
    require(base["invalid_attempts"] >= 1 and base["duplicates"] >= count // 13,
            "missing intended malformed or duplicate publisher probes")
    require(base["delivery_attempts"] >= count + count // 13 + 1,
            "missing expected callback attempts")
    require(base["admitted"] == base["measured_completed_service_n"],
            "admitted work missing a committed completion")
    expected_by_id = {src["event_id"]: src for src in expected}
    published = [r for r in rows if r["type"] == "published"]
    offers = [r for r in rows if r["type"] == "offer"]
    attempts = {r["attempt_id"]: r for r in rows if r["type"] == "attempt"}
    require([p["event_id"] for p in published] == [e["event_id"] for e in expected],
            "publisher order differs from declared source fixture")
    for p in published:
        require(p.get("source") == expected_by_id[p["event_id"]],
                f"published source payload mismatches fixture: {p['event_id']}")

    committed = {}
    db_services, queued_waits, cb_to_offer, commit_to_complete = [], [], [], []
    for offer in offers:
        eid = offer["event_id"]
        src = expected_by_id[eid]
        require(offer.get("validated_source") == src, f"{eid} accepted source mismatch")
        cls = "URGENT" if src["tamper"] else "ROUTINE"
        require(offer["trusted_class"] == cls, f"{eid} misclassified")
        cb_to_offer.append(offer["offer_ns"] - attempts[offer["attempt_id"]]["callback_ns"])
        require(offer["terminal"] in ("COMPLETED", "REJECTED"),
                f"{eid} incomplete or invalid terminal")
        fields = ("db_handler_start_ns", "db_commit_return_ns", "db_service_ns",
                  "db_rule_result", "db_result_json", "db_committed")
        if offer["terminal"] == "REJECTED":
            require(all(offer.get(k) is None for k in fields),
                    f"{eid} rejected job claims database operation")
            continue

        start = nonnegative_int(offer.get("start_ns"), f"{eid}.start")
        handler = nonnegative_int(offer.get("db_handler_start_ns"), f"{eid}.handler_start")
        commit = nonnegative_int(offer.get("db_commit_return_ns"), f"{eid}.commit_return")
        complete = nonnegative_int(offer.get("complete_ns"), f"{eid}.complete")
        service = nonnegative_int(offer.get("db_service_ns"), f"{eid}.db_service")
        require(offer["offer_ns"] <= start <= handler <= commit <= complete,
                f"{eid} start / handler / SQLite commit order incorrect")
        require(service == commit - handler and service > 0,
                f"{eid} service time must be measured lookup-to-commit span")
        require(offer.get("db_committed") is True, f"{eid} lacks commit success")
        dev_idx = int(src["device_id"].removeprefix("device_"))
        require(src["device_id"] == f"device_{dev_idx:02d}" and 0 <= dev_idx < 16,
                f"{eid} unexpected device context")
        rule = (("TAMPER_DISABLED" if dev_idx % 5 == 0 else "TAMPER_REVIEW")
                if src["tamper"] else ("LOW_BATTERY" if src["battery_pct"] < 20 else "HEALTHY"))
        result = canonical({"event_id": eid, "zone": f"zone_{dev_idx % 4}", "rule": rule})
        require(offer.get("db_rule_result") == rule and offer.get("db_result_json") == result,
                f"{eid} deterministic context/rule/JSON mismatch")
        committed[eid] = (src["device_id"], cls, rule, result)
        db_services.append(service)
        queued_waits.append(start - offer["offer_ns"])
        commit_to_complete.append(complete - commit)

    require(len(committed) == base["admitted"], "admitted count differs from verified commits")
    require(manifest.get("db_rows_reopened") == len(committed), "in-run reopen row count wrong")
    require(sqlite_file is not None, "independent SQLite evidence file is REQUIRED")
    sqlite_file = Path(sqlite_file)
    require(sqlite_file.is_file(), "SQLite evidence file missing")
    sha = hashlib.sha256(sqlite_file.read_bytes()).hexdigest()
    require(sha == manifest.get("sqlite_backup_sha256"),
            "SQLite backup fingerprint differs from emitter manifest")
    # URI mode=ro fails closed on missing files, rather than constructing a DB.
    con = sqlite3.connect(sqlite_file.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
        actual = {r[0]: tuple(r[1:]) for r in con.execute(
            "SELECT event_id, device_id, trusted_class, rule_result, result_json FROM handled_alerts")}
        context_count = con.execute("SELECT COUNT(*) FROM device_context").fetchone()[0]
    except sqlite3.DatabaseError as exc:
        raise AuditError(f"unreadable SQLite evidence: {exc}") from exc
    finally:
        con.close()
    require(integrity == "ok" and context_count == 16, "invalid SQLite schema/context")
    require(actual == committed, "SQLite persisted row contents differ from admitted completions")
    return {**base, "stage": "5H", "transport": transport, "shape": shape,
            "synthetic_fixture_verified": True,
            "db_independently_reopened": True,
            "db_rows_independently_matched": len(actual),
            "db_backup_sha256": sha,
            "db_handler_service_p50_ns": statistics.median(db_services) if db_services else None,
            "db_handler_service_p95_ns": quantile_ns(db_services, .95),
            "offer_to_start_p95_ns": quantile_ns(queued_waits, .95),
            "callback_to_offer_p95_ns": quantile_ns(cb_to_offer, .95),
            "commit_to_completion_p95_ns": quantile_ns(commit_to_complete, .95),
            "scope": "SYNTHETIC single-host MQTT/SQLite lab only; no field / novel policy / SLA sign-off"}


def self_test(fixture=None, db_fixture=None):
    # This fixture generator is imported ONLY for self-test; gate() does not
    # depend on the emitting handler/gateway implementation.
    if fixture is None:
        from stage5h_joint_gateway import run_joint
        with tempfile.TemporaryDirectory(prefix="stage5h-audit-test-") as tmp:
            db = Path(tmp) / "fixture.sqlite"
            rows, _ = run_joint(transport="inproc", shape="burst", count=36,
                                seed=101, K=3, urgent_deadline_ms=50,
                                routine_tau_ms=50, sqlite_output=db)
            test_rows(rows, db)
    else:
        require(db_fixture is not None, "--test-fixture requires --sqlite")
        rows = [json.loads(line) for line in Path(fixture).read_text(encoding="utf-8").splitlines()
                if line.strip()]
        test_rows(rows, Path(db_fixture))


def test_rows(rows, db):
    summary = gate(rows, db)
    assert summary["db_independently_reopened"] and summary["offered_unique"] >= 8
    print("PASS independent audit of positive synthetic SQLite-backed fixture")

    def mutate_row(records, kind, **kwargs):
        next(x for x in records if x["type"] == kind).update(kwargs)

    mutations = [
        ("unsupported transport scenario", lambda d: d[0].update(scenario_id="stage5h_fake_burst")),
        ("source digest", lambda d: d[0].update(source_sha256="bad")),
        ("schedule digest", lambda d: d[0].update(schedule_sha256="bad")),
        ("missing SQLite reopen", lambda d: d[0].update(db_reopen_exact=False)),
        ("false receiver completeness", lambda d: d[0].update(receiver_capture_complete=False)),
        ("tampered publisher payload", lambda d: mutate_row(d, "published", source={"event_id": "fake"})),
        ("tampered offered source", lambda d: mutate_row(d, "offer", validated_source={})),
        ("wrong trusted class", lambda d: mutate_row(d, "offer", trusted_class="ROUTINE")),
        ("wrong SQL rule", lambda d: next(o for o in d if o["type"] == "offer" and o["terminal"] == "COMPLETED").update(db_rule_result="WRONG")),
        ("fake commit success", lambda d: next(o for o in d if o["type"] == "offer" and o["terminal"] == "COMPLETED").update(db_committed=False)),
        ("wrong handler span", lambda d: next(o for o in d if o["type"] == "offer" and o["terminal"] == "COMPLETED").update(db_service_ns=0)),
        ("unsaved published event", lambda d: d.pop(next(i for i, x in enumerate(d) if x["type"] == "offer"))),
        ("unverified backup digest", lambda d: d[0].update(sqlite_backup_sha256="f" * 64)),
    ]
    for name, update in mutations:
        variant = copy.deepcopy(rows)
        update(variant)
        try:
            gate(variant, db)
        except (AuditError, ValueError):
            print("PASS rejected forged/corrupt evidence:", name)
        else:
            raise AssertionError(f"auditor accepted corrupted ledger: {name}")
    # The fixture's real transport is inproc: merely relabeling is not proof.
    # A positive MQTT run must carry external broker/CI provenance.
    if rows[0]["scenario_id"].startswith("stage5h_inproc_"):
        try:
            gate(rows, db, require_mqtt=True)
        except AuditError:
            print("PASS rejected in-process evidence at MQTT-only gate")
        else:
            raise AssertionError("in-process run passed MQTT-only gate")

    with tempfile.TemporaryDirectory(prefix="stage5h-audit-tamper-") as tmp:
        dest = Path(tmp) / "corrupted.sqlite"
        dest.write_bytes(db.read_bytes())
        con = sqlite3.connect(dest)
        try:
            con.execute("UPDATE handled_alerts SET rule_result='FORGED' WHERE event_id = "
                        "(SELECT event_id FROM handled_alerts LIMIT 1)")
            con.commit()
        finally:
            con.close()
        try:
            gate(rows, dest)
        except AuditError:
            print("PASS rejected changed persisted SQLite rows")
        else:
            raise AssertionError("auditor accepted altered SQLite")
    print("PASS independent Stage5H audit positive and negative tests")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("jsonl", nargs="?", type=Path)
    p.add_argument("--sqlite", type=Path, help="post-run SQLite backup for independent SQL check")
    p.add_argument("--require-mqtt", action="store_true")
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--test-fixture", type=Path)
    args = p.parse_args()
    if args.self_test:
        self_test(args.test_fixture, args.sqlite)
        return
    if args.jsonl is None or args.sqlite is None:
        p.error("both JSONL ledger and --sqlite persisted evidence are required")
    rows = [json.loads(line) for line in args.jsonl.read_text(encoding="utf-8").splitlines()
            if line.strip()]
    print(json.dumps(gate(rows, args.sqlite, require_mqtt=args.require_mqtt),
                     sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
