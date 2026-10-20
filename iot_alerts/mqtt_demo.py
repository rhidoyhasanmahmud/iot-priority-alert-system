"""Local MQTT demonstration. Run receiver before publisher."""
import argparse
import json
import queue
import threading
import time
import uuid
import paho.mqtt.client as mqtt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('role', choices=['receive', 'publish'])
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--policy', choices=['fifo', 'priority'], default='priority')
    parser.add_argument('--count', type=int, default=100)
    args = parser.parse_args()
    if args.count < 1:
        parser.error('count must be positive')
    pending = queue.PriorityQueue(maxsize=10000)
    ready = threading.Event()
    subscribed = threading.Event()
    sequence = 0
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    def connected(client, userdata, flags, reason, properties):
        if reason.is_failure:
            return
        if args.role == 'receive':
            client.subscribe('lab/alerts', qos=1)
        ready.set()

    def on_subscribe(client, userdata, mid, reasons, properties):
        if reasons and all(not r.is_failure for r in reasons):
            subscribed.set()

    def received(client, userdata, message):
        nonlocal sequence
        try:
            event = json.loads(message.payload)
            priority = event['priority']
            if type(priority) is not int or priority not in (0, 1, 2) or not isinstance(event['id'], str):
                raise ValueError('invalid event')
            pending.put_nowait((priority if args.policy == 'priority' else 0,
                                sequence, time.monotonic(), event))
            sequence += 1
        except (ValueError, KeyError, TypeError, queue.Full):
            print('Rejected invalid event or full queue', flush=True)

    client.on_connect = connected
    client.on_subscribe = on_subscribe
    client.on_message = received
    client.connect(args.host, 1883, 60)
    client.loop_start()
    try:
        if not ready.wait(10):
            raise TimeoutError('Broker connection not ready')
        if args.role == 'publish':
            run = uuid.uuid4().hex
            for index in range(args.count):
                event = dict(id=f'{run}-{index}', priority=0 if index % 10 == 0 else 2)
                client.publish('lab/alerts', json.dumps(event), qos=1).wait_for_publish(timeout=10)
        else:
            if not subscribed.wait(10):
                raise TimeoutError('Subscription not ready')
            print('Ready; publish alerts in another terminal. Ctrl+C to stop.', flush=True)
            while True:
                try:
                    _, _, arrival, event = pending.get(timeout=1)
                except queue.Empty:
                    continue
                time.sleep(.02)  # synthetic processing cost; non-preemptive
                print(json.dumps(dict(**event, local_latency_ms=(time.monotonic()-arrival)*1000)), flush=True)
    except KeyboardInterrupt:
        pass
    finally:
        client.disconnect()
        client.loop_stop()


if __name__ == '__main__':
    main()
