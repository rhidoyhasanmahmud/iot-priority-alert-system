# Literature review workspace

**Purpose:** understand existing evidence before choosing the conference-paper contribution. Current register: **9 full-text assessment notes**, with additional catalog-only items. Review 09 is an out-of-scope full-text exclusion record and does **not** count toward the relevant-paper target. Target: approximately **20-25 relevant full-text reviews**, including deep study of the closest methods. The number is a planning target, not an adequacy guarantee.

## Reading route

1. [Search scope and selection method](search.md)
2. Individual reviews in the register below
3. [Cross-paper comparison](synthesis/comparison.csv)
4. [Findings, disagreements and open questions](synthesis/findings.md)

## Review register

| No. | Paper | Year | Research theme | Status |
| --- | --- | ---: | --- | --- |
| 01 | [PrioMQTT: A prioritized version of the MQTT protocol](reviews/PrioMQTT%20-%20A%20prioritized%20version%20of%20the%20MQTT%20protocol.md) | 2024 | MQTT transmission priority | Full text reviewed; not replicated |
| 02 | [Priority-enabled MQTT: a robust approach to emergency event messaging](reviews/Priority-enabled%20MQTT%20-%20a%20robust%20approach%20to%20emergency%20event%20messaging.md) | 2024 | Emergency messaging architecture | Full text reviewed; not replicated |
| 03 | [Multi-Tier Message Scheduling for IoT-Based Urban Emergency Systems Through Semantic Priority Override](reviews/Multi-Tier%20Message%20Scheduling%20for%20IoT-Based%20Urban%20Emergency%20Systems%20Through%20Semantic%20Priority%20Override.md) | 2026 | Semantic alarm priority and source fairness | Full text reviewed; not replicated |
| 04 | [Real-Time Priority Queue Scheduling for Bursty Traffic](reviews/Real-Time%20Priority%20Queue%20Scheduling%20for%20Bursty%20Traffic.md) | 2025 | Learned queue-state scheduling under bursts | Full text reviewed; not replicated |
| 05 | [Scheduling for Periodic Multi-Source Systems with Peak-Age Violation Guarantees](reviews/Scheduling%20for%20Periodic%20Multi-Source%20Systems%20with%20Peak-Age%20Violation%20Guarantees.md) | 2023 | Periodic freshness and violation analysis | Full text reviewed; not replicated |
| 06 | [Adaptive Priority Scheduling of Internet of Things Data for Disaster Management in Smart Cities](reviews/Adaptive%20Priority%20Scheduling%20of%20Internet%20of%20Things%20Data%20for%20Disaster%20Management%20in%20Smart%20Cities.md) | 2024 | Multi-hop deadline-progress scheduling | Full text reviewed; not replicated |
| 07 | [Online age of information scheduling: The power of packet management and fairness](reviews/Online%20age%20of%20information%20scheduling%20-%20The%20power%20of%20packet%20management%20and%20fairness.md) | 2026 | Online fairness and replaceable updates | Full text reviewed; not replicated |
| 08 | [A Cloud-Edge-End Collaborative Remote Monitoring and Scheduling System for Textile Equipment](reviews/A%20Cloud-Edge-End%20Collaborative%20Remote%20Monitoring%20and%20Scheduling%20System%20for%20Textile%20Equipment.md) | 2026 | Industrial hierarchical alerting and compute/production coordination | Full text reviewed; not replicated |
| 09 | [IoT-based smart waste management system: real-time monitoring and environmental compensation](reviews/IoT-based%20smart%20waste%20management%20system%20-%20real-time%20monitoring%20and%20environmental%20compensation.md) | 2026 | Sensor monitoring and rain-based suppression | Full text assessed; excluded from core scheduling set |

[References and reading status](references.json) also retain catalog-only items R03-R07. They are not counted as completed reviews. Internal reference keys are preserved for traceability; visible review numbers are consecutive. R10 is a 2023 foundation paper; most new collection should prioritize 2024-2026 relevance.

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
