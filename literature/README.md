# Core literature review

**5 completed, core-related reviews.** Target: approximately 20-25 relevant papers, with deep reading of the closest 5-8 methods. The number is a planning target, not proof of completeness.

## Review register

| No. | Paper | Year | Research use | Main comparison limit |
| --- | --- | ---: | --- | --- |
| 01 | [PrioMQTT: A prioritized version of the MQTT protocol](reviews/PrioMQTT%20-%20A%20prioritized%20version%20of%20the%20MQTT%20protocol.md) | 2024 | Time-critical MQTT priority | Transport changes alongside priority |
| 02 | [Priority-enabled MQTT: a robust approach to emergency event messaging](reviews/Priority-enabled%20MQTT%20-%20a%20robust%20approach%20to%20emergency%20event%20messaging.md) | 2024 | Emergency-message class handling | Small prototype and unclear timing endpoints |
| 03 | [Multi-Tier Message Scheduling for IoT-Based Urban Emergency Systems Through Semantic Priority Override](reviews/Multi-Tier%20Message%20Scheduling%20for%20IoT-Based%20Urban%20Emergency%20Systems%20Through%20Semantic%20Priority%20Override.md) | 2026 | Closest alarm/fairness/admission work | Within-band fairness and admission shaping differ from routine-class protection |
| 04 | [Real-Time Priority Queue Scheduling for Bursty Traffic](reviews/Real-Time%20Priority%20Queue%20Scheduling%20for%20Bursty%20Traffic.md) | 2025 | Closest burst/congestion-aware priority work | Switch queues require transition training/model alignment |
| 05 | [Adaptive Priority Scheduling of Internet of Things Data for Disaster Management in Smart Cities](reviews/Adaptive%20Priority%20Scheduling%20of%20Internet%20of%20Things%20Data%20for%20Disaster%20Management%20in%20Smart%20Cities.md) | 2024 | Closest adaptive urgency/deadline work | Multi-hop routing/migration and infinite buffers |

## Reading workflow

1. [Search and screen for scope relevance](search.md).
2. Read each paper's problem, method, assumptions and evaluation.
3. Write a [critical review](review-template.md) with source locations and limitations.
4. Update the [comparison matrix](synthesis/comparison.csv) and [synthesis](synthesis/findings.md).

[Reference metadata](references.json) contains exactly these five active papers. Prior supporting/excluded notes and unreviewed catalog items are preserved in the [earlier Git snapshot](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/tree/938a07f828909bb2d8f31e271a0b479dd117f562/literature), outside the active list.

## File naming and order

Use the full paper title plus `.md`; replace unsafe punctuation such as a colon with a readable hyphen. Numbers belong in this register and metadata, not filenames. Use encoded destinations for Markdown links containing spaces. Retain internal reference keys/DOIs for identity; current visible serials are consecutive 01-05.

## Research boundary

No algorithm, comparator implementation or simulation matrix is selected. Core relevance is separate from evidence quality or baseline fidelity. Include contrary findings and close methods even when their resource model differs. Do not fill the target with generic IoT applications or loosely related theory.
