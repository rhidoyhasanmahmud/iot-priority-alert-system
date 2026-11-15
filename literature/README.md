# Literature review workspace

**Purpose:** understand existing evidence before choosing the conference-paper contribution.

**Relevance-audited progress:** 9 full-text assessment notes = **5 core-related + 3 supporting-only + 1 excluded**. Five additional catalog entries remain pending full-text screening. Only the 5 core-related completed reviews count toward the **20-25 relevant-paper target**. This is a reading target, not proof of literature completeness.

See the [paper-by-paper relevance audit](relevance-audit.md). Relevance and methodological quality are assessed separately; a core paper is not automatically a faithful implementation baseline.

## Reading route

1. [Search scope and selection method](search.md)
2. Individual reviews in the register below
3. [Cross-paper comparison](synthesis/comparison.csv)
4. [Findings, disagreements and open questions](synthesis/findings.md)

## Review register

| No. | Paper | Year | Relevance decision | Main limitation for our scope |
| --- | --- | ---: | --- | --- |
| 01 | [PrioMQTT: A prioritized version of the MQTT protocol](reviews/PrioMQTT%20-%20A%20prioritized%20version%20of%20the%20MQTT%20protocol.md) | 2024 | Core-related | Protocol/transmission layer; UDP/TCP change prevents queue-only gain attribution. |
| 02 | [Priority-enabled MQTT: a robust approach to emergency event messaging](reviews/Priority-enabled%20MQTT%20-%20a%20robust%20approach%20to%20emergency%20event%20messaging.md) | 2024 | Core-related | Small architecture prototype; weak timing/statistical evidence. Relevance is not a quality endorsement. |
| 03 | [Multi-Tier Message Scheduling for IoT-Based Urban Emergency Systems Through Semantic Priority Override](reviews/Multi-Tier%20Message%20Scheduling%20for%20IoT-Based%20Urban%20Emergency%20Systems%20Through%20Semantic%20Priority%20Override.md) | 2026 | Core-related; closest | Within-band fairness is not routine cross-band protection; admission and metadata must be aligned. |
| 04 | [Real-Time Priority Queue Scheduling for Bursty Traffic](reviews/Real-Time%20Priority%20Queue%20Scheduling%20for%20Bursty%20Traffic.md) | 2025 | Core-related; closest | Switch queues and learned transition/index model, not directly equivalent to a single event worker. |
| 05 | [Scheduling for Periodic Multi-Source Systems with Peak-Age Violation Guarantees](reviews/Scheduling%20for%20Periodic%20Multi-Source%20Systems%20with%20Peak-Age%20Violation%20Guarantees.md) | 2023 | Supporting only | Periodic peak-AoI objective, not urgency-class deadline or emergency-alert tradeoff. Do not treat as a direct comparator. |
| 06 | [Adaptive Priority Scheduling of Internet of Things Data for Disaster Management in Smart Cities](reviews/Adaptive%20Priority%20Scheduling%20of%20Internet%20of%20Things%20Data%20for%20Disaster%20Management%20in%20Smart%20Cities.md) | 2024 | Core-related; closest | Multi-hop routing/migration, preemption and infinite buffers complicate comparison; still core conceptual prior art. |
| 07 | [Online age of information scheduling: The power of packet management and fairness](reviews/Online%20age%20of%20information%20scheduling%20-%20The%20power%20of%20packet%20management%20and%20fairness.md) | 2026 | Supporting only | Total AoI and replaceable status updates differ from non-replaceable emergency alerts. |
| 08 | [A Cloud-Edge-End Collaborative Remote Monitoring and Scheduling System for Textile Equipment](reviews/A%20Cloud-Edge-End%20Collaborative%20Remote%20Monitoring%20and%20Scheduling%20System%20for%20Textile%20Equipment.md) | 2026 | Supporting only | Composite sensing/filtering/diagnosis/routing/placement study; not a queue-only urgency/routine policy comparison. |
| 09 | [IoT-based smart waste management system: real-time monitoring and environmental compensation](reviews/IoT-based%20smart%20waste%20management%20system%20-%20real-time%20monitoring%20and%20environmental%20compensation.md) | 2026 | Excluded: unrelated | IoT and cloud dashboard alone do not meet this research scope. |

[Reference metadata](references.json) retains five catalog-only items; these are pending, not completed full-text reviews. Review numbers preserve reading sequence and are not citation numbers.

## Review standard

Use the [critical-review template](review-template.md). Each review distinguishes the research problem, authors' contribution, model assumptions, mechanism, source-located evidence, reviewer appraisal and synthesis question. English is the technical record; a short Bangla reading note supports recall.

A full-text read is not an independent replication. Do not turn an unevaluated question into a novelty claim. Old implementation comparisons and extended teaching notes remain available through each review's provenance link, outside this active reading flow.

## Current decision

The question area is urgency, routine service, deadlines and overload in IoT messaging. The algorithm, comparator implementation and simulation protocol are not selected. Read and synthesize first; revise candidate questions whenever contrary evidence appears.

## File naming and order

Name each review after the **full paper title**, preserving readable words and capitalization, with a `.md` extension. Do not prefix a review number or append a year unless it is part of the actual title.

For example: `PrioMQTT - A prioritized version of the MQTT protocol.md`.

Replace filename-unsafe punctuation such as a colon or slash with a readable hyphen or space. The exact bibliographic title remains in the review and reference metadata. Use URL-encoded destinations for Markdown links containing spaces.

Consecutive review numbers remain in this register, the comparison table and review metadata; they are not filenames or bibliography citation numbers. Use DOI/internal reference keys for stable citation identity. If two distinct papers have the same title, add author and year only to disambiguate them.
