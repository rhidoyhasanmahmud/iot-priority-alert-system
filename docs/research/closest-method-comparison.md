# Closest-method comparison and comparator decision

Reviewed 21 October 2026 (Malaysia). Decision: retain the implemented matched controls for the registered mechanism study. The external-method comparison and algorithmic novelty gate remain open. No primary outcomes were inspected or generated for this review; `configs/research-v1.json` is unchanged.

## Verified references and access

**R8.** João Carlos N. Bittencourt, Paulo Portugal, Francisco Vasques and Daniel G. Costa. “Multi-Tier Message Scheduling for IoT-Based Urban Emergency Systems Through Semantic Priority Override.” *IEEE Access*, vol. 14, pp. 140988–141015, 2026. IEEE. [DOI: 10.1109/ACCESS.2026.3732592](https://doi.org/10.1109/ACCESS.2026.3732592). [Publisher abstract](https://ieeexplore.ieee.org/abstract/document/11685955).

Relevance: TRIAGE/4 addresses semantic alarm precedence and device fairness in an MQTT emergency setting, making it the closest conceptual comparator. The publisher abstract describes four operational bands and simulation plus a prototype. This is abstract-level evidence only; exact dispatch, fairness and protection rules remain unverified here.

**R9.** Rongping Lin, Jinpeng Zhang, Shan Luo, Jing Fu, Xiong Wang, Hui Li and Moshe Zukerman. “Real-Time Priority Queue Scheduling for Bursty Traffic.” *IEEE Internet of Things Journal*, vol. 12, no. 24, pp. 55883–55892, 2025. IEEE. [DOI: 10.1109/JIOT.2025.3627212](https://doi.org/10.1109/JIOT.2025.3627212). [University bibliographic record](https://scholars.cityu.edu.hk/en/publications/real-time-priority-queue-scheduling-for-bursty-traffic/) · [Author postprint](https://www.ee.cityu.edu.hk/~zukerman/J207.pdf).

Relevance: WTI schedules switch queues using priority and instantaneous congestion. The author postprint's Section III, Algorithm 1 and Section IV describe offline indices derived from state-transition data and runtime index lookup. This establishes substantial prior overlap with occupancy-aware scheduling; it does not establish equivalence to our event-level heuristic.

| Access check | Observation on review date | Review boundary |
| --- | --- | --- |
| R8 publisher abstract | Search-indexed publisher abstract and bibliographic metadata accessible | Conceptual overlap can be discussed |
| R8 publisher document page | Returned JavaScript/robot-verification page | Full method not read |
| R8 publisher PDF links | One fetch returned HTTP 418; the other was inaccessible | No full-text reproduction or absence-of-feature claim |
| R9 university record | Title, authors, venue, pages and DOI available | Citation verified |
| R9 author postprint | Ten-page PDF accessible; method, algorithm and implementation sections reviewed | Focused method comparison; no independent replication |

No publisher PDFs are redistributed in this repository. Search-result availability alone does not establish that a discovered third-party manuscript matches the final published method. Journal quartiles and index coverage were not independently checked and are not asserted.

## Model alignment

The R8 column below is restricted to its publisher abstract. “Unresolved” means this review has insufficient evidence; it does not mean the feature is absent.

| Dimension | This repository | R8: TRIAGE/4 | R9: WTI |
| --- | --- | --- | --- |
| Scheduling object | Individual alert in one application worker | Emergency-message scheduling; exact service boundary unresolved | Multiple output queues of a switch |
| Decision inputs | Original priority, wait, global occupancy, optional absolute deadline, fixed service estimate | Semantic alarm/zone priority and device fairness; detailed state unresolved | Queue state, priority and learned transition information |
| Main intervention | Adaptive aging with estimated urgent-deadline guard | Four-band semantic override; exact rules unresolved | Offline Whittle indices and runtime queue selection |
| Resource model | One non-preemptive worker, shared waiting capacity, reject incoming when full | Admission/protection details unresolved | Slotted queue service and queue-capacity state |
| Outcome alignment | Completed-event routine p95 wait plus urgent failure and loss | Alarm responsiveness and device fairness | Queueing, packet loss and network performance |
| Reproduction decision | Executable registered implementation | Full-text specification needed first | Requires explicit queue/service/training mapping |

Our method has no geographic-zone model or device-fairness objective. Its `source` field supports deduplication; it is not a device-fair scheduling mechanism. The current simulator also has no transition-learning phase or packet-byte service model. These are implementation differences, not proof of novelty or reasons to dismiss relevant prior methods.

## What the existing controls can answer

| Comparator | Purpose | Limit |
| --- | --- | --- |
| FIFO, strict priority, EDF | Common reference behavior and urgency/deadline tradeoffs | Cannot establish novelty against recent research |
| Historical fixed aging | Continuity with diagnostic pilot | Untuned reference; different tie-breaking |
| Tuned matched fixed guarded | Isolate occupancy adaptation with shared guard and deadline tie-breaking | Internal mechanism control, not a published closest method |
| Adaptive and matched fixed without guard | Component contrasts at inherited frozen settings | Unguarded variants are not independently optimized |

Keep these controls. Adding more simple controls does not close the closest-method gap. A positive result against the matched fixed rule would support a narrow empirical mechanism finding within the registered model, subject to uncertainty and loss checks. It would not establish superiority to TRIAGE/4 or WTI.

## Comparator implementation acceptance criteria

Before implementing an external method, record a specification with its source section/page, exact ordering and ties, admission rules, parameters and missing details. Then use the following checklist:

1. **Faithfulness:** obtain the complete method and identify an official implementation if available. Record the version and license. If details are ambiguous, record the ambiguity instead of choosing a convenient weak interpretation.
2. **Information parity:** list all inputs available to each scheduler at dispatch. Prohibit future arrivals and true future service costs. Any learned model must use training/tuning data only; account for training and update cost.
3. **Resource parity:** reconcile shared versus per-class buffers, total capacity, variable service costs, preemption and dispatch timing. Report any information or resource advantage explicitly.
4. **Traffic parity:** replay identical logical arrivals, priorities, deadlines and service costs. A method that filters traffic needs separate offered/admitted/completed counts and loss accounting. If new metadata is required, register how it is generated.
5. **Validation:** hand-check dispatch examples and invariants against the published specification before collecting comparison results. A plausible heuristic with a borrowed name is not a reproduction.
6. **Parameter fairness:** freeze search space and tuning objective before held-out runs. State whether the comparison evaluates the method's original objective or an adaptation to ours. Report wall-clock scheduling overhead separately from modeled service.
7. **Naming:** call modified algorithms adaptations and enumerate changes. An adaptation is not evidence that the original algorithm performs poorly.

For R8, obtaining and reviewing the complete dispatch and protection specification is the immediate dependency. For R9, a comparator specification must additionally resolve class queues, service slots, buffer allocation and transition-estimation data. Model mismatch can justify a scoped adaptation or a different experimental track; it does not by itself justify excluding a relevant competitor from a broad superiority claim.

## Protocol and execution decision

The existing version 1 experiment can answer the internal mechanism question. Its primary runs remain unexecuted in the checked-in evidence. It cannot settle external superiority or contribution originality.

Before committing the large primary budget, complete the R8 full-text assessment and choose a defensible comparison scope. If that adds methods, metadata, training, metrics or scenarios, create a versioned protocol amendment and registration before held-out execution. Preserve v1 unchanged. If any prior held-out outcomes have been inspected, document that fact and reserve fresh evaluation seeds for revised confirmatory claims.

A practical next work unit is the external comparator specification, followed by deterministic reproduction checks and a small engineering run. If full text remains unavailable, the blocker should stay explicit. A small original-code engineering run can still guide runtime/storage planning, but cannot be labelled a completed closest-method comparison.

## Wording supported at this stage

“An experimental application-worker scheduler combines occupancy-dependent aging with an estimated urgent-deadline guard. The evaluation is designed to isolate the occupancy and guard components and measure routine waiting alongside deadline failure and loss.”

Avoid “first adaptive MQTT scheduler,” “novel because it combines aging and priority,” “guaranteed deadlines,” “prevents starvation,” “attack-resistant,” or “outperforms state of the art.” These statements lack supporting evidence here. Full experiments may support narrower findings, including null results or an urgency/routine tradeoff.
