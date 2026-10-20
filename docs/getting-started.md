# Getting started

## Requirements

- Python 3.11+
- Docker Compose for the live MQTT demo
- No hardware or external Python packages for the simulation

Run commands from the repository root.

## Simulation

```bash
python -m unittest discover -s tests -v
python -m iot_alerts.experiment --count 10000 --rate 120 --service-ms 10 --seed 42 --output results/run
```

The output directory contains per-event `fifo.csv` and `priority.csv`, `summary.csv` and `config.json`. Use a different directory for each configuration. Priorities are 0 high, 1 medium and 2 low.

To reproduce the three-policy pilot, including fixed aging:

```bash
python -m iot_alerts.pilot --output results/pilot
```

See [pilot evidence](../evidence/pilot/README.md) for assumptions, metrics and reproduction details.

## Live MQTT demo

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
docker compose up -d
python -m iot_alerts.mqtt_demo receive --policy priority
```

On Windows, activate with `.venv\Scripts\activate`. After the receiver prints `Ready`, activate the same environment in another terminal and publish:

```bash
python -m iot_alerts.mqtt_demo publish --count 500
```

The receiver prints each processed event and receiver-local latency. Run one receiver at a time. Restart it with `--policy fifo` to try FIFO. Fixed aging is available in the simulation, not the live receiver.

Stop the receiver with Ctrl+C and remove the broker with `docker compose down`. The broker permits anonymous access and publishes only on localhost for laboratory use. Live integration validation remains pending.

## Diagram sources

Editable [architecture SVG](images/high-level-architecture.svg) and [flow SVG](images/alert-processing-flow.svg) accompany the README images.

After installing Pillow, regenerate both PNG and SVG assets:

```bash
python tools/render_diagrams.py
```

The renderer expects DejaVu Sans fonts in the paths defined in the script.

## Scope and next steps

The simulator models one worker with complete drain. The original experiment CLI and pilot use an unbounded queue; the [foundation runner](simulator-foundation.md) also supports bounded queues and per-event metadata. The live demo uses a bounded queue and synthetic processing. Their latency measurements have different boundaries; neither establishes real hardware end-to-end performance.

Bounded simulation queues and [deadline/loss summaries](deadline-and-loss-metrics.md) are available through the foundation runner. [EDF and four-policy comparison](edf-baseline.md) are also available. Planned work includes the candidate congestion-aware aging policy, broader repeated experiments and controlled MQTT validation. See the [proposal](../docx/IoT_Alert_Processing_Research_Proposal.docx) and [design](design-and-evaluation.md).

A reusable open-source release is planned. Select a license and add contribution guidance before that release.
