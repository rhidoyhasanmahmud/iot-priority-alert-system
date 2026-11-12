# Literature review workspace

**Purpose:** understand existing evidence before choosing the conference-paper contribution. Current register: **7 full-text review notes**, with additional catalog-only items. Target: approximately **20-25 relevant full-text reviews**, including deep study of the closest methods. The number is a planning target, not an adequacy guarantee.

## Reading route

1. [Search scope and selection method](search.md)
2. Individual reviews in the register below
3. [Cross-paper comparison](synthesis/comparison.csv)
4. [Findings, disagreements and open questions](synthesis/findings.md)

## Review register

| No. | Paper | Year | Research theme | Status |
| --- | --- | ---: | --- | --- |
| 01 | [PrioMQTT: A prioritized version of the MQTT protocol](reviews/01-priomqtt-2024.md) | 2024 | MQTT transmission priority | Full text reviewed; not replicated |
| 02 | [Priority-enabled MQTT: a robust approach to emergency event messaging](reviews/02-priority-enabled-mqtt-2024.md) | 2024 | Emergency messaging architecture | Full text reviewed; not replicated |
| 03 | [Multi-Tier Message Scheduling for IoT-Based Urban Emergency Systems Through Semantic Priority Override](reviews/03-multi-tier-message-scheduling-2026.md) | 2026 | Semantic alarm priority and source fairness | Full text reviewed; not replicated |
| 04 | [Real-Time Priority Queue Scheduling for Bursty Traffic](reviews/04-priority-queue-scheduling-bursty-traffic-2025.md) | 2025 | Learned queue-state scheduling under bursts | Full text reviewed; not replicated |
| 05 | [Scheduling for Periodic Multi-Source Systems with Peak-Age Violation Guarantees](reviews/05-periodic-multi-source-peak-age-2023.md) | 2023 | Periodic freshness and violation analysis | Full text reviewed; not replicated |
| 06 | [Adaptive Priority Scheduling of Internet of Things Data for Disaster Management in Smart Cities](reviews/06-adaptive-priority-disaster-management-2024.md) | 2024 | Multi-hop deadline-progress scheduling | Full text reviewed; not replicated |
| 07 | [Online age of information scheduling: The power of packet management and fairness](reviews/07-online-aoi-packet-management-fairness-2026.md) | 2026 | Online fairness and replaceable updates | Full text reviewed; not replicated |

[References and reading status](references.json) also retain catalog-only items R03-R07. They are not counted as completed reviews. Internal reference keys are preserved for traceability; visible review numbers are consecutive. R10 is a 2023 foundation paper; most new collection should prioritize 2024-2026 relevance.

## Review standard

Use the [critical-review template](review-template.md). Each review distinguishes the research problem, authors' contribution, model assumptions, mechanism, source-located evidence, reviewer appraisal and synthesis question. English is the technical record; a short Bangla reading note supports recall.

A full-text read is not an independent replication. Do not turn an unevaluated question into a novelty claim. Old implementation comparisons and extended teaching notes remain available through each review's provenance link, outside this active reading flow.

## Current decision

The question area is urgency, routine service, deadlines and overload in IoT messaging. The algorithm, comparator implementation and simulation protocol are not selected. Read and synthesize first; revise candidate questions whenever contrary evidence appears.

## File naming and order

Use `NN-short-paper-title-YYYY.md`, for example `08-deadline-aware-message-scheduling-2026.md`. The example is a naming pattern, not an identified paper. Numbers represent a stable review sequence, not publication year, relevance ranking or bibliography citation number. Append the next number when a new review is completed. Keep sorting/filtering by year or theme in the register instead of repeatedly renaming existing notes. Preserve DOI and internal reference keys independently of display order.
