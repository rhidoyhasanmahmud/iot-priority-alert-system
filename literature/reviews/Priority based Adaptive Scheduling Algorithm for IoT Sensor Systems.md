# Priority based Adaptive Scheduling Algorithm for IoT Sensor Systems

## 1. Bibliographic record and source

- **Review 15 · R24 · core-related mechanism; MAC/time-slot priority and adaptive sleep control.** Retain as prior art, with limited class-timing evidence.
- **Authors:** K. Kavitha; G. Suseendran.
- **Publication:** 2019 International Conference on Automation, Computational and Technology Management (ICACTM), pp. 361–366, 2019. Publisher: IEEE.
- **DOI:** [10.1109/ICACTM.2019.8776691](https://doi.org/10.1109/ICACTM.2019.8776691). [Official IEEE Xplore record](https://ieeexplore.ieee.org/abstract/document/8776691).
- **Verification, 15 November 2026:** indexed official IEEE record confirms title, venue, publisher and DOI; [VISTAS institutional record](https://ir.vistas.ac.in/id/eprint/9133/) links the same publication and manuscript. Direct IEEE HTML retrieval was blocked. No conference-ranking or indexing claim.
- **Read source:** supplied `Paper-64-IEEE-Xplore.pdf`, six published pages. Printed page = PDF page + 360. Page citations below use printed pages, with PDF locations where useful. SHA-256: `384e1fe73410acb21de361e70d0272544faebe19f82664897d769778c0857cb9`.
- Full-text critical reading; classification, policy table and result pages visually checked. No independent simulation or source-code verification. PDF not redistributed.

## 2. Research problem

Heterogeneous IoT sensor traffic has different delay tolerance, data rate and energy constraints. PASA makes base-station time-slot/channel assignments and adapts sensor sleep behavior using traffic class and resource-state signals. The relevant contribution is priority-aware control of transmission opportunity and traffic loss, rather than a new broker priority queue (Section III, pp. 362–363).

It belongs in the mechanism comparison because changing when a source may transmit changes urgency handling and offered work downstream. Its MAC/radio model must remain explicit.

## 3. Authors' claimed contribution

PASA combines collision-free priority-based slot allocation with an adaptive `ST` policy using traffic priority, remaining buffer size, remaining energy and transmit power. The paper reports better delivery ratio, residual energy and throughput than EE-CATS in NS2 (abstract; Sections III–V).

Delay sensitivity motivates the traffic classes, but deadline-miss rates, class-wise response tails and routine starvation protection are not evaluated in the reported tables. A no-delay-tolerance label is an input requirement, not evidence that the requirement was met.

## 4. Model and assumptions

- A base station controls slots/channel offsets in an IEEE 802.15.4 sensor network. Matching and graph coloring address duplex/interference conflicts (p. 362). This control cannot be assumed available to a message-broker scheduler.
- Four classes (Table I, p. 362): PR1 emergency/low data rate/no delay tolerance; PR2 real-time/medium rate/L1–L2 tolerance; PR3 real-time/high rate/L1 tolerance; PR4 non-real-time/low rate/L2 tolerance. Lower priority number means greater importance here.
- `ST` is presented as duty-cycle/sleep-time control. Table II explicitly explains PR1 `ST=0` as immediate activation (p. 363); it does not mean the emergency receives zero service. Larger sleep settings trade activity for energy.
- The purported remaining buffer estimate is `RBS = pr × (TBS / ND)`, where `TBS` is total buffer size and `ND` neighbor density (Equation 1, p. 363). It is not a measurement of current queue occupancy: holding those inputs fixed leaves it unchanged when packets arrive or depart.
- Remaining energy is initial energy minus transmit/receive energy (Equation 2); power is compared with a reference (Equation 3). HIGH/MEDIUM/LOW cutoffs, numeric sleep durations and complete energy-accounting details need specification.
- NS2 configuration (Table III, p. 363): 21/41/61/81/101 nodes, 50×50 m topology, constant-bit-rate traffic, 2–10 flows, omnidirectional antennas, initial energy 10 J, transmit/receive power 0.7/0.5 W. A reproducible run duration, repeated-seed protocol and confidence intervals are not adequately supplied in this six-page report.

## 5. Method and decision mechanism

**Transmission opportunity:** the base station selects conflict-free links via matching, assigns channel offsets using graph coloring, updates queue levels after a slot, then chooses subsequent links according to traffic priority (Section III-B, p. 362). Queue-level updates exist in this slot procedure; they must not be confused with Equation 1's separate `RBS` proxy.

**Sleep adaptation:** PR1 activates immediately. For the other classes, OR conditions on buffer, energy and power categories select HIGH/MEDIUM/LOW `ST` (Table II and pseudocode, p. 363). PR4's medium state yields HIGH sleep in both the table and code. That is part of the printed method, not a transcription error to be silently repaired. Mixed states also depend on the order of the `if/else if` branches; categorical cutoffs and the PR2 uncovered medium combination need clarification.

This is combined link scheduling and duty-cycle control. It does not supply task aging, an EDF rule, an explicit routine quota or a bounded-wait argument. Its gain cannot be assigned solely to a priority ordering change.

## 6. Evidence ledger

| Claim examined | Source location | Actual evidence | Interpretation boundary |
| --- | --- | --- | --- |
| Emergency traffic receives immediate activation | Tables I–II and adaptive algorithm, pp. 362–363 / PDF pp. 2–3 | PR1 maps to `ST=0`, explained as immediate activation; other classes use state-dependent sleep. | Activation is not a measured end-to-end deadline or delivery guarantee. |
| Adaptation accounts for congestion | Equation 1 and slot algorithm, pp. 362–363 | Slot logic updates queue levels, but the separate `RBS` formula depends on priority, total buffer and neighbor density. | Do not describe `RBS` as measured live occupancy. Which signal drives each implementation decision needs confirmation. |
| Delivery and loss improve with network size | Tables IV–V, p. 364 / PDF p. 4 | At 101 nodes PASA/EE-CATS delivery is 0.81268/0.7146 and drop counts 11168/20660; PASA has higher delivery and fewer drops at all tabulated node counts. | Aggregate observations; no class-specific loss/deadline tail, offered-population ledger or uncertainty estimate. |
| Throughput and energy improve with network size | Tables VI–VII, p. 364 | At 101 nodes residual energy is 7.48596/6.086805 J and throughput 0.803/0.5108 Mb/s for PASA/EE-CATS. | One configuration family; priority and sleep/link control change together. |
| PASA dominates across traffic flows | Tables VIII–XI, p. 365 / PDF p. 5 | Most metrics favor PASA, but at two flows throughput is 0.272 versus 0.29 Mb/s, a contrary result. At ten flows throughput is 1.1908 versus 0.5008 Mb/s. | The prose's general throughput advantage must not erase the two-flow regression or be treated as a uniform percentage gain. |

## 7. Critical appraisal

**Useful prior art.** The method shows priority combined with source activity/resource-state control well before this project's proposed work. It is especially relevant to questioning whether reduced queue delay/loss comes from service order, altered transmission opportunity or changed traffic reaching a bottleneck.

**Construct and reproduction limits.** The name remaining buffer space overstates what Equation 1 measures. Replacing it with actual occupancy would be a new adaptation, not a faithful reconstruction. Exact sleep values, state thresholds, mixed-state precedence, PR2 medium handling and traffic-class mixtures require clarification. These limitations restrict baseline fidelity while leaving the qualitative combined-control mechanism identifiable.

**Causal/statistical validity.** NS2 results compare a bundled intervention with EE-CATS, without clearly isolating priority versus collision-free scheduling versus sleep adaptation. Means/tables without sufficient run/seed/variance information do not establish significant improvements. Use exact table endpoints, including unfavorable ones, instead of repeating broad summary percentages whose aggregation is unclear.

**External validity.** CBR radio-network traffic is not a controlled urgent-burst overload experiment. Packet delivery, throughput and residual energy do not establish routine waiting protection, urgent deadline success or broker-level application latency. A different decision location is a comparison boundary, not grounds to declare the method unrelated.

**Research use:** retain as conceptually close priority/source-control prior art. It is not ready as a quantitative alert-scheduling baseline without specification and model alignment.

## 8. Synthesis contribution and open question

Compare PASA with the existing MQTT back-off paper: both combine scheduling preferences with control over source access, but PASA uses radio slots and sleep settings rather than broker-directed publish back-off. Compare its `RBS` proxy with WTI's explicit queue state; these are not equivalent occupancy-aware policies.

**Open reading question:** which methods isolate the urgent-service and low-class-loss effects of source activity control from downstream queue ordering, under equal offered traffic and energy budgets? That is a literature question, not a selected experiment or a novelty claim.

**Bangla note:** এই paper priority + transmission/sleep control বোঝার জন্য রাখা হয়েছে। “Remaining buffer” নাম দেখে এটাকে actual queue-occupancy feedback বলা ঠিক হবে না।

[Register](../README.md) · [Comparison](../synthesis/comparison.csv) · [Synthesis](../synthesis/findings.md)
