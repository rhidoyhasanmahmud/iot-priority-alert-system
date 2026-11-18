#!/usr/bin/env python3
"""First-frozen Stage10 synthetic MQTT/SQLite study, fail-closed by construction.

Pilot uses ONLY reserved previously inspected seeds, with in-process delivery.
Holdout uses a pinned Git commit and new unseen source seeds 230001..230030.
Any partial run writes an incomplete manifest and cannot count as evidence.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import sqlite3
import subprocess
import sys

from stage5k2_workload_fixture import save_fixture


PROTOCOL_SHA256 = "c66ba9824418ba20fc08be4bcfbb71bc72bff5e04f5b03d38794ccd297fa1429"
PROTOCOL_ID = "STI-2026-STAGE10-BOUNDED-ROUTINE-RECOVERY-HELDOUT-V1"
POLICIES = ("fifo_deferred", "strict_deferred", "stage9_pushout_strict", "pushout_deferred")


def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda:stream.read(65536),b""):
            h.update(chunk)
    return h.hexdigest()


def load_protocol(path: Path) -> dict:
    if sha256(path) != PROTOCOL_SHA256:
        raise ValueError("Stage10 protocol changed after freeze")
    c=json.loads(path.read_text())
    seeds=c["holdout_seeds"]
    if (c["protocol_id"]!=PROTOCOL_ID or c["policies"]!=list(POLICIES)
            or c["experimental_runs"]!=600 or c["matched_policy_blocks"]!=150
            or c["transport"]!="mqtt" or c["source_count"]!=60 or c["urgent_count"]!=15
            or c["candidate"]!="pushout_deferred" or c["field_calibrated"] is not False
            or c["candidate_novelty_verified"] is not False
            or c["bounded_spool_pending_capacity_B"]!=8
            or c["policy_capacity"]!={"fifo_deferred":8,"strict_deferred":8,
                                      "stage9_pushout_strict":0,"pushout_deferred":8}
            or c["pbkdf2_iterations_per_work_unit"]!=10000
            or c["urgent_deadline_ms"]!=50.0 or c["routine_tau_ms"]!=20.0
            or c["execution"]["per_trial_timeout_s"]!=35
            or len(seeds)!=30 or seeds!=list(range(230001,230031))
            or set(seeds)&set(c["pilot_only_seeds"])
            or len(c["study_cells"])!=5):
        raise ValueError("Stage10 frozen factors/identity invalid")
    return c


def command(args:list[str], timeout:int)->str:
    p=subprocess.run(args, text=True,capture_output=True,timeout=timeout)
    if p.returncode:
        raise RuntimeError(f"Failed {Path(args[1]).name}: {p.stderr[-2400:]}\n{p.stdout[-600:]}")
    return p.stdout


def policy_order(config:dict, seed:int, scenario:str, K:int)->list[str]:
    material=f"stage10|{config['policy_within_block_shuffle_seed']}|{seed}|{scenario}|{K}"
    h=hashlib.sha256(material.encode()).digest()
    ps=list(POLICIES)
    random.Random(int.from_bytes(h[:8],"big")).shuffle(ps)
    return ps


def plan(config:dict, *, pilot:bool, pilot_seeds:tuple[int,...])->list[tuple]:
    seeds=pilot_seeds if pilot else tuple(config["holdout_seeds"])
    if pilot and (not seeds or len(set(seeds))!=len(seeds)
                  or not set(seeds)<=set(config["pilot_only_seeds"])):
        raise ValueError("Pilot must use disjoint reserved development seeds only")
    cells=config["study_cells"][:2] if pilot else config["study_cells"]
    blocks=[(s,cell["scenario"],cell["K"]) for s in seeds for cell in cells]
    random.Random(config["block_shuffle_seed"]).shuffle(blocks)
    return [(s,n,k,p) for s,n,k in blocks for p in policy_order(config,s,n,k)]


def study(protocol:Path, out:Path, *, pilot:bool, pilot_seeds:tuple[int,...],
          git_revision:str)->dict:
    cfg=load_protocol(protocol)
    if not pilot and (len(git_revision)<8 or git_revision=="UNCOMMITTED"):
        raise ValueError("Fresh holdout must be pinned to a submitted commit")
    out=out.resolve()
    ordered=plan(cfg,pilot=pilot,pilot_seeds=pilot_seeds)
    if not pilot and len(ordered)!=cfg["experimental_runs"]:
        raise ValueError("Holdout run count diverges from freeze")
    out.mkdir(parents=True,exist_ok=False)
    (out/"fixtures").mkdir()
    (out/"runs").mkdir()
    here=Path(__file__).resolve().parent
    man={"status":"INCOMPLETE_NOT_SCIENTIFIC_EVIDENCE","complete":False,
         "protocol_id":PROTOCOL_ID,"protocol_sha256":PROTOCOL_SHA256,
         "study_phase":"RESERVED_DEVELOPMENT_PILOT" if pilot else "FROZEN_FIRST_HELDOUT_SYNTHETIC",
         "provenance":"SYNTHETIC_NOT_FIELD_CALIBRATED_ADDITIONAL_BUFFER_NOT_NOVELTY",
         "field_calibrated":False,"novelty_verified":False,
         "transport":"inproc" if pilot else "mqtt",
         "head_source_revision":git_revision,
         "started_utc":datetime.now(timezone.utc).isoformat(),
         "host":{"platform":platform.platform(),"python":platform.python_version(),
                 "sqlite":sqlite3.sqlite_version,"logical_cpu_count":os.cpu_count()},
         "seeds":list(pilot_seeds if pilot else cfg["holdout_seeds"]),
         "planned_trial_count":len(ordered),
         "planned_trial_cells":[{"seed":s,"scenario":n,"K":k,"policy":p}
                                for s,n,k,p in ordered],
         "calibration":None,"runs":[]}
    try:
        for seed,scenario in sorted({(s,n) for s,n,_,_ in ordered}):
            save_fixture(out/"fixtures"/f"s{seed}_{scenario}",seed=seed,
                         count=cfg["source_count"],urgent_count=cfg["urgent_count"],
                         **cfg["scenarios"][scenario])
        report,db=out/"lab_service_characterization.json",out/"lab_service_characterization.sqlite"
        command([sys.executable,str(here/"stage7_calibration_probe.py"),
                 "--seed","917","--repetitions","12",
                 "--iterations-per-unit",str(cfg["pbkdf2_iterations_per_work_unit"]),
                 "--output",str(report),"--sqlite-output",str(db)],60)
        ca=json.loads(command([sys.executable,str(here/"stage7_calibration_audit.py"),
                               "--report",str(report),"--sqlite",str(db)],20))
        if ca.get("field_calibrated") is not False or not ca["status"].startswith("PASS_"):
            raise RuntimeError("Lab host calibration failed independent audit")
        man["calibration"]={"report":report.name,"report_sha256":sha256(report),
                            "sqlite":db.name,"sqlite_sha256":sha256(db),
                            "audit_status":ca["status"]}
        for idx,(seed,scenario,K,policy) in enumerate(ordered,1):
            stem=f"s{seed}_{scenario}_K{K}_{policy}"
            fixture=out/"fixtures"/f"s{seed}_{scenario}"
            ledger,worker=out/"runs"/f"{stem}.jsonl",out/"runs"/f"{stem}.sqlite"
            spool=out/"runs"/f"{stem}_spool.sqlite"
            is_stage9=policy=="stage9_pushout_strict"
            script="stage9_urgent_pushout.py" if is_stage9 else "stage10_bounded_recovery.py"
            argv=[sys.executable,str(here/script),"--fixture-dir",str(fixture)]
            if not is_stage9:
                argv += ["--policy",policy,"--B",str(cfg["policy_capacity"][policy]),
                         "--spool-output",str(spool)]
                if not pilot:
                    argv += ["--evidence-phase","frozen_holdout"]
            argv += ["--transport","inproc" if pilot else "mqtt","--K",str(K),
                     "--iterations-per-unit",str(cfg["pbkdf2_iterations_per_work_unit"]),
                     "--urgent-deadline-ms",str(cfg["urgent_deadline_ms"]),
                     "--routine-tau-ms",str(cfg["routine_tau_ms"]),
                     "--output",str(ledger),"--sqlite-output",str(worker),
                     "--timeout-s",str(cfg["execution"]["per_trial_timeout_s"])]
            command(argv,cfg["execution"]["per_trial_timeout_s"]+20)
            audit_script="stage9_independent_audit.py" if is_stage9 else "stage10_independent_audit.py"
            audit_args=[sys.executable,str(here/audit_script),"--fixture-dir",str(fixture),
                        "--ledger",str(ledger),"--sqlite",str(worker)]
            if not is_stage9:
                audit_args += ["--spool",str(spool)]
            if not pilot:
                audit_args.append("--require-mqtt")
            audited=json.loads(command(audit_args,20))
            desired=("PASS_STAGE9_INDEPENDENT_PUSHOUT_QUEUE_AND_SQLITE_AUDIT" if is_stage9
                     else "PASS_STAGE10_INDEPENDENT_K_PLUS_B_SQLITE_QUEUE_AUDIT")
            if audited["status"]!=desired or audited["offered"]!=60:
                raise RuntimeError("Independent raw evidence audit failed")
            rows=[json.loads(x) for x in ledger.read_text().splitlines() if x.strip()]
            routine=[x for x in rows if x.get("type")=="offer" and
                     x["trusted_class"]=="ROUTINE"]
            C=sum(x["terminal"]=="COMPLETED" for x in routine)/len(routine)
            rejected=audited["rejected_full"] if is_stage9 else audited["rejected"]
            cancelled=audited["cancelled_pushout"] if is_stage9 else audited["cancelled"]
            fman=json.loads((fixture/"manifest.json").read_text())
            man["runs"].append({
                "execution_order":idx,"seed":seed,"scenario":scenario,"K":K,"policy":policy,
                "B":cfg["policy_capacity"][policy],
                "fixture_dir":f"fixtures/{fixture.name}",
                "ledger":f"runs/{ledger.name}","ledger_sha256":sha256(ledger),
                "sqlite":f"runs/{worker.name}","sqlite_sha256":sha256(worker),
                "spool":None if is_stage9 else f"runs/{spool.name}",
                "spool_sha256":None if is_stage9 else sha256(spool),
                "source_fixture_sha256":fman["offer_sha256"],
                "hidden_fixture_sha256":fman["hidden_work_sha256"],
                "offered":audited["offered"],
                "committed":audited["committed"] if is_stage9 else audited["completed"],
                "rejected":rejected,"cancelled":cancelled,
                "spool_inserted":0 if is_stage9 else audited["spool_inserted"],
                "U":audited["U"],"R":audited["R"],"C":C,
                "independent_audit_status":desired})
            print(f"INDEPENDENTLY AUDITED {idx}/{len(ordered)} {stem}",flush=True)
    finally:
        man["finished_utc"]=datetime.now(timezone.utc).isoformat()
        man["complete"]=len(man["runs"])==len(ordered)
        man["status"]=("COMPLETE_REQUIRES_BATCH_REAUDIT" if man["complete"]
                       else "INCOMPLETE_NOT_SCIENTIFIC_EVIDENCE")
        with (out/"study.json").open("x",encoding="utf-8") as f:
            json.dump(man,f,sort_keys=True,indent=2)
            f.write("\n")
    if not man["complete"]:
        raise RuntimeError("Partial Stage10 run cannot count as heldout evidence")
    return man


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--protocol",type=Path,default=Path(__file__).with_name("stage10_frozen_protocol.json"))
    p.add_argument("--mode",required=True,choices=["pilot","holdout"])
    p.add_argument("--pilot-seeds",nargs="+",type=int,default=[9008])
    p.add_argument("--git-revision",default="UNCOMMITTED")
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args()
    result=study(a.protocol,a.output_dir,pilot=a.mode=="pilot",
                 pilot_seeds=tuple(a.pilot_seeds),git_revision=a.git_revision)
    print(json.dumps({"status":result["status"],"completed":len(result["runs"])},sort_keys=True))


if __name__=="__main__":
    main()
