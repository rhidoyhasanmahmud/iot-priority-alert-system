#!/usr/bin/env python3
"""Independent file/SQLite gate for artificial Stage 7 lab-service profiles."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import statistics


class CalibrationError(ValueError):
    pass


def require(ok: bool, message: str) -> None:
    if not ok:
        raise CalibrationError(message)


def pct(values: list[int], fraction: float) -> int:
    ordered = sorted(values)
    return ordered[max(0, min(len(ordered) - 1, int(len(ordered) * fraction + .999999) - 1))]


def audit(report_path: Path, db_path: Path) -> dict:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    require(report.get("status") ==
            "ARTIFICIAL_HOST_LAB_SERVICE_CHARACTERIZATION_ONLY_NOT_FIELD_CALIBRATION",
            "Missing scope restriction")
    require(report.get("measurement") == "PBKDF2_SHA256_cpu_then_reference_SQLite_WAL_FULL_commit",
            "Unknown handler calibration method")
    scale = report.get("iterations_per_unit")
    n = report.get("repetitions_per_work_unit")
    require(type(scale) is int and 100 <= scale <= 1_000_000 and
            type(n) is int and 5 <= n <= 100, "Invalid scale or repetition count")
    require(report.get("units") == [1, 4, 7], "Unexpected unit levels")
    rows = report.get("rows")
    require(isinstance(rows, list) and len(rows) == 3 * n, "Missing calibration raw rows")
    raw = b"".join((json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n").encode()
                   for row in rows)
    require(hashlib.sha256(raw).hexdigest() == report.get("rows_sha256"),
            "Raw calibration hash mismatch")
    ids = [row.get("event_id") for row in rows]
    require(all(type(eid) is str and eid.startswith("synthetic_calibration_") for eid in ids)
            and len(set(ids)) == len(rows), "Invalid or duplicate synthetic IDs")
    for row in rows:
        unit = row.get("units")
        require(type(unit) is int and unit in (1, 4, 7), "Unexpected work unit")
        require(row.get("iterations") == unit * scale and
                all(type(row.get(key)) is int and row[key] > 0 for key in
                    ("cpu_ns", "sqlite_ns", "cpu_plus_sqlite_ns")) and
                row["cpu_plus_sqlite_ns"] == row["cpu_ns"] + row["sqlite_ns"],
                "Inconsistent measured work and service spans")
        result = json.dumps({"event_id": row["event_id"], "rule": "HEALTHY", "zone": "zone_1"},
                            sort_keys=True, separators=(",", ":"))
        require(row.get("result_json") == result, "False expected SQLite rule/result")
    for unit in (1, 4, 7):
        sub = [row for row in rows if row["units"] == unit]
        require(len(sub) == n, "Unbalanced work-unit calibration samples")
        stats = report.get("by_unit", {}).get(str(unit), {})
        totals = [row["cpu_plus_sqlite_ns"] for row in sub]
        require(stats.get("samples") == n and
                stats.get("cpu_median_ns") == int(statistics.median([r["cpu_ns"] for r in sub])) and
                stats.get("sqlite_median_ns") == int(statistics.median([r["sqlite_ns"] for r in sub])) and
                stats.get("total_median_ns") == int(statistics.median(totals)) and
                stats.get("total_p05_ns") == pct(totals, .05) and
                stats.get("total_p95_ns") == pct(totals, .95),
                "Summary statistics do not reproduce from raw intervals")
    require(db_path.is_file(), "SQLite evidence required")
    require(hashlib.sha256(db_path.read_bytes()).hexdigest() == report.get("sqlite_sha256"),
            "SQLite backup raw hash mismatch")
    con = sqlite3.connect(db_path.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        require(con.execute("PRAGMA integrity_check").fetchone()[0] == "ok",
                "SQLite integrity failed")
        data = {row[0]: row[1:] for row in con.execute(
            "SELECT event_id, device_id, trusted_class, rule_result, result_json FROM handled_alerts")}
    finally:
        con.close()
    require(set(data) == set(ids), "Persisted calibrated IDs differ from source")
    for row in rows:
        require(data[row["event_id"]] == ("device_01", "ROUTINE", "HEALTHY", row["result_json"]),
                "Persisted calibration rule/result mismatch")
    return {"status": "PASS_ARTIFICIAL_LAB_SERVICE_EVIDENCE_ONLY",
            "work_levels": [1, 4, 7], "records": len(rows),
            "sqlite_rows": len(data), "field_calibrated": False}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--report", type=Path, required=True)
    p.add_argument("--sqlite", type=Path, required=True)
    args = p.parse_args()
    print(json.dumps(audit(args.report, args.sqlite), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
