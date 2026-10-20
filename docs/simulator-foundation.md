# Simulator foundation

The shared engine runs one worker and one waiting queue. FIFO, strict priority and fixed aging use the same arrival, admission and completion logic. Only the next-event selection changes.

## Run it

```bash
python -m iot_alerts.foundation --policy aging --queue-capacity 10 --service-ms 10 --deadline-ms 100 --output results/foundation
```

The command writes `events.csv` with one outcome for every generated event and `config.json` with settings and basic counts. Completed events have start, finish, waiting and response times. Rejected events have a rejection timestamp and the reason `queue_full`; they have no invented latency.

- Omit `--queue-capacity` for an unbounded waiting queue.
- Use `--queue-capacity 0` for a worker without a waiting buffer.
- Use a positive capacity to limit waiting events. Work currently being processed does not occupy a waiting slot.
- `--aging-ms` sets the fixed aging interval. The original two-policy experiment CLI remains available.

## Event model

| Field | Meaning |
| --- | --- |
| `id` | Unique nonnegative integer within a run |
| `arrival` | Nonnegative simulation time in seconds |
| `priority` | 0 high, 1 medium, 2 low |
| `deadline_s` | Optional positive deadline relative to arrival |
| `service_time_s` | Optional positive processing time; overrides the run default |
| `absolute_deadline_s` | Derived value: arrival plus relative deadline |

Times must be finite. Duplicate IDs and invalid configuration are rejected. API users can give different service times and deadlines to individual events:

```python
from iot_alerts.simulator import Alert, run_simulation

events = [
    Alert(0, 0.0, 2, deadline_s=1.0, service_time_s=0.02),
    Alert(1, 0.01, 0, deadline_s=0.1, service_time_s=0.005),
]
result = run_simulation(events, 'priority', queue_capacity=5)
print(result.completed, result.dropped)
```

Deadlines are metadata in this task. They do not expire events or affect scheduling. EDF and aggregate deadline metrics belong to later tasks. Service is non-preemptive: a new urgent arrival cannot interrupt the worker.

## Exact event ordering

At any timestamp:

1. Complete the event currently in service, if it finishes now.
2. Admit all arrivals at that time in ascending event-ID order.
3. If the worker is idle, select one admitted event to start immediately.

During the arrival batch, an idle worker reserves one service slot in addition to the waiting capacity. This means a capacity of one can admit two simultaneous events when idle, but only one additional event when busy. The reservation is filled by the scheduler after the batch. This convention is identical for all policies.

When capacity is exhausted, reject the arriving event. Priority does not bypass admission or evict queued work. At the exact moment of completion, newly admitted urgent work can compete with older waiting events before dispatch. Equal scheduling keys use arrival order, then event ID.

FIFO selects the oldest admitted event. Strict priority selects the lowest priority value. Aging reduces the effective priority by one for every aging interval waited, down to zero; it recomputes priorities at dispatch. Equal effective priorities use the same arrival ordering.

## Results and compatibility

The engine drains all admitted events after arrivals end. Therefore:

- `generated = completed + dropped`
- `admitted = completed`
- every event appears in exactly one completion or rejection record
- `max_waiting` never exceeds the configured waiting capacity

`run_simulation` returns immutable completion and rejection records. `experiment.simulate` remains an unbounded compatibility adapter with the original per-event CSV schema. The checked-in pilot files are historical evidence and are not rewritten. Re-running the original pilot produces identical run metrics; a new run manifest includes the shared engine source hash.

The model has no broker or network simulation, deadline expiry, processing failures or early observation cutoff. Task 2 will add complete aggregate deadline and loss metrics. The live MQTT path is unchanged.
