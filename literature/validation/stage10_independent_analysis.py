#!/usr/bin/env python3
"""Independent Stage10 frozen raw evidence and paired-seed statistical analysis.

Does not import the Stage10 emitter or Stage10 frozen runner. Independently
reopens every fixture/ledger/main-and-spool SQLite database. Fail closed even
if the candidate's registered gate is negative or inconclusive.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import statistics

from stage5k2_independent_audit import audit as audit_fixture, audit_pair
from stage7_calibration_audit import audit as audit_calibration
from stage9_independent_audit import audit_run as audit_stage9
from stage10_independent_audit import audit_run as audit_stage10


FROZEN_SHA256="c66ba9824418ba20fc08be4bcfbb71bc72bff5e04f5b03d38794ccd297fa1429"
PROTOCOL_ID="STI-2026-STAGE10-BOUNDED-ROUTINE-RECOVERY-HELDOUT-V1"
POLICIES=("fifo_deferred","strict_deferred","stage9_pushout_strict","pushout_deferred")


def check(ok, reason):
    if not ok:
        raise ValueError("STAGE10 FROZEN INDEPENDENT AUDIT FAILURE: "+reason)


def sha256(path):
    h=hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda:stream.read(65536),b""):
            h.update(chunk)
    return h.hexdigest()


def safe_file(root:Path, rel:str)->Path:
    check(type(rel) is str and bool(rel),"Missing relative artifact name")
    p=(root/rel).resolve()
    check(p.is_relative_to(root.resolve()) and p.is_file(),"Missing/unsafe artifact path")
    return p


def quantile(xs:list[float],p:float)->float:
    ys=sorted(xs)
    check(len(ys)>0,"Quantile on empty sample")
    q=(len(ys)-1)*p
    lo,hi=math.floor(q),math.ceil(q)
    return ys[lo]+(q-lo)*(ys[hi]-ys[lo])


def paired_ci(values:list[float],*,seed:int,resamples:int)->dict:
    check(len(values)>=2,"Source-seed bootstrap needs at least two seeds")
    rng=random.Random(seed)
    n=len(values)
    bs=[sum(values[rng.randrange(n)] for _ in range(n))/n for _ in range(resamples)]
    return {"paired_source_seeds":n,"mean":statistics.mean(values),
            "ci95_low":quantile(bs,.025),"ci95_high":quantile(bs,.975),
            "unit":"ABSOLUTE_FRACTION_DIFFERENCE",
            "method":"PAIRED_SOURCE_SEED_PERCENTILE_BOOTSTRAP"}


def independent_policy_order(c:dict,s:int,n:str,K:int)->list[str]:
    material=f"stage10|{c['policy_within_block_shuffle_seed']}|{s}|{n}|{K}"
    ps=list(POLICIES)
    random.Random(int.from_bytes(hashlib.sha256(material.encode()).digest()[:8],"big")).shuffle(ps)
    return ps


def independent_plan(c:dict,seeds:list[int],pilot:bool)->list[tuple]:
    cells=c["study_cells"][:2] if pilot else c["study_cells"]
    blocks=[(s,x["scenario"],x["K"]) for s in seeds for x in cells]
    random.Random(c["block_shuffle_seed"]).shuffle(blocks)
    return [(s,n,K,p) for s,n,K in blocks for p in independent_policy_order(c,s,n,K)]


def audit_study(root:Path,protocol:Path,*,pilot:bool)->dict:
    root=root.resolve()
    check(sha256(protocol)==FROZEN_SHA256,"Protocol hash changed after freeze")
    c=json.loads(protocol.read_text())
    check(c["protocol_id"]==PROTOCOL_ID and c["policies"]==list(POLICIES)
          and c["field_calibrated"] is False and c["candidate_novelty_verified"] is False,
          "Different study identity or scientific scope")
    raw=json.loads(safe_file(root,"study.json").read_text())
    check(raw["protocol_id"]==PROTOCOL_ID and raw["protocol_sha256"]==FROZEN_SHA256
          and raw["complete"] is True and raw["status"]=="COMPLETE_REQUIRES_BATCH_REAUDIT"
          and raw["field_calibrated"] is False and raw["novelty_verified"] is False
          and raw["provenance"]=="SYNTHETIC_NOT_FIELD_CALIBRATED_ADDITIONAL_BUFFER_NOT_NOVELTY",
          "Incomplete or substituted study")
    check(raw["study_phase"] == ("RESERVED_DEVELOPMENT_PILOT" if pilot else
                               "FROZEN_FIRST_HELDOUT_SYNTHETIC")
          and raw["transport"] == ("inproc" if pilot else "mqtt"),
          "Unexpected transport or study-phase label")
    seeds=raw["seeds"]
    check(type(seeds) is list and len(seeds)==len(set(seeds)),"Duplicate source seeds")
    if pilot:
        check(bool(seeds) and set(seeds)<=set(c["pilot_only_seeds"]),"Pilot used holdout seed")
    else:
        check(seeds==c["holdout_seeds"] and len(seeds)==30
              and len(raw["head_source_revision"])>=8
              and raw["head_source_revision"]!="UNCOMMITTED",
              "Missing heldout seeds or pinned source identity")
    planned=independent_plan(c,seeds,pilot)
    check([(x["seed"],x["scenario"],x["K"],x["policy"]) for x in raw["planned_trial_cells"]]
          == planned and raw["planned_trial_count"]==len(planned)
          and len(raw["runs"])==len(planned)
          and len(planned)==len(seeds)*(8 if pilot else 20),
          "Planned versus executed trial set differs")
    cal=raw["calibration"]
    check(cal is not None and cal["audit_status"].startswith("PASS_"),
          "Missing host characterization")
    cp,cd=safe_file(root,cal["report"]),safe_file(root,cal["sqlite"])
    check(sha256(cp)==cal["report_sha256"] and sha256(cd)==cal["sqlite_sha256"]
          and audit_calibration(cp,cd)["field_calibrated"] is False,
          "Characterization file or independent analysis changed")
    fixture_paths={}
    for seed in seeds:
        for name in {n for _,n,_,_ in planned}:
            fp=root/"fixtures"/f"s{seed}_{name}"
            f=audit_fixture(fp)
            spec=c["scenarios"][name]
            check(f["count"]==60 and f["urgent_count"]==15
                  and f["shape"]==spec["shape"]
                  and f["work_dispersion"]==spec["dispersion"]
                  and f["planned_horizon_ns"]==spec["horizon_ns"],
                  "Wrong or mutated source fixture")
            fixture_paths[(seed,name)]=fp
        if not pilot:
            base=fixture_paths[(seed,"smooth")]
            for name,rel in (("burst","burst_shape"),("overload","intensity"),
                             ("variable","work_dispersion")):
                audit_pair(base,fixture_paths[(seed,name)],rel)
    blocks={}
    for idx,run in enumerate(raw["runs"],1):
        s,n,K,p=planned[idx-1]
        check((run["seed"],run["scenario"],run["K"],run["policy"])==(s,n,K,p)
              and run["execution_order"]==idx
              and run["fixture_dir"]==f"fixtures/s{s}_{n}"
              and run["B"]==c["policy_capacity"][p],
              "Missing, reordered, or relabelled run")
        lp,worker=safe_file(root,run["ledger"]),safe_file(root,run["sqlite"])
        check(sha256(lp)==run["ledger_sha256"] and
              sha256(worker)==run["sqlite_sha256"],"Raw ledger/SQLite changed")
        rows=[json.loads(x) for x in lp.read_text().splitlines() if x.strip()]
        man=next(x for x in rows if x["type"]=="manifest")
        check(man["K"]==K and
              man["synthetic_iterations_per_work_unit"]==c["pbkdf2_iterations_per_work_unit"]
              and man["urgent_deadline_offset_ns"]==int(c["urgent_deadline_ms"]*1e6)
              and man["routine_tau_ns"]==int(c["routine_tau_ms"]*1e6),
              "Frozen timing, work, or capacity was changed")
        stage9=p=="stage9_pushout_strict"
        if stage9:
            check(run["spool"] is None and run["spool_sha256"] is None
                  and man["policy_id"]=="urgent_pushout_strict", "Wrong B0 comparator")
            audit=audit_stage9(rows,worker,fixture_paths[(s,n)],require_mqtt=not pilot)
            status="PASS_STAGE9_INDEPENDENT_PUSHOUT_QUEUE_AND_SQLITE_AUDIT"
            completed,rejected,cancelled=audit["committed"],audit["rejected_full"],audit["cancelled_pushout"]
            spool_count=0
        else:
            check(man["policy_id"]==p and man["B"]==run["B"]==8,
                  "B8 comparator capacity changed")
            check(man.get("evidence_phase")==
                  ("development" if pilot else "frozen_holdout") and
                  man["study_status"]==(
                    "STAGE10_TUNING_ONLY_NO_INFERENCE" if pilot else
                    "STAGE10_FROZEN_HELDOUT_SYNTHETIC_NOT_FIELD_CALIBRATED"),
                  "Heldout/development raw record phase was substituted")
            spool=safe_file(root,run["spool"])
            check(sha256(spool)==run["spool_sha256"],"Spool SQLite modified")
            audit=audit_stage10(rows,worker,spool,fixture_paths[(s,n)],require_mqtt=not pilot)
            status="PASS_STAGE10_INDEPENDENT_K_PLUS_B_SQLITE_QUEUE_AUDIT"
            completed,rejected,cancelled=audit["completed"],audit["rejected"],audit["cancelled"]
            spool_count=audit["spool_inserted"]
        offers=[x for x in rows if x.get("type")=="offer"]
        routine=[x for x in offers if x["trusted_class"]=="ROUTINE"]
        C=sum(x["terminal"]=="COMPLETED" for x in routine)/len(routine)
        fixture_manifest=json.loads((fixture_paths[(s,n)]/"manifest.json").read_text())
        check(audit["status"]==run["independent_audit_status"]==status
              and run["source_fixture_sha256"]==fixture_manifest["offer_sha256"]
              and run["hidden_fixture_sha256"]==fixture_manifest["hidden_work_sha256"]
              and run["offered"]==len(offers)==audit["offered"]==60
              and run["committed"]==completed and run["rejected"]==rejected
              and run["cancelled"]==cancelled and run["spool_inserted"]==spool_count
              and run["U"]==audit["U"] and run["R"]==audit["R"] and run["C"]==C,
              "Frozen run summary fails independent reconstruction")
        ordering={x["event_id"]:i for i,x in enumerate(json.loads(x)
                  for x in (fixture_paths[(s,n)]/"offers.jsonl").read_text().splitlines())}
        observed=[ordering[x["event_id"]] for x in offers]
        blocks.setdefault((s,n,K),{})[p]={
            "U":audit["U"],"R":audit["R"],"C":C,
            "rejected":rejected,"cancelled":cancelled,"completed":completed,
            "spool_inserted":spool_count,
            "urgent_rejected":sum(x["trusted_class"]=="URGENT" and x["terminal"]=="REJECTED"
                                  for x in offers),
            "routine_rejected":sum(x["trusted_class"]=="ROUTINE" and x["terminal"]=="REJECTED"
                                   for x in offers),
            "routine_cancelled":sum(x["trusted_class"]=="ROUTINE" and x["terminal"]=="CANCELLED"
                                    for x in offers),
            "urgent_late_completed":sum(x["trusted_class"]=="URGENT" and
                                         x["terminal"]=="COMPLETED" and
                                         x["complete_ns"]>x["urgent_deadline_ns"] for x in offers),
            "offer_span_ms":(offers[-1]["offer_ns"]-offers[0]["offer_ns"])/1e6,
            "source_order_inversions":sum(observed[i]>observed[j]
                                          for i in range(len(observed))
                                          for j in range(i+1,len(observed)))}
    check(len(blocks)==len(seeds)*(2 if pilot else 5)
          and all(set(v)==set(POLICIES) for v in blocks.values()),
          "Any missing policy/paired source cell is fatal")
    result={"status":"PASS_PILOT_NO_INFERENCE" if pilot else
                     "PASS_STAGE10_FROZEN_SYNTHETIC_HELDOUT_FULL_INDEPENDENT_AUDIT",
            "protocol_id":PROTOCOL_ID,"protocol_sha256":FROZEN_SHA256,
            "field_calibrated":False,"algorithm_novelty_verified":False,
            "source_seeds":len(seeds),"raw_runs_reaudited":len(raw["runs"]),
            "four_policy_matched_blocks":len(blocks),
            "scope":"ARTIFICIAL_ONE_WORKER_LOCAL_MQTT_SQLITE_B8_NOT_REAL_IOT_SLA",
            "capacity_tradeoff_disclosed":True}
    if pilot:
        result["warning"]="DEVELOPMENT_ONLY_NOT_A_HOLDOUT_RESULT"
        return result
    results={}
    for idx,cell in enumerate(c["study_cells"]):
        n,K=cell["scenario"],cell["K"]
        observations=[blocks[(s,n,K)] for s in seeds]
        comps={
          "U_fifo_B8_minus_candidate_B8":[x["fifo_deferred"]["U"]-x["pushout_deferred"]["U"]
                                           for x in observations],
          "U_strict_B8_minus_candidate_B8":[x["strict_deferred"]["U"]-x["pushout_deferred"]["U"]
                                             for x in observations],
          "C_candidate_B8_minus_stage9_B0":[x["pushout_deferred"]["C"]-x["stage9_pushout_strict"]["C"]
                                            for x in observations],
          "U_candidate_B8_minus_stage9_B0":[x["pushout_deferred"]["U"]-x["stage9_pushout_strict"]["U"]
                                            for x in observations],
          "C_candidate_B8_minus_strict_B8":[x["pushout_deferred"]["C"]-x["strict_deferred"]["C"]
                                             for x in observations],
          "C_candidate_B8_minus_fifo_B8":[x["pushout_deferred"]["C"]-x["fifo_deferred"]["C"]
                                           for x in observations],
          "R_candidate_B8_minus_stage9_B0":[x["pushout_deferred"]["R"]-x["stage9_pushout_strict"]["R"]
                                            for x in observations],
        }
        results[f"{n}_K{K}"]={
            "role":cell["role"],
            "policies":{p:{
                **{f"mean_{m}":statistics.mean(x[p][m] for x in observations)
                   for m in ("U","R","C","rejected","cancelled","completed",
                             "spool_inserted","urgent_rejected","routine_rejected",
                             "routine_cancelled","urgent_late_completed")},
                "median_observed_offer_span_ms":statistics.median(x[p]["offer_span_ms"]
                                                                   for x in observations),
                "source_order_inversions_total":sum(x[p]["source_order_inversions"]
                                                     for x in observations)}
                        for p in POLICIES},
            "paired_effects":{name:paired_ci(xs,seed=c["bootstrap_seed"]+idx*100+j,
                                              resamples=c["bootstrap_resamples"])
                              for j,(name,xs) in enumerate(comps.items())}}
    result["cells"]=results
    fx=results["burst_K3"]["paired_effects"]
    targets=c["primary_decision"]
    gates={
      "equal_B8_FIFO_urgent_U_improvement_gt5pp":fx["U_fifo_B8_minus_candidate_B8"]["ci95_low"]>
                                                targets["U_improvement_min_absolute"],
      "equal_B8_Strict_urgent_U_improvement_gt5pp":fx["U_strict_B8_minus_candidate_B8"]["ci95_low"]>
                                                  targets["U_improvement_min_absolute"],
      "B8_vs_B0_Stage9_routine_C_rescue_gt5pp":fx["C_candidate_B8_minus_stage9_B0"]["ci95_low"]>
                                               targets["C_vs_stage9_extra_buffer_improvement_min_absolute"],
      "B8_vs_B0_Stage9_urgent_U_noninferior_10pp":fx["U_candidate_B8_minus_stage9_B0"]["ci95_high"]<
                                                  targets["U_noninferiority_margin_vs_stage9_absolute"],
    }
    result["predeclared_primary_intersection_gate"]={
        "primary_cell":{"scenario":"burst","K":3},
        "component_decisions":gates,
        "supported_under_artificial_model":all(gates.values()),
        "always_report_equal_B8_routine_C_disadvantage":fx["C_candidate_B8_minus_strict_B8"],
        "B8_to_B0_not_same_resource_superiority":True,
        "no_auto_authorization_to_write_or_submit_manuscript":True,
        "negative_or_inconclusive_result_preserved":True}
    result["statistical_warning"]=(
        "Source-seed-paired percentile bootstrap uses 30 independent synthetic sources; "
        "per-event observations are correlated. Study is a single artificial worker, "
        "not a measured IoT SLA. Extra B8 storage vs B0 is not a scheduling-only effect; "
        "mean C is eventual post-source drain, not deadline completion. "
        "No crash-restart evidence, field calibration, algorithm novelty or publication claim. "
        "Secondary endpoints are descriptive and multiplicity-unadjusted. "
        "Artificial thresholds and 10pp margin are investigator-chosen without domain approval.")
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--study-dir",type=Path,required=True)
    p.add_argument("--protocol",type=Path,
                   default=Path(__file__).with_name("stage10_frozen_protocol.json"))
    p.add_argument("--pilot",action="store_true")
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    result=audit_study(a.study_dir,a.protocol,pilot=a.pilot)
    if a.output:
        with a.output.open("x",encoding="utf-8") as f:
            json.dump(result,f,sort_keys=True,indent=2)
            f.write("\n")
    print(json.dumps(result,sort_keys=True,indent=2))


if __name__=="__main__":
    main()
