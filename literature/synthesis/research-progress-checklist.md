# Conference research progress — step-by-step checklist

**As of:** 16 November 2026 · **Track:** RQ v1.0 (*Routine-Service Protection Under Bursty IoT Alerts*) · **Rule:** check a box only when its *evidence link or decision record* exists. “Paper read” and “paper found” are different events. Do not change the main RQ merely because a competing paper appears; make a reasoned review decision.

## Live dashboard

| Stage | Status | Work product | Exit / blockers |
| --- | --- | --- | --- |
| 1. Topic, review scope and research question | **Completed for current iteration** | [RQ v1.0](research-questions.md) | Domain-derived numeric service budgets still needed |
| 2. Core literature review | **19 completed retained notes** | [Register](../README.md), [matrix](comparison.csv), [synthesis](findings.md) | More papers only when a specific gap requires them |
| 3. Adversarial novelty screening | **Completed as a focused audit; NOT novelty-certified** | [Independent audit](novelty-assessment.md), [search log](../search-log.csv) | N01 directly challenges the broad claim |
| 4. Closest theory and database coverage | **Stage 4A complete; Stage 4B targeted analytical decision complete; FINAL sign-off pending** | [Model-equivalence crosswalk](closest-paper-model-crosswalk.md), [Stage 4B novelty decision](novelty-decision-stage4b.md) | New N09 threat; N01/N03/N06/N09 authorized full text, independent database/citation chasing and supervisor approval |
| 5. Application and measurable requirements | **5A–5H lab pipeline verified; 5I real-workload evidence register + NOT_READY gate drafted; OPERATIONAL VALIDITY OPEN** | [5F verified MQTT](mqtt-measurement-pilot-stage5f.md), [5G service probe](application-handler-calibration-stage5g.md), [5H joint audit](joint-mqtt-sqlite-stage5h.md), [5I evidence gate](workload-evidence-calibration-stage5i.md) | Actual device/handler workload, owner-backed deadlines and resource capacity, professor sign-off |
| 6. Evaluation pre-registration | **Pending** | Signed protocol | Faithful baselines, acceptance rules, workloads and statistics |
| 7. Implementation and result validation | **Not started in this literature-only main branch** | Reproducible code/results | Invariants, independent traces, held-out results |
| 8. Contribution, manuscript and review | **Not started** | Supervisor go/no-go + submission draft | Confirm novelty and venue fit |

**Current gate:** Stage **4B's targeted analysis is done with an explicit REVISE/NARROW verdict, but definitive novelty clearance remains open**. Stage 5 application provenance can be prepared while authorized full-text/database checks and supervisor approval continue; do **not** claim algorithm novelty or commit to a new scheduler design. The existing implementation is archived; this tracker does not claim it has been reproduced or benchmarked.

## Step 1 — Research questions and scope

- [x] Select one conference-level main question and three linked sub-questions.
- [x] Define urgent deadline failure on **offered** jobs and routine timely start on **offered** jobs.
- [x] Freeze the initial single-worker, non-preemptive, finite-buffer experimental boundary.
- [x] Mark admitted-only accounting, classification error, outage control and multi-worker routing as outside current primary comparisons.
- [ ] Confirm one real IoT application and its operational timing semantics.
- [ ] Justify numerical epsilon (urgent deadline-failure budget), tau (routine waiting limit), gamma (routine-access target) and waiting capacity K.

**Checklist outcome:** *Question and formal direction set; application requirements not yet validated.* Evidence: [research-questions.md](research-questions.md).

## Step 2 — Literature foundation

- [x] Retain 19 closely related completed review notes.
- [x] Maintain source register, comparison matrix and cross-paper synthesis.
- [x] Record included/excluded material in revision history.
- [x] Keep newly discovered external leads separate from completed full reviews.
- [ ] Promote any new lead into the retained set **only after** reading and recording all requisite methods/results/limitations.

**Checklist outcome:** *Core review foundation exists, but cannot be described as exhaustive or full-field novelty proof.* Evidence: [review register](../README.md), [comparison](comparison.csv), [synthesis](findings.md).

## Step 3 — Independent adversarial novelty audit

- [x] Test broad “priority + fairness + deadline” claims against established work.
- [x] Verify N01 (Gonthier et al., ACM ICPP 2025), a near-direct urgent-deadline/routine-flow scheduling comparator.
- [x] Verify DRR delay bounds and real-time job mapping (Tabatabaee & Le Boudec, IEEE RTAS 2021).
- [x] Verify existing estimation-error/fairness work (Dell'Amico et al., IEEE TC 2016).
- [x] Verify single-server online multi-class deadlines/admission (Hajek & Seri 2005; Goldman et al. 2000).
- [x] Write RQ-by-RQ risk judgments, falsification tests, and an explicit conditional verdict.
- [x] Record search provenance and the level at which each lead was actually read.
- [ ] **Do not** check “novelty established” at this stage.

**Checklist outcome:** *Focused audit done. Verdict: promising testable framing, severe overlap, originality NOT established.* Evidence: [novelty-assessment.md](novelty-assessment.md).

## Step 4 — Closest-paper/model equivalence (4B analytic audit done; SIGN-OFF OPEN)

For **N01 Gonthier et al.**:
- [ ] Obtain and read the complete publisher/authors' paper, including the algorithms and experiments.
- [x] Map their objective “urgent deadline completion + maximum routine flow” to ours “urgent offered failures + routine starts within tau,” including a mathematical non-equivalence example.
- [x] Map **verified** N01 processor count, service-information model and both output metrics; record finite-buffer/rejection as **unverified** rather than asserting absence.
- [ ] Verify finite queue/admission assumptions and rejected-job treatment in the complete N01 paper.
- [ ] Reproduce or fairly adapt their EDF+FIFO/Greedy-Slack-style baseline under matching information.
- [x] Write a provisional **substantially overlapping but not established equivalent** conclusion, with evidence boundaries.
- [ ] Sign off final equivalence/subsumption conclusion after complete authorized original-paper reading.

For **N02–N06**:
- [x] Read N02 original RTAS service-curve/arrival assumptions and real-time-job mapping.
- [ ] Derive and validate applicability of the bound to finite-K waiting and offered-population losses.
- [x] Inspect N05 author-hosted complete primary paper's model and Dlex algorithm, not claim proof replication.
- [ ] Obtain N03 full text and complete N05 proof/variable-size applicability review.
- [ ] Obtain complete N06 online hard-deadline admission analysis.
- [x] Keep N04 as a documented boundary/limitation; do not claim estimator-error novelty.
- [x] Carry out additional targeted public publisher/web searches and retain query provenance **without** claiming exhaustive database coverage.
- [x] Verify N07 finite-input-buffer optimization, N08 non-preemptive mixed-criticality scheduling, N09 finite-buffer deadline losses and N10 multi-priority waiting cancellations at their stated reading levels.
- [x] Prove the conditional ex-post routine-start-to-completion-deadline identity, distinguishing unknown pre-service sizes from online-available deadlines.
- [x] Record elementary finite-K admission and non-preemptive blocking bounds as sanity checks, **not original theorems**.
- [x] Produce a precise **REVISE/NARROW, not novelty-cleared** analytic decision memo and falsification criteria.
- [ ] Conduct reproducible independent database searches (e.g., Scopus/IEEE/ACM) and citation chasing; log dates, strings, result counts, exclusions and full-text limits.
- [ ] Present a 1–2 page novelty-go/no-go memo to the supervisor, with a precise **not-yet-published substantive claim** or a decision to reframe.

**Checklist outcome:** *Stage 4A model crosswalk COMPLETE; Stage 4B targeted mathematical/publisher audit and REVISE/NARROW memo COMPLETE; definitive 4B full-text/database/theorem/supervisor sign-off remains OPEN.* See [source-specific model crosswalk](closest-paper-model-crosswalk.md) and [Stage 4B decision memo](novelty-decision-stage4b.md). This is a research validity gate, not a coding task.

### Step 4B — Go/Revise/No-Go record and evidence gate

- [x] Explicitly reject broad novelty of priority+routine fairness, start thresholds, finite buffer dropping, and simple deadline/blocking capacity facts.
- [x] Separate equivalence of **per-job outcome metrics** from equivalence of **online scheduling objectives/algorithms**.
- [x] Keep RQ v1.0 unchanged pending professor decision; recommended contribution is conditional empirical operating-region analysis.
- [ ] Obtain complete authorized N01/N03/N06/N09 methods/theorems; make exact applicability notes.
- [ ] Complete separately accessible Scopus, IEEE Xplore and ACM DL searches with result counts and citation trails.
- [ ] Discuss [the Stage 4B decision](novelty-decision-stage4b.md) with supervisor; record dated Go / Revise / No-Go sign-off.

**Checklist outcome:** *Targeted academic-review decision DONE, novelty certified NOT DONE. Stage 5 evidence gathering can proceed; method novelty cannot be claimed.*

## Step 5 — Application and experimental targets

- [x] **Provisionally** specify MQTT gateway local offer, processing start and processing completion boundaries for the archived synthetic demonstrator. This is **not** a validated deployed-system boundary; see [Stage 5A](application-boundary-stage5a.md).
- [ ] Collect or justify a source for real arrival bursts, per-job service demand and class mix.
- [ ] Explain actual urgency/deadline requirements and use plausible non-sensitive traces.
- [ ] Predeclare epsilon, tau, gamma, K and sensitivity ranges before tuning.
- [ ] Document offered job count, offered **work** and queue occupancy; avoid hidden upstream rate-limiting.

**Checklist outcome:** *Application boundary has a documented fictional candidate; Stage 5F broker transport, Stage 5G mock SQLite handler and Stage 5H combined in-process SQLite smoke PASS, but field/service realism and numerically approved operating requirements remain PENDING. Historic K=1000, D=100/500/2000 ms, 10 ms synthetic handler and a 1pp relative tolerance remain archived only, **not validated absolute targets**.* Evidence: [Stage 5A](application-boundary-stage5a.md), [Stage 5F](mqtt-measurement-pilot-stage5f.md), [Stage 5G](application-handler-calibration-stage5g.md), [Stage 5H](joint-mqtt-sqlite-stage5h.md).

### Stage 5A — Application boundary and provenance (provisional design complete)

- [x] Recover the archive's MQTT security-event enrichment demonstrator with exact source link.
- [x] Map tampering events to urgent and routine device-health events to routine; exclude former medium class from the primary two-class RQ.
- [x] Describe publisher, broker, callback, trusted classification/dedup, local offering, queue, single worker and completed effect separately.
- [x] Define event-level timing fields, disjoint lifecycle categories and a reproducibility/invariant checklist.
- [x] Build an evidence register that flags historic constants as **illustrative** and exposes absent operator/trace justification.
- [ ] Obtain real/calibrated service-time and workload evidence or approve a **synthetic-only** conference contribution.
- [ ] Validate actual deadlines, tau, gamma, absolute offered urgent epsilon and queue K before any held-out tests.
- [ ] Confirm provisional application model and Stage 4B research positioning with supervisor.

**Stage 5A checklist outcome:** *Provisional document complete; final requirements and metrics NOT frozen. Stage 6 implementation/evaluation remains blocked by evidence and sign-off.*

### Stage 5B — Source-level archived evidence audit (LIMITED CHECK COMPLETE)

- [x] Identify immutable archived source, actually committed pilot metrics and local MQTT smoke evidence.
- [x] Recompute archived pilot summary arithmetic: 90 rate/seed/policy groups, 270 class rows and 27/27 p95 aggregates agree.
- [x] Check live smoke count partitions: 8 runs × 40 planned offers = 320 policy-event records; 192 completed/128 dropped across those runs, **one seed**, not 320 independent real sensor events.
- [x] Compare current RQ with archive: old pilot had **unbounded** queue, 3 classes and constant 10 ms; archived MQTT worker used synthetic sleep, not measured enrichment.
- [x] Identify callback-entry versus post-validation **offer boundary mismatch**, old 1pp-relative versus new absolute epsilon, and generator-controlled burst/load confound.
- [x] Define nine source/metrics/protocol acceptance tests for new two-class, finite-K, offered-population traces.
- [ ] Run archival raw evidence verifier / decompress published raw bundles independently.
- [ ] Collect or execute a new two-class, finite-K **U and R(tau)** evidence packet with correctly reconciled offered arrivals.
- [ ] Validate service-time assumptions, epsilon/tau/gamma/K and synthetic-only scope with professor.

**Stage 5B checklist outcome:** *Existing engineering evidence FOUND and bounded arithmetic verified; current conference RQ empirical evidence NOT validated. See [source-by-source audit](archived-evidence-audit-stage5b.md).*

### Stage 5C — Two-class metric oracle and tiny synthetic smoke (ENGINEERING VALIDATION)

- [x] Implement **independent** no-dependency FIFO/strict-priority reference oracle for offered urgent U and routine R(tau) with K waiting plus one worker.
- [x] Define exact completion/admission/dispatch tie rule and class-neutral rejection; do not expose unstarted p in policy selection.
- [x] Test overflow, nonpreemptive blocking, equality at thresholds, zero offered-class denominators and same-time release: **9/9 golden cases PASS**.
- [x] Run **48/48** finite-K, variable synthetic-service engineering smoke cases on 6 matched trace seeds across two artificial shapes, capacities and policies.
- [x] Repeat script; byte-identical output under Python 3.12.14. Document the code checksum and all debug-only parameters.
- [x] Keep verifier isolated under `literature/validation/`, preserving archived full implementation and current RQ v1.0.
- [ ] Independently compare future real MQTT/application event logs with the oracle at post-validation offer boundary.
- [ ] Obtain or justify realistic arrival, service variability, epsilon/tau/gamma/K and professor approval; **no conference inference** from debug outputs.

**Stage 5C checklist outcome:** *Two-class metric/invariant oracle PASS in synthetic ticks. The simulation is deliberately not a real trace, not a new scheduler, not a registered primary experiment, and not novelty sign-off.* Evidence: [Stage 5C report](two-class-metric-validation-stage5c.md) and [executable oracle](../validation/stage5c_golden_oracle.py).

### Stage 5D — MQTT offer-boundary reconciliation and calibration contract (PLANNING / OFFLINE VALIDATOR ONLY)

- [x] Verify the archived callback-entry timestamp versus the new post-validation local-offer boundary directly in archived `live.py`/`mqtt_demo.py`.
- [x] Specify per-attempt MQTT callback/validation dispositions and one offered event ledger row per unique trusted local offer, including rejected offers.
- [x] Implement independent offline JSONL lifecycle auditor under `literature/validation/`, covering two-class offered U and R(tau), finite-K admission snapshots, monotonic ordering, duplicates and uncertain rate bounds.
- [x] Pass **1 fictional hand-checked ledger + 10 malformed-ledger negative tests + 1 incomplete-run case**; two byte-identical self-test runs and Python compile succeed.
- [x] Draft measured-laboratory versus synthetic-only options, source/worker/burst calibration evidence gates, and an unfilled D_u/epsilon/tau/gamma/K decision sheet.
- [x] Actually instrument a two-class finite-K MQTT gateway and capture independently auditable broker-backed callback-to-offer/local lifecycle ledgers: Stage 5F three-scenario CI PASS; **synthetic-only engineering scope**.
- [ ] Measure a declared real worker or explicitly approve synthetic-only limits; justify and freeze numeric service targets with supervisor before Stage 6.
- [ ] Finish independent full-theory/database/supervisor novelty sign-off (Stage 4B remains REVISE/NARROW).

**Stage 5D checklist outcome:** *Original Stage 5D boundary and offline audit tooling PASS on invented data; Stage 5F subsequently added and independently checked three broker-backed **synthetic laboratory** traces. Real application/source/service calibration and operational requirements remain NOT COMPLETE. See [Stage 5D evidence plan](workload-measurement-calibration-stage5d.md), [offline ledger auditor](../validation/stage5d_lifecycle_audit.py), and [Stage 5F lab evidence](mqtt-measurement-pilot-stage5f.md). No full research experiment yet.*

### Stage 5E — Two-class instrumented gateway pilot (IN-PROCESS ENGINEERING VALIDATION)
- [x] Implement and locally run a bounded FIFO gateway with one nonpreemptive CPU-work worker, post-validation/dedup offer boundary and full offered-event accounting.
- [x] Execute six (K=0/3 × base/burst/overload) in-process smoke cases and independently audit their complete lifecycle traces with Stage 5D.
- [x] Preserve a small auditable 36-offer in-process debug JSONL with checksum; warn that runtime-dependent figures vary even with the same source schedule.
- [x] Implement an optional Paho MQTT 2.x integration path, with QoS1 publisher readiness and capture-completeness guard; **no MQTT run was executed in the original Stage 5E environment**.
- [x] Run and independently audit actual broker-backed MQTT input in Stage 5F (3/3 local-broker CI scenarios); retain raw JSONL.\n- [ ] Replace synthetic CPU surrogate with a declared measured application handler or obtain synthetic-only supervisor approval.

**Stage 5E checklist outcome:** *Original in-process validation PASS; subsequent Stage 5F verified broker-backed lab transport/accounting (not the original Stage 5E run). Field/service realism still NOT established.* [Stage 5E report](mqtt-measurement-pilot-stage5e.md) · [gateway code](../validation/stage5e_gateway_pilot.py) · [debug sample](../validation/fixtures/stage5e_inproc_burst_k3_debug.jsonl).

### Stage 5F — Independent broker-backed MQTT audit gate (BROKER LAB SMOKE PASSED; RESEARCH STILL BLOCKED)
- [x] Make a main-targeted corrective PR containing the Stage 5E files previously merged only to a feature branch.
- [x] Implement a strict Stage 5F offline gate requiring source-ID/callback/offer reconciliation and rejecting incomplete or in-process-only traces mislabelled as MQTT.
- [x] Run the gate's local positive and negative self-checks; validate an isolated broker/Paho GitHub Actions workflow YAML syntax and test plan.
- [x] Observe [GitHub Actions run #43870469820](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/actions/runs/43870469820): Ubuntu/Python 3.12, Mosquitto 2.0.18/Paho 2.2, three broker-backed base/burst/overload captures, 3/3 independent ledgers PASS, 195 received/forwarded/ACK'd publishes, 3 subscriptions.
- [x] Retrieve and integrity-test the seven-file CI ZIP; re-run independent gate on all three raw JSONLs and version those synthetic-only ledgers in this PR with SHA-256 links in the Stage 5F report.
- [ ] Repeat realistic source/worker calibration, freeze D_u/epsilon/tau/gamma/K and complete Stage 4B professor novelty sign-off before Stage 6.

**Stage 5F checklist outcome:** *Broker-backed Mosquitto/Paho transport and lifecycle accounting lab smoke PASS (3/3, one CI run, 60 synthetic source IDs per shape); actual application handler, real source/service calibration, statistically replicated policy comparisons and Stage 4B novelty sign-off still OPEN. [Stage 5F evidence](mqtt-measurement-pilot-stage5f.md) · [offline gate](../validation/stage5f_mqtt_gate.py).*

### Stage 5G — Provisional SQLite alert handler and service-timing contract (LAB CHECKED; VALIDITY OPEN)
- [x] Specify exact fictional device lookup → fixed rule → SQLite INSERT/transaction commit worker, one nonpreemptive application handler per event; validation, MQTT, queue wait excluded.
- [x] Implement reference handler in Python standard library with WAL/FULL SQLite, and test duplicate/invalid/unknown device rollback and normal database close/reopen.
- [x] Implement independent service-ledger auditor checking input digest, rule/class, duration arithmetic and nonoverlapping single-worker spans; pass hand-checked positive and 6/6 malformed negative tests.
- [x] Execute three synthetic seeds × 120 commits (30 urgent, 90 routine per run), retain raw JSONLs and explicitly label unstable single-host timing observations as **not** field service-time calibration.
- [x] Verify [Stage 5G CI run #43873927699](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/actions/runs/43873927699): handler/error self-tests, 6/6 negative audit, two new 32-event traces and three retained 120-event fixture audits **PASS**. [Stage 5F MQTT regression #43873927339](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/actions/runs/43873927339) also PASS.
- [ ] Obtain supervisor/application owner approval of true work semantics and synthetic-only versus representative calibration scope.
- [ ] Measure real or representative handler plus source arrival/resource constraints under controlled hardware and load; predeclare D_u/epsilon/tau/gamma/K.
- [ ] Complete Stage 4B final novelty sign-off before Stage 6 full experiment.

**Stage 5G checklist outcome:** *Mock application handler, transaction and timing accounting PASS in a reproducible laboratory; real IoT source/handler service distribution, durability under failure, operational deadlines, confidence bounds and method novelty NOT ESTABLISHED. See [Stage 5G report](application-handler-calibration-stage5g.md), [emitter](../validation/stage5g_reference_handler.py), [independent auditor](../validation/stage5g_service_audit.py).*

### Stage 5H — Integrated MQTT + finite-K + SQLite commit contract (BROKER & INDEPENDENT SQLITE AUDIT PASS; FIELD VALIDITY OPEN)

- [x] Reuse the validated Stage 5E/F MQTT publisher and one-worker class-neutral FIFO finite-K gateway with Stage 5G fictional transaction handler.
- [x] Record receiver callback, post-validation offer, admission snapshot, service start, SQLite handler start, commit return and completion as separate local lifecycle fields.
- [x] Test six in-process joint load/capacity combinations, independent source/schedule/SQL rule and exact admitted-versus-persisted-row checks.
- [x] Commit an in-process golden diagnostic JSONL plus separate SHA-256-backed SQLite backup encoded as base64 for CI re-audit.
- [x] Reject 13 corrupted ledger cases, in-process-at-MQTT gate and real SQLite row tampering.
- [x] Add a GitHub Actions workflow for 3 real broker-backed MQTT→SQLite scenarios with separate actual SQLite backup verification.
- [x] Verify [Stage 5H MQTT+SQLite CI #43877369913](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/actions/runs/43877369913) SUCCESS and [Stage 5F regression #43877369587](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/actions/runs/43877369587) SUCCESS; download actual broker artifact and independently re-audit all three SQLite backups (base 58/60 committed, burst 49/60, overload 24/60; all 180 offered), with 49 class-neutral full-buffer rejects across 3 distinct synthetic shapes.
- [x] Archive broker-backed raw ledgers, per-shape independently matched SQLite backup snapshots and gate JSON with source/binary SHA-256; CI artifact #14230686972 is short-lived.
- [ ] Verify updated Stage 5H workflow re-audits all three permanently archived broker captures (after next PR CI completes).
- [ ] Obtain device/handler trace representativeness, production failure semantics and an owner-approved D_u/epsilon/tau/gamma/K; require supervisor Stage 4B novelty sign-off before Stage 6.

**Stage 5H checklist outcome:** *Joint in-process plus real Mosquitto MQTT/SQLite pipeline and independent persisted-row audit PASS; archived three broker datasets for future re-audit. Research external validity still pending. See [Stage 5H report](joint-mqtt-sqlite-stage5h.md). This is **not** a new scheduling algorithm or conference experiment.*

### Stage 5I — Evidence acquisition, calibration and research-readiness gate (CONTRACT COMPLETE; ACTUAL EVIDENCE MISSING)

- [x] Explicitly distinguish valid Stage 5H lab transaction/queue lifecycle from representative device arrivals, real handler service and owner-backed thresholds.
- [x] Define 16 required external evidence controls, including privacy/data rights, source sampling/censoring, broker losses, actual effect, resource and timing provenance, operator approval, Stage 4B and Stage 6.
- [x] Keep `D_u`, absolute offered urgent `epsilon`, offered routine `tau`/`gamma`, and waiting-capacity `K` **null** until independently documented operator decisions.
- [x] Implement independent Stage 5D/5H-ledger + SQLite-aware Stage 5I gate with strictly typed parameter proposals, exact required evidence references and no automatic Stage 6 approval.
- [x] Pass the self-test: one technically valid synthetic SQLite ledger stays `NOT_READY`, a forged `observed_deployment` label cannot upgrade it, seven malformed packets rejected and missing SQLite rejected.
- [x] Commit one archival Stage 5H `base` readiness report: technical PASS, **23 explicit blockers**, `NOT_READY`; no invented field values.
- [x] Add CI to re-audit all three stored real-broker Stage 5H synthetic captures and assert blocked research readiness.
- [x] Verify [Stage 5I evidence gate CI #43880322439](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/actions/runs/43880322439) SUCCESS: nine self-test safety cases and independent archived MQTT+SQLite `base`/`burst`/`overload` audits all produced technical PASS and correct research `NOT_READY` with 23 blockers each; saved [readiness artifact #14232810316](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/actions/runs/43880322439/artifacts/14232810316). [Stage 5F regression #43880322206](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/actions/runs/43880322206) also SUCCESS.
- [ ] Obtain real rights-approved source/handler/resource/failure/clock evidence; inspect content and document independent capture windows and any upstream censoring.
- [ ] Obtain operator/supervisor decision on `D_u`, `epsilon`, `tau`, `gamma`, `K`, choice of representative versus synthetic-only venue scope, and Stage 4B novelty sign-off.

**Stage 5I checklist outcome:** *A reproducible external-evidence packet protocol and fail-closed readiness validator exist, but no actual production calibration has occurred. See [Stage 5I report](workload-evidence-calibration-stage5i.md). Stage 6 remains blocked.*

## Step 6 — Design the evaluation before coding

- [ ] Freeze exact baseline descriptions and information availability (FIFO, priority, EDF+FIFO, aging, DRR, applicable N01 adaptation). If task sizes are unknown before service, label completion-accounted DRR-like variants as *adaptations*; never give them actual future durations.
- [ ] Separate count-based from measured consumed-work policies; prohibit uncharged oracle durations.
- [ ] Fix workload grid, matched offered traces, independent replication and held-out split.
- [ ] Fix primary success criteria and relevant effect size; define statistical intervals and negative-result reporting.
- [ ] Define invariants: conservation, finite waiting capacity, non-preemption, deadline bookkeeping and deterministic tie rules.
- [ ] Review the protocol with professor/research team.

**Checklist outcome:** *PENDING. No implementation recommendation is final until this step.*

## Step 7 — Execute, verify and analyze

- [ ] Implement simulation with reproducible seeds and a published config schema.
- [ ] Automate lifecycle/invariant tests and baseline parity tests.
- [ ] Run pilot experiments, then lock tuning before held-out comparisons.
- [ ] Report urgent U, routine R(tau), full rejections/censoring, workload mix, overhead and uncertainty.
- [ ] Examine counterexamples and regimes where conventional methods equal or beat the candidate.
- [ ] Make replication artifact and negative results available.

**Checklist outcome:** *NOT STARTED; previous implementation remains on the archive branch only.*

## Step 8 — Decide whether to submit

- [ ] Demonstrate the precise, defensible contribution **beyond** N01/N02/N05/N06.
- [ ] Confirm protocol-compliant, non-cherry-picked effects across independent traces.
- [ ] Obtain supervisor feedback on abstract, novelty statement and limitations.
- [ ] Select a suitable conference and verify its scope, ethics, length and reproducibility rules.
- [ ] Prepare manuscript, figures, references, artifact access and response-to-review plan.

**Checklist outcome:** *NOT STARTED. “Best Paper” is an aspiration, not a scientific result or prediction.*

## Update log

| Date | What changed | Next blocker |
| --- | --- | --- |
| 2026-11-16 | Captured RQ v1.0 current main-branch decision; independently checked closer primary sources, documented overlap/novelty risks and an experimental-gate design. | Complete closest theory/model equivalence and supervisor go/no-go before selecting an algorithm. |
| 2026-11-16 | Stage 4A: inspected Gonthier first-party slides/ACM text, Hajek–Seri author-hosted paper and RTAS original text; added formal objective counterexample, risk crosswalk and reading-level limitations. | Stage 4B: authorized full N01/N03/N06 text, theory reductions, database/citation checks, domain budgets. |
| 2026-11-16 | Stage 4B: derived ex-post routine-start/variable-service completion-deadline identity; elementary finite-K and blocking conditions; checked N07–N10 publisher sources; issued **REVISE/NARROW** claim-by-claim verdict. | Complete restricted full-text/theory/database coverage and supervisor sign-off. Begin Stage 5 application trace + budget provenance, not algorithm design. |
| 2026-11-16 | Stage 5A: recovered archived synthetic MQTT security-event enrichment scenario; provisionally narrowed urgent/routine classes; defined local measurement boundary, lifecycle trace schema and evidence register; historical budgets explicitly **not validated**. | Stage 5B trace/calibration, threshold validation, operator/supervisor acceptance, Stage 4 full sign-off. |
| 2026-11-16 | Stage 5B archival audit: identified actual 90-run unbounded pilot and one-seed 8-policy AMQTT smoke; independently checked saved CSV/JSON group/count arithmetic; mapped 11 incompatibilities with new RQ and 9 evidence acceptance tests. | New two-class finite-K offered-population trace/metric evidence, real service-time calibration or approved synthetic-only scope, professor sign-off. |
| 2026-11-16 | Stage 5C metric validation: independent FIFO/priority golden oracle, 9/9 fixed cases and 48/48 paired synthetic smoke runs, exact same repeat output; pure methodological verifier only. | Real/MQTT boundary reconciliation, representative application service/workload, budget values and Stage 4 sign-off before Stage 6 formal protocol. |

| 2026-11-16 | Stage 5D: verified archived callback-entry mismatch; specified post-validation offer ledger; implemented independent Python JSONL audit with fictional positive/negative/unfinished cases and reproducible double run; drafted calibration/parameter evidence gates. | Capture two-class finite-K MQTT ledger with measured or explicitly synthetic handler; validate source/service and epsilon/tau/gamma/K with supervisor. |

| 2026-11-16 | Stage 5E: runnable FIFO gateway with two classes, finite waiting K, post-dedup local offer and actual synthetic CPU work; 6/6 in-process smoke cases and one retained independent-audit fixture passed. | Real Mosquitto/Paho integration and representative handler/source calibration pending. |
| 2026-11-16 | Stage 5F: PR #47 merged into main after #46 feature-branch merge mismatch. Verified [broker-backed run #43870469820](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/actions/runs/43870469820) with 3/3 ledger audits; retained three raw synthetic JSONLs and hash provenance. | Operational field/worker calibration, professor numerical/synthetic-only and Stage 4B novelty decisions; no conference result inferred. |
| 2026-11-16 | Stage 5G: fictional device context/rule/SQLite WAL/FULL commit worker specified; self-tests and 6/6 negative audit pass; three 120-event seed traces retained. Verified [Stage 5G CI #43873927699](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/actions/runs/43873927699) and [Stage 5F regression #43873927339](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/actions/runs/43873927339) both successful. | Obtain real application semantics/arrival evidence or professor-approved synthetic-only scope, validate numerical SLA and Stage 4B originality before Stage 6. |

| 2026-11-16 | Stage 5H: synthetic MQTT→finite-K FIFO→SQLite COMMIT verified on [CI #43877369913](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/actions/runs/43877369913), 3/3 broker shapes and saved SQLite snapshots independently replayed, 131/180 offered SQL commits and 49 full-buffer rejects. [Stage 5F regression #43877369587](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/actions/runs/43877369587) PASS. Raw JSONL plus encoded SQLite evidence retained per shape. | New archived-fixture replay workflow revision awaits next CI run; field handler and workload, real D_u/epsilon/tau/gamma/K, crash recovery, and Stage 4B novelty sign-off still unavailable. |

| 2026-11-16 | Stage 5I: 16-field external-evidence register, blank operational parameters, independent lifecycle/SQLite-backed fail-closed readiness gate and nine defensive self-test cases; archived synthetic Stage5H base trace produces 23 blocker `NOT_READY` diagnosis. | Stage 5I [CI #43880322439](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/actions/runs/43880322439) SUCCESS and Stage 5F regression SUCCESS; actual rights-cleared device/handler service evidence, application-owner requirements and supervisor Stage4B novelty decision not available. |

**Rules for future updates:** Update the date and dashboard; check only completed, traceable work; add evidence links; do not report preliminary models/claims as validated findings; preserve the current RQ text unless a new reasoned team decision supersedes it.
