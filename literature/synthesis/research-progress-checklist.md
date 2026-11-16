# Conference research progress — step-by-step checklist

**As of:** 16 November 2026 · **Track:** RQ v1.0 (*Routine-Service Protection Under Bursty IoT Alerts*) · **Rule:** check a box only when its *evidence link or decision record* exists. “Paper read” and “paper found” are different events. Do not change the main RQ merely because a competing paper appears; make a reasoned review decision.

## Live dashboard

| Stage | Status | Work product | Exit / blockers |
| --- | --- | --- | --- |
| 1. Topic, review scope and research question | **Completed for current iteration** | [RQ v1.0](research-questions.md) | Domain-derived numeric service budgets still needed |
| 2. Core literature review | **19 completed retained notes** | [Register](../README.md), [matrix](comparison.csv), [synthesis](findings.md) | More papers only when a specific gap requires them |
| 3. Adversarial novelty screening | **Completed as a focused audit; NOT novelty-certified** | [Independent audit](novelty-assessment.md), [search log](../search-log.csv) | N01 directly challenges the broad claim |
| 4. Closest theory and database coverage | **Pending — critical path** | Side-by-side theory-equivalence worksheet | Full-text N01/N02/N03/N05/N06, citation chasing |
| 5. Application and measurable requirements | **Pending** | Domain/trace provenance + budget memo | Epsilon, tau, gamma, K, service distribution, deadlines |
| 6. Evaluation pre-registration | **Pending** | Signed protocol | Faithful baselines, acceptance rules, workloads and statistics |
| 7. Implementation and result validation | **Not started in this literature-only main branch** | Reproducible code/results | Invariants, independent traces, held-out results |
| 8. Contribution, manuscript and review | **Not started** | Supervisor go/no-go + submission draft | Confirm novelty and venue fit |

**Current gate:** close Stage **4** before committing to a new scheduler design. The existing implementation is archived; this tracker does not claim it has been reproduced or benchmarked.

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

## Step 4 — Closest-paper/model equivalence (NEXT)

For **N01 Gonthier et al.**:
- [ ] Obtain and read the complete publisher/authors' paper, including the algorithms and experiments.
- [ ] Map their objective “urgent deadline completion + maximum routine flow” to ours “urgent offered failures + routine starts within tau.”
- [ ] Map server count (including one processor), finite queue/admission assumption, known/unknown service times and rejected-job treatment.
- [ ] Reproduce or fairly adapt their EDF+FIFO/Greedy-Slack-style baseline under matching information.
- [ ] Write an explicit conclusion: equivalent, subsuming, partially overlapping, or incomparable; justify each mismatch.

For **N02–N06**:
- [ ] Read N02 network-calculus assumptions and derive whether a routine queue waiting bound applies.
- [ ] Obtain complete N03 latency/fairness and N05 multiclass-buffer analyses.
- [ ] Obtain complete N06 online hard-deadline admission analysis.
- [ ] Check N04 if any service-time predictor is introduced; otherwise cite as a boundary/limitation.
- [ ] Conduct reproducible independent database searches (e.g., Scopus/IEEE/ACM) and citation chasing; log dates, strings, result counts, exclusions and full-text limits.
- [ ] Present a 1–2 page novelty-go/no-go memo to the supervisor, with a precise **not-yet-published substantive claim** or a decision to reframe.

**Checklist outcome:** *PENDING. This is a research validity gate, not a coding task.* Evidence to create: a source-specific theory/model crosswalk linked from [the audit](novelty-assessment.md).

## Step 5 — Application and experimental targets

- [ ] Specify where a job enters the **local processing** boundary and what constitutes service start/completion.
- [ ] Collect or justify a source for real arrival bursts, per-job service demand and class mix.
- [ ] Explain actual urgency/deadline requirements and use plausible non-sensitive traces.
- [ ] Predeclare epsilon, tau, gamma, K and sensitivity ranges before tuning.
- [ ] Document offered job count, offered **work** and queue occupancy; avoid hidden upstream rate-limiting.

**Checklist outcome:** *PENDING. Any chosen thresholds without evidence must be labeled illustrative, not validated.*

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

**Rules for future updates:** Update the date and dashboard; check only completed, traceable work; add evidence links; do not report preliminary models/claims as validated findings; preserve the current RQ text unless a new reasoned team decision supersedes it.
