#!/usr/bin/env python3
"""Fixture-contract regression tests; no scientific performance measurements."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from stage5k2_independent_audit import FixtureAuditError, audit, audit_pair
from stage5k2_workload_fixture import save_fixture


PARAMS = {"seed": 1729, "count": 60, "urgent_count": 15,
          "horizon_ns": 1_000_000_000, "shape": "smooth", "dispersion": "flat"}


class CandidateFixtureContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)

    def fixture(self, name: str, **changes: object) -> Path:
        values = PARAMS | changes
        root = self.base / name
        save_fixture(root, **values)
        return root

    def test_independent_audit_accepts_valid_fixture(self) -> None:
        found = audit(self.fixture("valid"))
        self.assertEqual(found["count"], 60)
        self.assertEqual(found["urgent_count"], 15)
        self.assertEqual(found["offered_synthetic_work_units"], 240)
        self.assertEqual(found["status"], "PASS_SYNTHETIC_FILE_INTEGRITY_ONLY")

    def test_reproducible_output_across_directories(self) -> None:
        a, b = self.fixture("a"), self.fixture("b")
        for name in ["manifest.json", "offers.jsonl", "hidden_work.jsonl"]:
            self.assertEqual((a / name).read_bytes(), (b / name).read_bytes())

    def test_no_hidden_work_in_offer_visible_channel(self) -> None:
        root = self.fixture("firewall", dispersion="variable")
        rows = [json.loads(line) for line in (root / "offers.jsonl").read_text().splitlines()]
        self.assertTrue(all(set(row) == {"fixture_id", "event_id", "trusted_class",
                                              "planned_offer_offset_ns"} for row in rows))
        self.assertFalse(any("work" in key or "future" in key for row in rows for key in row))
        self.assertEqual(audit(root)["offered_synthetic_work_units"], 240)

    def test_burst_pair_changes_shape_not_population_or_horizon(self) -> None:
        smooth = self.fixture("smooth")
        burst = self.fixture("burst", shape="clustered")
        self.assertEqual(audit_pair(smooth, burst, "burst_shape")["count"], 60)

    def test_overload_pair_changes_only_horizon(self) -> None:
        normal = self.fixture("normal")
        overload = self.fixture("overload", horizon_ns=500_000_000)
        self.assertEqual(audit_pair(normal, overload, "intensity")["count"], 60)

    def test_work_variability_pair_preserves_mean_and_times(self) -> None:
        flat = self.fixture("flat")
        varying = self.fixture("varying", dispersion="variable")
        self.assertEqual(audit_pair(flat, varying, "work_dispersion")["offered_synthetic_work_units"], 240)

    def test_negative_tampered_offer_detected(self) -> None:
        root = self.fixture("bad_offer")
        data = (root / "offers.jsonl").read_bytes()
        (root / "offers.jsonl").write_bytes(data.replace(b'"trusted_class":"urgent"',
                                                        b'"trusted_class":"routine"', 1))
        with self.assertRaisesRegex(FixtureAuditError, "hash mismatch"):
            audit(root)

    def test_negative_tampered_hidden_work_detected(self) -> None:
        root = self.fixture("bad_work")
        data = (root / "hidden_work.jsonl").read_bytes()
        (root / "hidden_work.jsonl").write_bytes(data.replace(b'"synthetic_required_work_units":4',
                                                              b'"synthetic_required_work_units":999', 1))
        with self.assertRaisesRegex(FixtureAuditError, "hash mismatch"):
            audit(root)

    def test_negative_forged_manifest_count_detected(self) -> None:
        root = self.fixture("bad_manifest")
        file = root / "manifest.json"
        data = json.loads(file.read_text())
        data["count"] += 2
        file.write_text(json.dumps(data))
        with self.assertRaisesRegex(FixtureAuditError, "cardinalities"):
            audit(root)

    def test_negative_incompatible_work_pair_detected(self) -> None:
        a = self.fixture("a")
        b = self.fixture("b", dispersion="variable", shape="clustered")
        with self.assertRaisesRegex(FixtureAuditError, "work"):
            audit_pair(a, b, "burst_shape")

    def test_invalid_configuration_rejected_without_creating_directory(self) -> None:
        name = self.base / "invalid"
        with self.assertRaises(ValueError):
            save_fixture(name, **(PARAMS | {"count": 61}))
        self.assertFalse(name.exists())

    def test_existing_fixture_never_overwritten(self) -> None:
        root = self.fixture("already_there")
        before = (root / "manifest.json").read_bytes()
        with self.assertRaises(FileExistsError):
            save_fixture(root, **PARAMS)
        self.assertEqual(before, (root / "manifest.json").read_bytes())


if __name__ == "__main__":
    unittest.main(verbosity=2)
