# Literature Review Knowledge Base — IoT Priority Alert System

This folder is a **readable, evidence-traced research notebook**, not a collection of abstract paraphrases. Each paper receives a self-contained English technical explanation followed by a **collapsible Bangla explanation under every question**, so that its problem, approach, evidence, and relevance can be understood again months later without repeatedly reopening the PDF.

**Research focus:** For a bounded, non-preemptive application worker after MQTT delivery, investigate the tradeoff between **urgent-alert deadline failures** and **routine-event waiting** under normal and bursty traffic, accounting for **loss and scheduler overhead**. The proposed occupancy-aware guarded aging policy is **experimental**, and claims of state-of-the-art superiority or novelty remain subject to closest-method evaluation and completed experiments.

The pre-existing project references and comparisons remain in [Related Work](../../related-work.md), [reference metadata](../../related-work.json), and [closest-method comparison](../closest-method-comparison.md). **Do not mistake a bibliographic entry there for a completed full-text paper note here.**

## Paper index

| ID | Paper (verified actual title) | Year | Method / focus | Relevance | Evidence status | Individual note |
| --- | --- | --- | --- | --- | --- | --- |
| **R10** | **Scheduling for Periodic Multi-Source Systems with Peak-Age Violation Guarantees** — Lin, Huang & Hsu | 2023 | GRR; peak-AoI violation; IPQ vs SPQ | Medium | **Full uploaded preprint examined**; no independent replication | [Read R10](papers/R10-grr-peak-age-2023.md) |

**ID policy:** R01–R09 are already used by the repository's existing [Related Work catalog](../../related-work.md); the first **new** source receives **R10**. The individual notes for R01–R09 will be created only when corresponding source material is available for a properly scoped review. Future papers continue as R11, R12, etc., without renumbering existing references.

**Critical file-name mismatch:** The uploaded file was named *A Scheduling Approach to Minimize Peak-Age Violation with Fairness Guarantees in IIoT Systems* (a separate **ICC 2026** paper). Its contents actually identify Lin et al.'s **2023 GRR** paper. R10 is based **only on the contents of the uploaded 32-page 2023 preprint**. The incorrectly implied 2026 paper remains **unreviewed**, and will receive its own ID only when its actual full text is supplied.

### Review status meanings

| Status | Meaning |
| --- | --- |
| Metadata/abstract only | Identity and available abstract checked; detailed method/result claims are restricted |
| Partial full-text review | Selected sections read; unreviewed claims remain unresolved |
| Full uploaded manuscript examined | Core method, analytical results, experiments, figures, and limitations reviewed from the supplied version; **does not** mean independent replication |
| Replicated | Source-level reproduction and comparison procedures documented; no paper currently has this status here |

---

## Consolidated literature findings

> **Scope:** This synthesis currently covers **one individually reviewed source (R10)**. The pre-existing R01–R09 catalog includes other relevant works but is **not falsely counted as nine full reviews**. Update this section as actual individual notes are added.

### 1. Freshness and deadline failure are different objectives

**R10:** The AoI of a source measures **how old the receiver's freshest delivered status is**. The paper studies the *probability* that **peak AoI** crosses a threshold. This is useful motivation for studying tails/violations rather than only averages, but **it is not equivalent to an alert exceeding its own processing deadline**.

**Implication:** In our experiment reports, keep **urgent deadline-failure rate**, **routine waiting time**, **admission loss**, and optional **freshness measurements** conceptually distinct. Do not label deadline miss as peak-AoI violation without an appropriate generation/delivery model.

### 2. Where scheduling happens changes what can be compared

**R10:** GRR determines **which periodically updating source group and source** receives transmission service; IPQ/SPQ govern **which status update** a given source keeps. Its model is a shared base station with per-source queues.

**Our model:** A shared application-level worker **after MQTT delivery** schedules distinct alert events. Changing an arrival-generation process, network transmission protocol, queue capacity, or packet discard policy changes the evaluated problem.

**Implication:** R10 offers transferable scheduling intuition and a mathematical tail-risk viewpoint, **not a fair direct benchmark** against our current alert scheduler.

### 3. Stale measurements and indispensable alerts must be distinguished

**R10:** SPQ retains the latest waiting measurement and can outperform IPQ on freshness when transmitting older statuses becomes counterproductive.

**Risk for our project:** If two messages represent **different emergency incidents**, dropping the earlier alert because a later alert arrived can be unacceptable. A measurement replacement policy cannot simply be reused as emergency loss management.

### 4. Strong claims require the right evidence

**R10:** The reported results combine mathematical bounds with computer simulations. GRR improves the modeled violation-probability trends versus standard RR for most of the source groups examined; the paper explicitly notes an exception for the group favored by RR. For SPQ a tight analytical lower bound was **not** obtained.

**Implication:** Keep simulation-only claims separate from mathematical guarantees. Report workload assumptions, baseline choices, group-specific exceptions, and uncertainty. Do not infer unconditional or application-wide superiority.

---

## Cross-paper comparison matrix

This table will grow as **additional notes** are actually completed. Existing R08 and R09 summaries below are **pointers to the older scoped repository review**, not new full-paper reviews.

| ID | Scheduling object and context | Core technique | Objective/evidence | Relationship to our study | Review boundary |
| --- | --- | --- | --- | --- | --- |
| **R08** | Emergency-message scheduling (source/model details unresolved) | TRIAGE/4 semantic bands and device fairness | Alarm responsiveness/fairness in publisher abstract | **Closest conceptual overlap**; complete rules must be obtained before reproduction | Existing [closest-method note](../closest-method-comparison.md) is primarily **abstract-level** |
| **R09** | Network switch output queues under bursty traffic | Whittle-index priority/queue-state scheduling | Queue-level performance in a different resource model | Shows congestion/priority approaches are prior art; model alignment required | Existing [closest-method note](../closest-method-comparison.md) examines method sections; **not replicated** |
| **R10** | Periodic heterogeneous status updates via base station | Frequency-aware GRR; IPQ/SPQ | Peak-AoI violation bounds and simulated trends | Useful related theory/metric; **not a direct fairness/deadline comparator** | **Full supplied preprint reviewed**, without independent replication |

**Interpretation rule:** “Not verified,” “unresolved,” or “not directly comparable” never means the competing paper lacks a method or feature. It means the evidence presently available **does not support an absence or equivalence claim**.

---

## Research gaps and decision log

| Candidate observation / gap | Present evidence | Status | Research action |
| --- | --- | --- | --- |
| Averages may hide threshold exceedance | R10's AoI/peak-age motivation and analysis | **Established within R10's model** | Explain and report relevant tail/violation metrics carefully |
| Scheduling heterogeneity matters | GRR vs RR in R10's periodic multi-source simulations | **Supported for tested setup** | Do not transfer directly to bursty event-worker scheduling |
| Occupancy-dependent aging's unique contribution | Existing R08/R09 record; our candidate design | **Unresolved novelty question** | Complete closest-method comparison and reproducible evaluation |
| Urgent response versus routine waiting under bursts | Our registered research question; baseline designs | **Candidate empirical question** | Execute matched, loss-aware experiments and quantify uncertainty |
| Formal guarantee for our MQTT worker | R10 proves results only in a different mathematical model | **Not established** | Avoid “guaranteed deadline”/“prevents starvation” claims |

**Current decision:** Keep R10 as an **AoI theory and threshold-analysis background reference**. Do **not** implement GRR as a direct baseline solely on the basis of this paper. Preserve the project's existing research protocol and closest-method gate.

---

## How to write every future paper note

Store one Markdown document per actual paper under **papers/**. Preserve the **five fixed questions**, each with its English explanation first and a GitHub-compatible **Bangla collapsible section directly underneath**:

1. **What?** — What problem does the paper solve? Define the objective, key metrics, and boundaries.
2. **Why?** — Why does this problem matter? What exactly is missing from the compared approaches? Distinguish authors' positioning from independently established gaps.
3. **How?** — Explain system model, assumptions, algorithm, mathematical intuition, **step-by-step worked example**, and alternative configurations.
4. **Evidence?** — Record baselines, workload/dataset, parameters, figures, actual outcomes, uncertainty, and which claims are analytical versus empirical. **Do not invent percentages from charts.**
5. **So What?** — Critically discuss strengths, limitations, reproducibility, transfer to our queue/traffic model, related-work placement, and the **decision for our research**.

Under **each** answer, use native GitHub Markdown HTML:

    <details>
    <summary>🇧🇩 বাংলা ব্যাখ্যা — What?</summary>

    এখানে একই technical ধারণা সহজ বাংলায় ব্যাখ্যা করা হবে।
    কোনো assumptions বা findings বদলানো হবে না।

    </details>

### Mandatory source discipline

- Record the **actual PDF title and authors**, verified venue, publisher, year, and DOI/official source. **Never trust uploaded filenames alone.**
- If the supplied document is an **arXiv preprint**, distinguish its page numbering/version from the published article.
- Give **section, page, figure, theorem, or equation** identifiers for substantive technical claims; any fabricated pedagogical example must be clearly labeled as such.
- Separate **author-reported result**, **our explanatory paraphrase**, **our critical inference**, and **suggested implementation action**.
- Keep effects within the authors' traffic/service/threshold assumptions. Explicitly note important comparator or replication gaps.
- Do not commit third-party PDFs to this public repository unless redistribution permissions have been checked; DOI and source links suffice.
- When a new paper is fully reviewed: create its note, add a row to the **Paper index**, update the **Consolidated literature findings**, **Cross-paper comparison**, and **Research gaps/decisions**. If appropriate, also append verified metadata to the existing [related-work catalog](../../related-work.json) via a separately reviewed edit.

**For future reading:** Start with this README for the cross-paper synthesis, then open the individual note when the algorithm/evidence needs to be recalled.
