# Literature review workspace

**Purpose:** understand existing evidence before choosing the conference-paper contribution. Current register: **7 full-text review notes**, with additional catalog-only items. Target: approximately **20-25 relevant full-text reviews**, including deep study of the closest methods. The number is a planning target, not an adequacy guarantee.

## Reading route

1. [Search scope and selection method](search.md)
2. Individual reviews in the register below
3. [Cross-paper comparison](synthesis/comparison.csv)
4. [Findings, disagreements and open questions](synthesis/findings.md)

## Review register

| ID | Paper | Year | Research theme | Status |
| --- | --- | ---: | --- | --- |
| R01 | [PrioMQTT: A prioritized version of the MQTT protocol](reviews/R01-priomqtt-2024.md) | 2024 | MQTT transmission priority | Full text reviewed; not replicated |
| R02 | [Priority-enabled MQTT: a robust approach to emergency event messaging](reviews/R02-priority-enabled-mqtt-2024.md) | 2024 | Emergency messaging architecture | Full text reviewed; not replicated |
| R08 | [Multi-Tier Message Scheduling for IoT-Based Urban Emergency Systems Through Semantic Priority Override](reviews/R08-triage4-2026.md) | 2026 | Semantic alarm priority and source fairness | Full text reviewed; not replicated |
| R09 | [Real-Time Priority Queue Scheduling for Bursty Traffic](reviews/R09-wti-bursty-queues-2025.md) | 2025 | Learned queue-state scheduling under bursts | Full text reviewed; not replicated |
| R10 | [Scheduling for Periodic Multi-Source Systems with Peak-Age Violation Guarantees](reviews/R10-grr-peak-age-2023.md) | 2023 | Periodic freshness and violation analysis | Full text reviewed; not replicated |
| R11 | [Adaptive Priority Scheduling of Internet of Things Data for Disaster Management in Smart Cities](reviews/R11-adaptive-disaster-2024.md) | 2024 | Multi-hop deadline-progress scheduling | Full text reviewed; not replicated |
| R12 | [Online age of information scheduling: The power of packet management and fairness](reviews/R12-online-aoi-fairness-2026.md) | 2026 | Online fairness and replaceable updates | Full text reviewed; not replicated |

[References and reading status](references.json) also retain catalog-only items R03-R07. Their reserved IDs explain numbering gaps; they are not counted as completed reviews. R10 is a 2023 foundation paper; most new collection should prioritize 2024-2026 relevance.

## Review standard

Use the [critical-review template](review-template.md). Each review distinguishes the research problem, authors' contribution, model assumptions, mechanism, source-located evidence, reviewer appraisal and synthesis question. English is the technical record; a short Bangla reading note supports recall.

A full-text read is not an independent replication. Do not turn an unevaluated question into a novelty claim. Old implementation comparisons and extended teaching notes remain available through each review's provenance link, outside this active reading flow.

## Current decision

The question area is urgency, routine service, deadlines and overload in IoT messaging. The algorithm, comparator implementation and simulation protocol are not selected. Read and synthesize first; revise candidate questions whenever contrary evidence appears.
