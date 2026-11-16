#!/usr/bin/env python3
"""Independent file-level audit of *fictional* Stage 5K.2 candidate fixtures.

Does not import or trust the fixture generator. This audits reproducibility and
information separation, NOT physical representativeness or policy performance.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


OFFER_FIELDS = frozenset({"fixture_id", "event_id", "trusted_class", "planned_offer_offset_ns"})
WORK_FIELDS = frozenset({"event_id", "synthetic_required_work_units"})


class FixtureAuditError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise FixtureAuditError(message)


def parse_jsonl(data: bytes, label: str) -> list[dict]:
    rows = []
    for number, line in enumerate(data.splitlines(), 1):
        try:
            value = json.loads(line)
        except (ValueError, UnicodeError) as error:
            raise FixtureAuditError(f"{label} line {number}: invalid JSON: {error}") from error
        require(type(value) is dict, f"{label} line {number}: expected object")
        rows.append(value)
    require(bool(rows), f"{label}: no rows")
    return rows


def audit(root: Path) -> dict:
    try:
        manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
        offer_raw = (root / "offers.jsonl").read_bytes()
        work_raw = (root / "hidden_work.jsonl").read_bytes()
    except (OSError, ValueError) as error:
        raise FixtureAuditError(f"Missing/bad fixture file: {error}") from error

    require(type(manifest) is dict, "Manifest must be a JSON object")
    for file_tag, data in [("offer", offer_raw), ("hidden_work", work_raw)]:
        expected = manifest.get(f"{file_tag}_sha256")
        require(type(expected) is str and hashlib.sha256(data).hexdigest() == expected,
                f"{file_tag} raw hash mismatch")

    offers = parse_jsonl(offer_raw, "offers")
    work = parse_jsonl(work_raw, "hidden_work")
    count = manifest.get("count")
    urgent_count = manifest.get("urgent_count")
    horizon = manifest.get("planned_horizon_ns")
    require(type(count) is int and count >= 4 and count % 2 == 0, "Bad count")
    require(type(urgent_count) is int and 0 < urgent_count < count, "Bad urgent count")
    require(type(horizon) is int and horizon > 0, "Bad horizon")
    require(len(offers) == len(work) == count, "Source and hidden-work cardinalities differ")
    require(all(set(row) == OFFER_FIELDS for row in offers), "Forbidden or missing offer-visible fields")
    require(all(set(row) == WORK_FIELDS for row in work), "Forbidden or missing hidden-work fields")

    ids = [row["event_id"] for row in offers]
    work_ids = [row["event_id"] for row in work]
    require(all(isinstance(v, str) and v.startswith("synthetic-") for v in ids), "Invalid event ID")
    require(len(set(ids)) == count and ids == work_ids, "Event ID missing, duplicated or mispaired")
    require(all(row["fixture_id"] == manifest.get("fixture_id") for row in offers),
            "Wrong fixture ID in offers")
    classes = [row["trusted_class"] for row in offers]
    require(set(classes) <= {"urgent", "routine"}, "Unknown class")
    require(classes.count("urgent") == urgent_count, "Urgent count mismatch")
    require(classes.count("routine") == manifest.get("routine_count"), "Routine count mismatch")

    offsets = [row["planned_offer_offset_ns"] for row in offers]
    require(all(type(value) is int for value in offsets), "Non-integral source offset")
    require(offsets[0] == 0 and offsets[-1] == horizon, "Planned source horizon mismatch")
    require(all(a < b for a, b in zip(offsets, offsets[1:])), "Nonmonotonic/duplicate source times")
    require(manifest.get("first_offer_offset_ns") == offsets[0] and
            manifest.get("last_offer_offset_ns") == offsets[-1], "Wrong manifest source span")

    units = [row["synthetic_required_work_units"] for row in work]
    require(all(type(value) is int and value > 0 for value in units), "Invalid synthetic work")
    require(sum(units) == manifest.get("total_offered_synthetic_work_units"),
            "Wrong offered synthetic work total")
    require(sum(units) == count * 4 and manifest.get("mean_offered_synthetic_work_units") == 4,
            "Work mean unexpectedly differs from declared illustrative 4-unit model")
    dispersion = manifest.get("work_dispersion")
    if dispersion == "flat":
        require(set(units) == {4}, "Flat work profile inconsistent")
    elif dispersion == "variable":
        require(units.count(1) == units.count(7) == count // 2, "Variable work profile inconsistent")
    else:
        raise FixtureAuditError("Unsupported work profile")
    require(manifest.get("shape") in {"smooth", "clustered"}, "Unsupported shape")
    require(manifest.get("purpose") ==
            "synthetic_fixture_integrity_only_NOT_CALIBRATED_OR_SCIENTIFIC_RESULTS",
            "Fixture is not explicitly marked uncalibrated")

    return {"status": "PASS_SYNTHETIC_FILE_INTEGRITY_ONLY", "root": str(root),
            "count": count, "urgent_count": urgent_count, "planned_horizon_ns": horizon,
            "offered_synthetic_work_units": sum(units), "shape": manifest["shape"],
            "work_dispersion": dispersion, "offers": offers, "hidden": work}


def audit_pair(left_path: Path, right_path: Path, axis: str) -> dict:
    left = audit(left_path)
    right = audit(right_path)
    require(left["count"] == right["count"], "Pair changes offered job count")
    left_info = [(row["event_id"], row["trusted_class"]) for row in left["offers"]]
    right_info = [(row["event_id"], row["trusted_class"]) for row in right["offers"]]
    require(left_info == right_info, "Pair changes the ordered ID/class population")
    left_work = [row["synthetic_required_work_units"] for row in left["hidden"]]
    right_work = [row["synthetic_required_work_units"] for row in right["hidden"]]
    left_times = [row["planned_offer_offset_ns"] for row in left["offers"]]
    right_times = [row["planned_offer_offset_ns"] for row in right["offers"]]

    if axis == "burst_shape":
        require(left["planned_horizon_ns"] == right["planned_horizon_ns"], "Shape confounds intensity")
        require(left_work == right_work, "Shape confounds offered work")
        require(left["shape"] != right["shape"] and left_times != right_times,
                "No distinct burst shape")
    elif axis == "intensity":
        require(left["shape"] == right["shape"] and left["work_dispersion"] == right["work_dispersion"],
                "Intensity confounds shape/work family")
        require(left_work == right_work, "Intensity changes work assignments")
        require(left["planned_horizon_ns"] != right["planned_horizon_ns"], "No change in intensity")
    elif axis == "work_dispersion":
        require(left["planned_horizon_ns"] == right["planned_horizon_ns"] and left_times == right_times,
                "Work dispersion confounds arrival times")
        require(left["work_dispersion"] != right["work_dispersion"] and left_work != right_work,
                "No change in work dispersion")
        require(sum(left_work) == sum(right_work), "Work dispersion changes mean offered work")
    else:
        raise FixtureAuditError(f"Unsupported pair axis: {axis}")
    return {"status": "PASS_SYNTHETIC_PAIRED_CONTRACT_ONLY", "axis": axis,
            "count": left["count"], "offered_synthetic_work_units": sum(left_work)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture_dir", type=Path)
    parser.add_argument("--pair-with", type=Path)
    parser.add_argument("--axis", choices=["burst_shape", "intensity", "work_dispersion"])
    args = parser.parse_args()
    if bool(args.pair_with) != bool(args.axis):
        parser.error("--pair-with and --axis must be given together")
    result = (audit_pair(args.fixture_dir, args.pair_with, args.axis)
              if args.pair_with else audit(args.fixture_dir))
    for key in ["offers", "hidden"]:
        result.pop(key, None)
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
