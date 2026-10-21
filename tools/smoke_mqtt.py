"""Functional MQTT smoke; uses an isolated broker, never paper performance evidence."""
import argparse
import csv
import json
import shutil
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICIES = ('fifo', 'priority', 'aging', 'edf', 'adaptive_guarded', 'adaptive', 'fixed_guarded', 'fixed_deadline')


def send_extra(host, port, source):
    import paho.mqtt.client as mqtt
    ready = threading.Event()
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = lambda c, u, f, reason, p: ready.set() if not reason.is_failure else None
    try:
        client.connect(host, port, 60)
        client.loop_start()
        if not ready.wait(5):
            raise TimeoutError('Test publisher connection timed out')
        for payload in ('{', '{"id":"invalid","priority":true}',
                        json.dumps(dict(source=source, id='0', priority=1))):
            info = client.publish('lab/alerts', payload, qos=1)
            info.wait_for_publish(timeout=5)
            if not info.is_published():
                raise TimeoutError('Test publisher acknowledgement timed out')
    finally:
        client.disconnect()
        client.loop_stop()


def run_policy(policy, output, host, port):
    ready = threading.Event()
    log = (output/f'{policy}.log').open('w')
    process = subprocess.Popen([sys.executable, '-m', 'iot_alerts.mqtt_demo', 'receive', '--host', host,
        '--port', str(port), '--policy', policy, '--queue-capacity', '100', '--service-ms', '2',
        '--service-estimate-ms', '2', '--duration-s', '3', '--output', str(output/policy)],
        cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    def pump():
        for line in process.stdout:
            log.write(line)
            log.flush()
            if line.startswith('Ready;'):
                ready.set()
    thread = threading.Thread(target=pump, daemon=True)
    thread.start()
    try:
        if not ready.wait(8):
            raise TimeoutError(f'{policy}: receiver not ready; inspect {output/policy}.log')
        publisher = subprocess.run([sys.executable, '-m', 'iot_alerts.mqtt_demo', 'publish', '--host', host,
            '--port', str(port), '--count', '20', '--duplicate-every', '2', '--deadlines-ms', '100', '500', '2000'],
            cwd=ROOT, capture_output=True, text=True, timeout=10, check=True)
        source = json.loads(publisher.stdout)['source']
        send_extra(host, port, source)
        if process.wait(timeout=15) != 0:
            raise RuntimeError(f'{policy}: receiver failed; inspect its log')
        thread.join(2)
        summary = json.loads((output/policy/'summary.json').read_text())
        expected = dict(received_messages=33, admitted=20, completed=20, duplicate_messages=10,
                        invalid_messages=2, identity_conflicts=1, rejected_queue_full=0, unfinished=0)
        if any(summary.get(name) != value for name, value in expected.items()) or not summary['drained']:
            raise AssertionError(f'{policy}: unexpected accounting: {summary}')
        with (output/policy/'completed.csv').open(newline='') as stream:
            rows = list(csv.DictReader(stream))
        if len(rows) != 20 or len({(r['source'], r['id']) for r in rows}) != 20:
            raise AssertionError(f'{policy}: duplicated completion or missing raw rows')
        receipts = [json.loads(line) for line in (output/policy/'receipts.jsonl').read_text().splitlines()]
        if len(receipts) != 33:
            raise AssertionError(f'{policy}: missing receipt records')
        print(f'{policy}: 20 completions, 10 duplicates, 2 invalid, 1 conflict; drained', flush=True)
        return summary
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        thread.join(2)
        if process.stdout:
            process.stdout.close()
        log.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--external-broker', action='store_true', help='Reuse an isolated broker; never starts/stops it')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=18883)
    parser.add_argument('--output', type=Path, default=ROOT/'results/mqtt-smoke')
    args = parser.parse_args()
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=False)
    broker, broker_log = None, None
    try:
        if not args.external_broker:
            executable = shutil.which('mosquitto')
            if executable is None:
                raise RuntimeError('Install Mosquitto or use --external-broker with an isolated local broker')
            if args.host != '127.0.0.1':
                raise ValueError('Managed smoke broker must bind loopback')
            config = args.output/'broker.conf'
            config.write_text(f'listener {args.port} 127.0.0.1\nallow_anonymous true\npersistence false\n')
            broker_log = (args.output/'broker.log').open('w')
            broker = subprocess.Popen([executable, '-c', str(config)], stdout=broker_log, stderr=subprocess.STDOUT)
        end = time.monotonic()+5
        while True:
            if broker is not None and broker.poll() is not None:
                raise RuntimeError('Managed broker exited before readiness; inspect broker.log')
            try:
                with socket.create_connection((args.host, args.port), timeout=.2):
                    break
            except OSError:
                if time.monotonic() >= end:
                    raise TimeoutError('Broker not available')
                time.sleep(.05)
        summaries = {p: run_policy(p, args.output, args.host, args.port) for p in POLICIES}
        (args.output/'smoke-summary.json').write_text(json.dumps(dict(
            evidence='functional smoke only; not comparative performance evidence',
            duplicates='deliberate same-ID publishes, not forced MQTT retransmissions',
            broker='external' if args.external_broker else 'mosquitto', policies=summaries), indent=2)+'\n')
    finally:
        if broker is not None:
            broker.terminate()
            try:
                broker.wait(timeout=3)
            except subprocess.TimeoutExpired:
                broker.kill()
                broker.wait()
        if broker_log is not None:
            broker_log.close()


if __name__ == '__main__':
    main()
