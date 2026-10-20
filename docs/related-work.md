# Related work and contribution assessment

Verified on 20 October 2026. This is a focused review, not a systematic literature review. Bibliographic verification is separate from full-text appraisal. No journal quartile or indexing claim is made.

## Comparison matrix

| ID | Year | Decision location and method | Relevance and proposed distinction | Evidence available |
| --- | --- | --- | --- | --- |
| R1 | 2024 | Prioritizes time-critical traffic using a UDP-based MQTT extension. | Transport and protocol intervention; our queue is after delivery. No direct performance comparison is valid without matching the network model. | Publisher abstract and metadata; author repository abstract |
| R2 | 2024 | RabbitMQ virtual queues distinguish urgent, critical and FCFS messages. | Shows that emergency priority queues already exist. We will examine routine waiting and repeated overload rather than claim priority support itself as new. | Full publisher text |
| R3 | 2024 | Combines selective transmission and urgent-message processing in HBMQTT. | Traffic suppression changes the offered workload; our initial comparisons keep identical input traces. Full text is needed before making absence claims. | Publisher abstract and metadata |
| R4 | 2024 | Explores integrating PrioMQTT with TSN for traffic with diverse timing needs. | Network support matters for timing bounds. We make no network-level deadline guarantee from an application queue. | Publisher abstract and indexed first-page author text |
| R5 | 2022 | Maps application timing requirements to SDN resource reservations. | A broader architecture than our worker queue. Its treatment of ordinary-traffic cost motivates reporting both event classes. | Full author article in PMC, with publisher DOI |
| R6 | 2023 | Derives worst-case response-time analysis for an SDN-based MQTT architecture. | A formal guarantee requires an explicit analyzable model. Our initial results are empirical finite-workload measurements. | Publisher abstract and complete bibliographic record |
| R7 | 2019 | Modifies Mosquitto for urgent message delivery. | Prior art for broker-level urgency. Detailed algorithm and evaluation limitations remain unassessed because full text was unavailable. | Publisher title and indexed first-page author text; bibliographic cross-check in R2 |
| R8 | 2026 | TRIAGE/4 combines semantic alarm priority and device fairness with simulation and an MQTT prototype. | Closest conceptual overlap: alarm latency and fairness are already studied. Any novelty claim needs a full comparison with this method, not just FIFO and strict priority. | Publisher abstract and metadata; author publication list confirms authors |

## Defensible research question

For a bounded, non-preemptive application worker after MQTT delivery, does occupancy-dependent aging produce a better urgent-deadline versus routine-waiting tradeoff than tuned fixed aging and EDF, once losses and policy overhead are included?

This is a candidate empirical gap, not proof that nobody has studied it. R8 already studies alarm responsiveness and fairness. A different queue location or application label alone is not sufficient novelty. Before freezing the algorithm, obtain the closest full texts, search their references and citing work, and either reproduce a relevant policy or explain precisely why its model cannot be compared directly.

## Go or revise decision

Continue toward an algorithm paper only if the candidate has a distinct decision rule or demonstrated operating insight beyond existing approaches, and improves held-out tradeoffs against tuned baselines. Otherwise narrow to a distinctive empirical study or redesign the policy. Do not describe this preliminary review as establishing novelty.

## Complete references

### R1
Gaetano Patti; Luca Leonardi; Giuseppe Testa; Lucia Lo Bello. 2024. **PrioMQTT: A prioritized version of the MQTT protocol**. Computer Communications, 220, 43–51. Publisher: Elsevier. DOI: [10.1016/j.comcom.2024.03.018](https://doi.org/10.1016/j.comcom.2024.03.018).
Relevance: Prioritizes time-critical traffic using a UDP-based MQTT extension. Transport and protocol intervention; our queue is after delivery. No direct performance comparison is valid without matching the network model.
Verification: Publisher abstract and metadata; author repository abstract. [Official source](https://www.sciencedirect.com/science/article/pii/S0140366424001105).

### R2
P S Akshatha; S Divyashree; S M Dilip Kumar. 2024. **Priority-enabled MQTT: a robust approach to emergency event messaging**. Journal of Engineering and Applied Science, 71, article 67. Publisher: Springer Nature. DOI: [10.1186/s44147-024-00400-2](https://doi.org/10.1186/s44147-024-00400-2).
Relevance: RabbitMQ virtual queues distinguish urgent, critical and FCFS messages. Shows that emergency priority queues already exist. We will examine routine waiting and repeated overload rather than claim priority support itself as new.
Verification: Full publisher text. [Official source](https://link.springer.com/article/10.1186/s44147-024-00400-2).

### R3
Jiby J. Puthiyidam; Shelbi Joseph. 2024. **PR-MQTT: a novel approach for traffic reduction and message prioritisation in IoT applications**. International Journal of Web Engineering and Technology, 19(1), 44–66. Publisher: Inderscience. DOI: [10.1504/IJWET.2024.138096](https://doi.org/10.1504/IJWET.2024.138096).
Relevance: Combines selective transmission and urgent-message processing in HBMQTT. Traffic suppression changes the offered workload; our initial comparisons keep identical input traces. Full text is needed before making absence claims.
Verification: Publisher abstract and metadata. [Official source](https://www.inderscience.com/info/inarticle.php?artid=138096).

### R4
Giuseppe Testa; Luca Leonardi; Lucia Lo Bello; Gaetano Patti. 2024. **Towards Integrating MQTT with Time-Sensitive Networking**. 2024 IEEE 29th International Conference on Emerging Technologies and Factory Automation (ETFA). Publisher: IEEE. DOI: [10.1109/ETFA61755.2024.10710933](https://doi.org/10.1109/ETFA61755.2024.10710933).
Relevance: Explores integrating PrioMQTT with TSN for traffic with diverse timing needs. Network support matters for timing bounds. We make no network-level deadline guarantee from an application queue.
Verification: Publisher abstract and indexed first-page author text. [Official source](https://ieeexplore.ieee.org/document/10710933/).

### R5
Ehsan Shahri; Paulo Pedreiras; Luis Almeida. 2022. **Extending MQTT with Real-Time Communication Services Based on SDN**. Sensors, 22(9), article 3162. Publisher: MDPI. DOI: [10.3390/s22093162](https://doi.org/10.3390/s22093162).
Relevance: Maps application timing requirements to SDN resource reservations. A broader architecture than our worker queue. Its treatment of ordinary-traffic cost motivates reporting both event classes.
Verification: Full author article in PMC, with publisher DOI. [Official source](https://www.mdpi.com/1424-8220/22/9/3162).

### R6
Ehsan Shahri; Paulo Pedreiras; Luis Almeida. 2023. **Response Time Analysis for RT-MQTT Protocol Grounded on SDN**. Fourth Workshop on Next Generation Real-Time Embedded Systems (NG-RES 2023), OASIcs 108, 5:1–5:15. Publisher: Schloss Dagstuhl – Leibniz-Zentrum für Informatik. DOI: [10.4230/OASIcs.NG-RES.2023.5](https://doi.org/10.4230/OASIcs.NG-RES.2023.5).
Relevance: Derives worst-case response-time analysis for an SDN-based MQTT architecture. A formal guarantee requires an explicit analyzable model. Our initial results are empirical finite-workload measurements.
Verification: Publisher abstract and complete bibliographic record. [Official source](https://drops.dagstuhl.de/entities/document/10.4230/OASIcs.NG-RES.2023.5).

### R7
Kitae Hwang; Jae Moon Lee; In Hwan Jung; Dong-Hee Lee. 2019. **Modification of Mosquitto Broker for Delivery of Urgent MQTT Message**. 2019 IEEE Eurasia Conference on IOT, Communication and Engineering (ECICE), 166–167. Publisher: IEEE. DOI: [10.1109/ECICE47484.2019.8942800](https://doi.org/10.1109/ECICE47484.2019.8942800).
Relevance: Modifies Mosquitto for urgent message delivery. Prior art for broker-level urgency. Detailed algorithm and evaluation limitations remain unassessed because full text was unavailable.
Verification: Publisher title and indexed first-page author text; bibliographic cross-check in R2. [Official source](https://ieeexplore.ieee.org/document/8942800/).

### R8
João Carlos N. Bittencourt; Paulo Portugal; Francisco Vasques; Daniel G. Costa. 2026. **Multi-Tier Message Scheduling for IoT-Based Urban Emergency Systems Through Semantic Priority Override**. IEEE Access, 14, 140988–141015. Publisher: IEEE. DOI: [10.1109/ACCESS.2026.3732592](https://doi.org/10.1109/ACCESS.2026.3732592).
Relevance: TRIAGE/4 combines semantic alarm priority and device fairness with simulation and an MQTT prototype. Closest conceptual overlap: alarm latency and fairness are already studied. Any novelty claim needs a full comparison with this method, not just FIFO and strict priority.
Verification: Publisher abstract and metadata; author publication list confirms authors. [Official source](https://ieeexplore.ieee.org/document/11685955/).
