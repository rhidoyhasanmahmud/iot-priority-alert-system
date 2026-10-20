# IoT Priority Alert System

A reproducible framework for exploring how scheduling decisions affect urgent IoT alerts and routine event processing under congestion.

The project combines a local MQTT demonstration with a deterministic experiment runner. Its research direction is to study deadline performance and waiting-time tradeoffs using strong baselines and controlled workloads.

## Research proposal

Read the [research proposal](docx/IoT_Alert_Processing_Research_Proposal.docx) for the problem, research questions, candidate policy, experiment design and delivery plan. The proposal describes planned work; it does not report measured improvements or establish algorithmic novelty.

## Implementation status

| Component | Status |
| --- | --- |
| FIFO and non-preemptive strict priority | Implemented in the simulator and MQTT demo |
| Seeded arrivals and per-event CSV output | Implemented in the simulator |
| Local MQTT publisher and receiver | Implemented; live integration validation pending |
| Automated scheduling tests | Implemented |
| Fixed aging and earliest deadline first | Planned |
| Congestion-aware aging candidate | Proposed for investigation |
| Deadlines, bounded simulation queues and loss accounting | Planned |
| Repeated experiment matrix, ablations and confidence intervals | Planned |

Python 3.11+; no hardware required for the initial prototype.

## Reproducible experiment

No external dependencies required:

```bash
python -m unittest discover -s tests -v
python -m iot_alerts.experiment --count 10000 --rate 120 --service-ms 10 --seed 42 --output results/rate120-seed42
```

Open `summary.csv` in the output directory. Raw per-event results are in `fifo.csv` and `priority.csv`; `config.json` records the parameters. Use a unique output directory per run. Priorities: 0 high, 1 medium, 2 low.

## Live MQTT demonstration

Docker Compose is required for the broker:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
docker compose up -d
python -m iot_alerts.mqtt_demo receive --policy priority
```

After the receiver prints `Ready`, in a second terminal with the same virtual environment activated:

```bash
python -m iot_alerts.mqtt_demo publish --count 500
```

Stop the receiver with Ctrl+C. To try FIFO, restart it using `--policy fifo` and publish again. Run one receiver at a time. These live runs use real timing and are not paired experiments. Cleanup: `docker compose down`.

On Windows activate the virtual environment using `.venv\Scripts\activate` instead. The broker allows anonymous access for local laboratory use only; its published port is bound to localhost.

## Scope and evidence

- Implemented: seeded sensor workload, FIFO/priority simulation, raw CSV metrics, local MQTT demo and CI tests.
- The simulation measures modeled response latency; the demo measures receiver-local latency. Neither establishes real hardware end-to-end performance.
- Priority may help urgent events while increasing low-priority waiting. It does not increase server capacity or detect cyberattacks.
- See [design and evaluation](docs/design-and-evaluation.md) for the research question, experiment protocol, limitations and semester milestones.


## Roadmap

1. Verify related work and refine the contribution.
2. Add deadlines, bounded queues, complete event accounting and stronger baselines.
3. Evaluate the candidate policy against fixed aging and earliest deadline first.
4. Validate selected scenarios in a controlled MQTT testbed.
5. Publish reproducible findings and prepare the repository for an open-source release.

A reusable open-source release is planned. A license and contribution guidelines will be added before that release; no license is granted by this roadmap.
