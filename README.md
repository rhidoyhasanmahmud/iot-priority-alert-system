# IoT Priority Alert System

Bachelor-level experimental prototype for comparing FIFO and non-preemptive strict priority scheduling of IoT alerts. Python 3.11+; no hardware required.

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
