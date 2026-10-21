"""Local MQTT demonstration with one draining processing worker."""
import argparse
import csv
import hashlib
import platform
import json
import threading
import time
import uuid
from pathlib import Path

from .live import LiveProcessor, POLICIES, parse_payload
from .scheduling import AgingConfig
from .simulator import positive

TOPIC = 'lab/alerts'


def publish(client, count, *, deadlines=None, duplicate_every=0):
    source = uuid.uuid4().hex
    attempts = 0
    for index in range(count):
        priority = 0 if index % 10 == 0 else 2
        event = dict(source=source, id=str(index), priority=priority)
        if deadlines is not None:
            event['deadline_ms'] = deadlines[priority]
        parse_payload(json.dumps(event))
        for _ in range(2 if duplicate_every and (index+1) % duplicate_every == 0 else 1):
            info = client.publish(TOPIC, json.dumps(event), qos=1)
            info.wait_for_publish(timeout=10)
            if not info.is_published():
                raise TimeoutError('Publish acknowledgement timed out')
            attempts += 1
    return dict(source=source, unique_events=count, publish_attempts=attempts)


def receive(client, args, processor, subscribed):
    args.output.mkdir(parents=True, exist_ok=False)
    config = vars(args) | dict(output=str(args.output), topic=TOPIC, qos=1,
        measurement='receiver callback entry to completion; monotonic clock; excludes network',
        deadlines='relative to receiver callback entry; publisher metadata is untrusted',
        dedup='source + id; pinned pending/active IDs plus bounded completion-time TTL cache',
        service_estimate_ms=args.service_estimate_ms,
        python=platform.python_version(),
        source_sha256={name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                       for name in ('live.py', 'mqtt_demo.py', 'simulator.py', 'scheduling.py')},
        policies_share_selector=True, timestamp_order='real callback/worker interleaving; no simulated arrival batches')
    (args.output/'config.json').write_text(json.dumps(config, indent=2)+'\n')
    failed, errors = threading.Event(), []
    with (args.output/'receipts.jsonl').open('w') as receipts, (args.output/'completed.csv').open('w', newline='') as completed, (args.output/'lifecycle.jsonl').open('w') as lifecycle:
        fields = ['source', 'id', 'priority', 'deadline_ms', 'sequence', 'status', 'arrival_s', 'start_s',
                  'finish_s', 'absolute_deadline_s', 'deadline_status', 'wait_ms', 'local_latency_ms', 'service_ms']
        writer = csv.DictWriter(completed, fieldnames=fields, lineterminator='\n')
        writer.writeheader()

        def record_lifecycle(event, **details):
            try:
                lifecycle.write(json.dumps(dict(event=event, local_s=processor.now(), **details))+'\n')
                lifecycle.flush()
            except BaseException as error:
                errors.append(repr(error))
                failed.set()

        def connected(client, userdata, flags, reason, properties):
            success = not reason.is_failure
            record_lifecycle('connected', success=success, reason=str(reason))
            if success:
                result, _ = client.subscribe(TOPIC, qos=1)
                if result != 0:
                    errors.append(f'Subscribe failed: {result}')
                    failed.set()

        def on_subscribe(client, userdata, mid, reasons, properties):
            success = bool(reasons) and all(not reason.is_failure for reason in reasons)
            record_lifecycle('subscribed', success=success, reasons=[str(r) for r in reasons])
            if success:
                subscribed.set()

        def disconnected(client, userdata, flags, reason, properties):
            subscribed.clear()
            record_lifecycle('disconnected', reason=str(reason))

        client.on_connect = connected
        client.on_subscribe = on_subscribe
        client.on_disconnect = disconnected

        def received(client, userdata, message):
            try:
                receipt = processor.ingest(message.payload)
                receipts.write(json.dumps(receipt, allow_nan=False)+'\n')
                receipts.flush()
            except BaseException as error:
                errors.append(repr(error))
                failed.set()

        def worker():
            try:
                while (item := processor.take()) is not None:
                    time.sleep(args.service_ms/1000)
                    row = processor.complete(item)
                    writer.writerow(row)
                    completed.flush()
                    print(json.dumps(row, allow_nan=False), flush=True)
            except BaseException as error:
                errors.append(repr(error))
                failed.set()

        client.on_message = received
        thread = threading.Thread(target=worker, name='alert-worker')
        thread.start()
        reason = 'duration' if args.duration_s is not None else 'interrupt'
        try:
            client.connect(args.host, args.port, 60)
            client.loop_start()
            if not subscribed.wait(10):
                raise TimeoutError('Subscription not ready')
            print('Ready; publish alerts in another terminal. Ctrl+C to drain and stop.', flush=True)
            if args.duration_s is None:
                while not failed.wait(.2):
                    pass
            else:
                failed.wait(args.duration_s)
            if failed.is_set():
                raise RuntimeError('Processing worker failed')
        except KeyboardInterrupt:
            reason = 'interrupt'
        except BaseException:
            reason = 'error'
            raise
        finally:
            # Stop callbacks before closing admission; then finish all admitted work.
            client.disconnect()
            client.loop_stop()
            processor.close()
            thread.join()
            summary = processor.snapshot() | dict(stop_reason=reason, worker_errors=errors,
                drained=processor.snapshot()['unfinished'] == 0,
                counters='message attempts; duplicates/conflicts/full-queue retries are separate categories')
            (args.output/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
        if errors:
            raise RuntimeError(f'Processing failed: {errors[0]}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('role', choices=['receive', 'publish'])
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', type=int, default=1883)
    parser.add_argument('--policy', choices=POLICIES, default='priority')
    parser.add_argument('--count', type=int, default=100)
    parser.add_argument('--queue-capacity', type=int, default=10000)
    parser.add_argument('--service-ms', type=float, default=20)
    parser.add_argument('--aging-ms', type=float, default=100)
    parser.add_argument('--aging-min-ms', type=float, default=100)
    parser.add_argument('--aging-max-ms', type=float, default=1000)
    parser.add_argument('--service-estimate-ms', type=float, default=20)
    parser.add_argument('--dedup-capacity', type=int, default=10000)
    parser.add_argument('--dedup-ttl-s', type=float, default=60)
    parser.add_argument('--duration-s', type=float, help='Receive for this duration after SUBACK, then drain')
    parser.add_argument('--deadlines-ms', nargs=3, type=float, metavar=('HIGH', 'MEDIUM', 'LOW'))
    parser.add_argument('--duplicate-every', type=int, default=0, help='Republish every Nth event with the same ID')
    parser.add_argument('--output', type=Path, default=Path('results/live'))
    args = parser.parse_args()
    try:
        if args.count < 1 or not 1 <= args.port <= 65535 or args.duplicate_every < 0:
            raise ValueError('Invalid count, port or duplicate interval')
        positive(args.service_ms, 'service-ms')
        if args.duration_s is not None:
            positive(args.duration_s, 'duration-s')
        for value in args.deadlines_ms or []:
            positive(value, 'deadlines-ms')
        config = AgingConfig(args.aging_min_ms/1000, args.aging_max_ms/1000, args.service_estimate_ms/1000)
        processor = LiveProcessor(args.policy, capacity=args.queue_capacity, aging_interval=args.aging_ms/1000,
            aging_config=config, dedup_capacity=args.dedup_capacity, dedup_ttl=args.dedup_ttl_s)
    except ValueError as error:
        parser.error(str(error))
    import paho.mqtt.client as mqtt
    subscribed, ready = threading.Event(), threading.Event()
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    def connected(client, userdata, flags, reason, properties):
        if not reason.is_failure:
            if args.role == 'receive':
                client.subscribe(TOPIC, qos=1)
            ready.set()

    def on_subscribe(client, userdata, mid, reasons, properties):
        if reasons and all(not reason.is_failure for reason in reasons):
            subscribed.set()

    client.on_connect, client.on_subscribe = connected, on_subscribe
    if args.role == 'receive':
        receive(client, args, processor, subscribed)
    else:
        try:
            client.connect(args.host, args.port, 60)
            client.loop_start()
            if not ready.wait(10):
                raise TimeoutError('Broker connection not ready')
            print(json.dumps(publish(client, args.count, deadlines=args.deadlines_ms,
                                     duplicate_every=args.duplicate_every)), flush=True)
        finally:
            client.disconnect()
            client.loop_stop()


if __name__ == '__main__':
    main()
