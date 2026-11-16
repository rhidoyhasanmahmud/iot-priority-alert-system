# Search scope and selection method

## Review question

What mechanisms balance urgent-message responsiveness, routine service and loss in IoT messaging, and under which traffic, service and information assumptions are their benefits supported?

This is a working question for a **focused critical review**, not a registered systematic review. The conference study's narrower question and scope are in the [research-question note](synthesis/research-questions.md).

## Search scope

- Priority years: 2024-2026. Retain older foundational methods when justified.
- Sources: Google Scholar for discovery; IEEE Xplore, ACM Digital Library, ScienceDirect and Springer Link for authoritative publication records; legitimate author repositories for accessible manuscripts.
- Search concepts: IoT/MQTT/edge messaging; priority/deadline/aging; bursts/overload; fairness/admission/loss.
- Candidate queries: `MQTT message prioritization`; `IoT deadline-aware scheduling`; `priority scheduling bursty traffic`; `IoT queue scheduling fairness overload`.

These are proposed queries, not searches claimed to have been executed.

## Selection

Include work with a relevant dispatch/admission mechanism, a useful theoretical model, or evidence that changes the evaluation question. Record why the paper belongs in the review.

Exclude duplicates, unavailable full texts from the completed-review count, and generic IoT applications without a relevant mechanism. Record exclusion reasons when screening new results. Low citation count is not grounds to exclude recent work. Do not assume indexing or quartile status without verification.

## Search records for future sessions

When a new search is actually performed, record date, database, exact query, filters, candidate DOI/title, decision and reason in a search-log CSV. Create that file with real entries; do not backfill invented historical searches. The inherited catalog has no complete historical search log. The [executed-search log](search-log.csv) starts with the bounded research-question checks of 15 November 2026; it does not reconstruct older searches or imply exhaustive screening.

## Reading and updating

1. Screen title/abstract and verify publication identity.
2. Read model/method and relevant evaluation or proofs.
3. Write a source-located critical review using the template.
4. Update the register, reference metadata and comparison row.
5. After each 4-5 papers, update synthesis with supporting and conflicting evidence.

Read the closest 5-8 methods deeply. Stop broad collection when decisions are well supported, rather than assuming a numerical threshold guarantees completeness. Preserve negative findings and model incompatibilities.

## Gate before implementation

The [research-question note](synthesis/research-questions.md) now fixes one main question and three sub-questions within the selected routine-protection direction. Admission/outages and label robustness are parked. Resolve the closest fair-queue/deadline theory, application requirements and exact contribution before selecting a new method or evaluation protocol. Existing DRR job mappings and size-estimation research prevent simple count/work or generic prediction-error novelty claims. Plan experiments to answer the question; archived code does not establish the contribution.

## Active-set policy - 15 November 2026

Only completed, core-related full-text reviews belong in the active register, reference catalog and comparison matrix. Screen title/abstract plus method/evaluation before writing a detailed note. An IoT/MQTT application without a relevant scheduling/admission mechanism is excluded. Loosely related freshness theory or industrial architecture is not added to fill the core target.

If a paper is supporting-only or unrelated, give a short reason to the user and do not add a long active review. Catalog-only candidates are not counted or added as reviewed papers. Keep a conceptually close method despite buffer/network differences when it genuinely informs urgency, routine protection, deadlines or congestion; disclose those differences.

Relevance is separate from quality and comparator fidelity. The register and reference metadata track the current completed set; inclusion does not mean a method is ready for implementation.

A topic-related paper may be held outside the active evidence set when publication identity is unverified or unresolved fundamental method/evidence problems prevent dependable use. State that reason explicitly; do not label it unrelated. For supplied batches, keep brief screening decisions in the review PR description rather than creating detailed active reviews for rejected items.

