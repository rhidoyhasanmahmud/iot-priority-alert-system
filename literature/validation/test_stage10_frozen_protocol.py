#!/usr/bin/env python3
"""Stage10 immutable protocol, seed isolation and independent batch red-team."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from stage10_frozen_study import load_protocol,plan,PROTOCOL_SHA256,study
from stage10_independent_analysis import audit_study


HERE=Path(__file__).resolve().parent
PROTOCOL=HERE/"stage10_frozen_protocol.json"


class FrozenIdentityTest(unittest.TestCase):
    def test_frozen_hash_and_matched_600_trial_plan(self):
        c=load_protocol(PROTOCOL)
        self.assertEqual(len(PROTOCOL_SHA256),64)
        cases=plan(c,pilot=False,pilot_seeds=())
        self.assertEqual(len(cases),600)
        self.assertEqual(len(set(cases)),600)
        self.assertEqual({s for s,_,_,_ in cases},set(range(230001,230031)))
        self.assertEqual({(s,n,k) for s,n,k,_ in cases},
                         {(s,n,k) for s in range(230001,230031)
                          for n,k in (("burst",3),("smooth",3),
                                      ("overload",3),("variable",3),("burst",0))})

    def test_known_tuning_and_stage9_seeds_excluded(self):
        c=load_protocol(PROTOCOL)
        for seed in (9001,9008,9010,210001,220001,220030):
            self.assertNotIn(seed,c["holdout_seeds"])
        for seed in (220001,220030,230001,230030):
            with self.assertRaises(ValueError):
                plan(c,pilot=True,pilot_seeds=(seed,))
        with self.assertRaises(ValueError):
            plan(c,pilot=True,pilot_seeds=(9008,9008))

    def test_pilot_never_plans_frozen_holdout_seeds(self):
        c=load_protocol(PROTOCOL)
        q=plan(c,pilot=True,pilot_seeds=(9006,9008))
        self.assertEqual(len(q),16)
        self.assertEqual({s for s,_,_,_ in q},{9006,9008})

    def test_reject_mutated_frozen_threshold_or_capacity(self):
        with TemporaryDirectory() as td:
            p=Path(td)/"mutated.json"
            p.write_text(PROTOCOL.read_text().replace('"urgent_deadline_ms": 50.0',
                                                      '"urgent_deadline_ms": 70.0'))
            with self.assertRaises(ValueError):
                load_protocol(p)


class FrozenEvidenceRedTeamTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=TemporaryDirectory(prefix="stage10-frozen-test-")
        cls.root=Path(cls.temp.name)/"pilot"
        cls.manifest=study(PROTOCOL,cls.root,pilot=True,pilot_seeds=(9006,),
                           git_revision="UNCOMMITTED")

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_all_eight_source_matched_raw_db_trials_reaudited(self):
        report=audit_study(self.root,PROTOCOL,pilot=True)
        self.assertEqual(report["raw_runs_reaudited"],8)
        self.assertEqual(report["four_policy_matched_blocks"],2)
        self.assertEqual(report["status"],"PASS_PILOT_NO_INFERENCE")

    def test_forged_manifests_and_incomplete_runs_rejected(self):
        original=(self.root/"study.json").read_text()
        try:
            row=json.loads(original)
            row["complete"]=False
            (self.root/"study.json").write_text(json.dumps(row))
            with self.assertRaises(ValueError):
                audit_study(self.root,PROTOCOL,pilot=True)
        finally:
            (self.root/"study.json").write_text(original)

    def test_reject_forged_metrics_even_if_per_run_sqlite_remains_valid(self):
        original=(self.root/"study.json").read_text()
        try:
            row=json.loads(original)
            row["runs"][0]["C"]=0.9999
            (self.root/"study.json").write_text(json.dumps(row))
            with self.assertRaises(ValueError):
                audit_study(self.root,PROTOCOL,pilot=True)
        finally:
            (self.root/"study.json").write_text(original)

    def test_reject_forged_spool_digest(self):
        original=(self.root/"study.json").read_text()
        try:
            row=json.loads(original)
            item=next(x for x in row["runs"] if x["spool_sha256"] is not None)
            item["spool_sha256"]="f"*64
            (self.root/"study.json").write_text(json.dumps(row))
            with self.assertRaises(ValueError):
                audit_study(self.root,PROTOCOL,pilot=True)
        finally:
            (self.root/"study.json").write_text(original)


if __name__=="__main__":
    unittest.main()
