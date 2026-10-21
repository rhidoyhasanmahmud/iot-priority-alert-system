# Reproduction and evidence audit

The software workflow is implemented. Primary research results and publication readiness remain unestablished. A passing engineering audit does not establish a novel contribution, a successful hypothesis or conference acceptance.

## Audit the evidence shipped in Git

From a clean checkout with Python 3.11+:

```bash
python -m unittest discover -s tests -v
python -m iot_alerts.evidence_audit --output results/evidence-audit
```

The audit uses the standard library; no broker, hardware, plotting package or network service is required. It reruns the 90 historical pilot simulations in a temporary directory, compares run metrics and aggregate CSVs byte for byte, compares the decompressed raw example and recomputes the two paired bootstrap intervals. It restores the checked-in live smoke archive into another temporary directory, verifies its inventory and raw-record consistency using the live verifier, and compares its public summary with the verified raw results. Temporary reproduced files are removed afterward.

`audit.json` records each check, errors, input SHA-256 values, Python version and the current audit source hash; `report.md` gives a short review. Any failed check makes the CLI exit nonzero. Output directories must be new. Inputs are preserved. The audit only inspects checked-in evidence: it does not discover or certify studies elsewhere in `results/`. Its pending-work list describes the repository evidence scope, not whether someone has run an unpublished study externally.

Hashes detect changes relative to manifests. They do not authenticate an independent replication or prove scientific validity. Pilot reproduction exercises the current code; archived live verification checks recorded observations without rerunning their original wall-clock timing. Exact live timing and per-policy counts can change on another host.

## Claims and evidence

| Statement | Current evidence | Boundary / required next evidence |
| --- | --- | --- |
| Baseline policies expose an urgency/routine tradeoff | Reproducible synthetic pilot, ten paired seeds | Finite unbounded baseline model; no candidate benefit established |
| Live queue, deduplication and reconnect checks work in the recorded run | Archived eight-policy local smoke, overload and restart/resubscribe raw logs | Engineering observation; no persistent exactly-once or crash-recovery guarantee |
| Candidate improves routine waiting within the urgent-failure budget | Registered primary protocol and implemented analysis | Untested in the full primary matrix; retain unfavorable and infeasible outcomes |
| Adaptation and guard each contribute | Implemented ablation and sensitivity workflow | Full held-out component and fresh-seed sensitivity results still needed |
| Candidate has practical live performance value | Controlled validation harness | Full 160-run live profile, drift disclosure and model-to-live limitations needed |
| Contribution differs sufficiently from closest published methods | Related-work review and identified gaps | Full-text comparison, especially reference R8, and justified comparable baseline needed |
| System detects cyberattacks or provides production security | No security-detection evaluation | Outside current demonstrated scope; priority metadata is not attack detection |

The [design review](design-review.md) and [related work](../related-work.md) define the contribution boundaries. Exploratory unadjusted scenario intervals must not become simultaneous or universal improvement claims.

## Execute the research in order

1. Review the closest work, research question and protocol before collecting primary results. Resolve comparator and novelty gaps. A material protocol change needs a newly versioned registration, not edits justified by held-out outcomes.
2. Use a clean reviewed commit and record Python, dependencies, machine/OS, CPU and memory. First execute the complete smoke workflow in the [runner](experiment-runner.md), [analysis](statistical-analysis.md) and [robustness](robustness.md) guides.
3. Register the primary study, tune and freeze selection, then evaluate and verify. The primary simulation commands process 192 million alert instances across 7,680 tuning and 11,520 evaluation runs; raw outputs can be large. Estimate runtime/storage using smoke measurements. If tuning is infeasible, retain and report it; do not consult held-out results to change parameters.
4. Generate paired analysis and ablation from verified held-out outputs. Register and run fresh-seed sensitivity (7,200 additional runs), then analyze it. Preserve all scenarios, missing metrics, loss and failure results alongside conditional waiting metrics.
5. Run the [live validation](../live-validation.md) `validation` profile (160 workload runs plus functional checks). It uses development defaults rather than the research-tuned settings; report that distinction. Any future tuned live comparison needs an explicitly registered configuration. Record broker versions, host, load, publisher drift and the receipt-to-completion timing boundary.
6. Preserve each complete directory, source snapshot, plan, frozen selection, raw traces, metrics, inventories, analysis and figures. Keep sensitivity and parent directories in their recorded relative layout. Keep interrupted runs as incomplete and restart in a new directory; current runners do not resume.

Use the linked guides for exact commands and optional pinned plotting/broker dependencies. Never run the full matrix implicitly as part of this audit. Read-only analysis may inspect older archived source; experiment execution requires its registered source/Python identity. Record an explicit commit and all dependency versions for the final evidence bundle. CI smoke artifacts expire and are not a durable substitute for that bundle.

## Prepare the paper after evaluation

Write the problem and contribution against the closest methods, specify queue/admission/deadline semantics, then describe the preregistered tuning/evaluation separation and paired-seed analysis. The results section should report effect sizes, uncertainty, loss and failure tradeoffs, ablation, sensitivity and live observations, including null or unfavorable findings. Discuss synthetic traffic, finite overload with drain, simplified service costs, conditional tail metrics, live timing drift, limited security scope and generalizability.

Before submission, verify every numerical claim against an exact table/run path and reviewed analysis version. Complete the closest-method comparison, select an appropriate venue based on the resulting contribution and obtain coauthor review. Make source, reproduction instructions and a durable evidence bundle available under agreed licensing and sharing terms. No publication outcome is implied by completing this implementation plan.
