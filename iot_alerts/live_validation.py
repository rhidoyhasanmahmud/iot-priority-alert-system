"""Registered POSIX loopback validation, planned replay and raw evidence checks."""
import argparse
import csv
from contextlib import ExitStack
import importlib.metadata
import itertools
import json
import math
from collections import Counter
import random
import shutil
import signal
import statistics
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

from .experiment import write_csv
from .metrics import summarize
from .simulator import Alert, Completion, Rejection, SimulationResult
from .study import ROOT, digest, file_hash, provenance, read_json, seal, source_identity, verify, write_json
from .workloads import generate_workload, load_trace, save_trace, trace_fingerprint

PROTOCOL = ROOT/'configs/live-validation-v1.json'


def json_lines(path):
    """A concurrent reader waits for the final newline; malformed complete rows fail."""
    if not path.exists():
        return []
    data = path.read_text()
    lines = data.splitlines()
    if data and not data.endswith('\n'):
        lines = lines[:-1]
    return [json.loads(line) for line in lines]


def wait_for(predicate, timeout=10):
    end = time.monotonic()+timeout
    while not predicate():
        if time.monotonic() >= end:
            raise TimeoutError('Validation condition timed out')
        time.sleep(.02)


def register(output, profile='smoke', broker='mosquitto', port=18884):
    if profile not in ('smoke', 'validation') or broker not in ('mosquitto', 'amqtt') or type(port) is not int or not 1024 <= port <= 65535:
        raise ValueError('Invalid profile, broker or unprivileged port')
    protocol = read_json(PROTOCOL)
    plan = protocol | protocol['profiles'][profile] | dict(profile=profile, broker=broker, port=port)
    plan.pop('profiles')
    plan['scenarios'] = [dict(id=f's{i:03d}', rate=rate, traffic=traffic)
                         for i, (rate, traffic) in enumerate(itertools.product(plan['rates'], plan['traffic']))]
    orders = []
    for scenario in plan['scenarios']:
        for seed in plan['seeds']:
            policies = list(plan['policies'])
            random.Random(f'{scenario["id"]}:{seed}:live-order').shuffle(policies)
            orders.append(dict(scenario_id=scenario['id'], seed=seed, policies=policies))
    plan['execution_order'] = orders
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    traces = {}
    (output/'traces').mkdir()
    for order in orders:
        scenario = next(s for s in plan['scenarios'] if s['id'] == order['scenario_id'])
        events = generate_workload(plan['count'], scenario['rate'], order['seed'], traffic=scenario['traffic'],
            priority_weights=plan['priority_weights'], service_time=plan['service_ms']/1000,
            deadlines=tuple(d/1000 for d in plan['deadlines_ms']))
        name = f'traces/{scenario["id"]}-{order["seed"]}.csv'
        save_trace(output/name, events)
        traces[name] = dict(file_sha256=file_hash(output/name), workload_sha256=trace_fingerprint(events))
    write_json(output/'plan.json', plan)
    identity = provenance()
    write_json(output/'registration.json', dict(plan_sha256=digest(plan), traces=traces, provenance=identity,
        workload_runs=len(orders)*len(plan['policies'])))
    for name in identity['source']['files']:
        target = output/'source_snapshot'/name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT/name).read_bytes())
    return plan


def load_plan(output, *, executing=False):
    plan, registration = read_json(output/'plan.json'), read_json(output/'registration.json')
    if digest(plan) != registration['plan_sha256']:
        raise ValueError('Live plan checksum mismatch')
    for name, expected in registration['provenance']['source']['files'].items():
        if file_hash(output/'source_snapshot'/name) != expected:
            raise ValueError('Live source snapshot checksum mismatch')
    for name, expected in registration['traces'].items():
        if file_hash(output/name) != expected['file_sha256'] or trace_fingerprint(load_trace(output/name)) != expected['workload_sha256']:
            raise ValueError('Planned live trace checksum mismatch')
    if executing and source_identity() != registration['provenance']['source']:
        raise ValueError('Live source/Python changed after registration')
    return plan, registration


class Broker:
    def __init__(self, plan, output):
        self.plan, self.output, self.process, self.log = plan, output, None, None

    def start(self):
        port = self.plan['port']
        if self.plan['broker'] == 'mosquitto':
            executable = shutil.which('mosquitto')
            if executable is None:
                raise ValueError('Mosquitto is unavailable; install it or register --broker amqtt')
            config = self.output/'broker.conf'
            config.write_text(f'listener {port} 127.0.0.1\nallow_anonymous true\npersistence false\n')
            command = [executable, '-c', str(config)]
        else:
            importlib.metadata.version('amqtt')
            command = [sys.executable, '-m', 'iot_alerts.validation_broker', '--port', str(port)]
        self.log = (self.output/'broker.log').open('a')
        self.process = subprocess.Popen(command, cwd=ROOT, stdout=self.log, stderr=subprocess.STDOUT)
        def available():
            if self.process.poll() is not None:
                raise RuntimeError('Owned validation broker exited; inspect broker.log')
            try:
                with socket.create_connection(('127.0.0.1', port), timeout=.2):
                    return True
            except OSError:
                return False
        wait_for(available)

    def stop(self):
        if self.process is not None and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
        if self.log is not None:
            self.log.close()
        self.process, self.log = None, None


class Receiver:
    def __init__(self, plan, policy, output, *, capacity=None, service_ms=None):
        self.output = output
        output.mkdir(parents=True)
        self.log = (output/'receiver.log').open('w')
        command = [sys.executable, '-m', 'iot_alerts.mqtt_demo', 'receive', '--host', '127.0.0.1',
            '--port', str(plan['port']), '--policy', policy, '--queue-capacity', str(plan['capacity'] if capacity is None else capacity),
            '--service-ms', str(plan['service_ms'] if service_ms is None else service_ms),
            '--service-estimate-ms', str(plan['service_estimate_ms']), '--aging-ms', str(plan['aging_ms']),
            '--aging-min-ms', str(plan['aging_min_ms']), '--aging-max-ms', str(plan['aging_max_ms']),
            '--dedup-ttl-s', str(plan['dedup_ttl_s']), '--dedup-capacity', str(plan['dedup_capacity']),
            '--output', str(output/'receiver')]
        self.process = subprocess.Popen(command, cwd=ROOT, stdout=self.log, stderr=subprocess.STDOUT)

    def lifecycle(self):
        return json_lines(self.output/'receiver/lifecycle.jsonl')

    def receipts(self):
        return json_lines(self.output/'receiver/receipts.jsonl')

    def ready(self, count=1):
        def subscribed():
            if self.process.poll() is not None:
                raise RuntimeError('Receiver exited before readiness; inspect receiver.log')
            return sum(r['event'] == 'subscribed' and r.get('success') for r in self.lifecycle()) >= count
        wait_for(subscribed)

    def stop(self, timeout=15):
        if self.process.poll() is None:
            self.process.send_signal(signal.SIGINT)
        try:
            code = self.process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait()
            raise TimeoutError('Receiver failed to drain')
        finally:
            self.log.close()
        if code != 0:
            raise RuntimeError('Receiver failed; inspect receiver.log and summary')


class Publisher:
    def __init__(self, port, journal=None):
        import paho.mqtt.client as mqtt
        self.ready, self.lock = threading.Event(), threading.Lock()
        self.origin, self.ack, self.rows, self.infos = time.monotonic(), {}, [], []
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.files = ExitStack()
        self.attempt_stream, self.ack_stream = None, None
        if journal is not None:
            journal.mkdir(parents=True, exist_ok=False)
            self.attempt_stream = self.files.enter_context((journal/'attempts.jsonl').open('w'))
            self.ack_stream = self.files.enter_context((journal/'acks.jsonl').open('w'))
            write_json(journal/'connection.json', dict(monotonic_origin_s=self.origin, clock='time.monotonic'))
        self.client.on_connect = lambda c, u, f, r, p: self.ready.set() if not r.is_failure else None
        def acknowledged(client, userdata, mid, reason, properties):
            with self.lock:
                self.ack[mid] = time.monotonic()-self.origin
                if self.ack_stream is not None:
                    self.ack_stream.write(json.dumps(dict(mid=mid, ack_s=self.ack[mid]))+'\n')
                    self.ack_stream.flush()
        self.client.on_publish = acknowledged
        try:
            self.client.connect('127.0.0.1', port, 60)
            self.client.loop_start()
            if not self.ready.wait(5):
                raise TimeoutError('Controlled publisher not ready')
        except BaseException:
            self.close()
            raise

    def send(self, wire, planned_s=0):
        issued = time.monotonic()-self.origin
        info = self.client.publish('lab/alerts', json.dumps(wire), qos=1)
        if info.rc != 0:
            raise RuntimeError(f'Publish enqueue failed: {info.rc}')
        self.rows.append(dict(**wire, planned_s=planned_s, issued_s=issued, publish_return_s=time.monotonic()-self.origin,
                              drift_ms=(issued-planned_s)*1000, mid=info.mid))
        if self.attempt_stream is not None:
            self.attempt_stream.write(json.dumps(self.rows[-1])+'\n')
            self.attempt_stream.flush()
        self.infos.append(info)

    def collect(self):
        for info in self.infos:
            info.wait_for_publish(timeout=5)
            if not info.is_published():
                raise TimeoutError('Missing publisher acknowledgement')
        with self.lock:
            rows = [r | dict(ack_s=self.ack.get(r['mid'])) for r in self.rows]
        if any(r['ack_s'] is None for r in rows):
            raise ValueError('Missing ACK timing record')
        return rows

    def close(self):
        try:
            self.client.disconnect()
        finally:
            try:
                self.client.loop_stop()
            finally:
                self.files.close()


def replay(plan, events, source, delivered=None, journal=None):
    publisher = Publisher(plan['port'], journal)
    try:
        start = time.monotonic()
        offset = start-publisher.origin
        for index, event in enumerate(events):
            remaining = start+event.arrival-time.monotonic()
            if remaining > 0:
                time.sleep(remaining)
            wire = dict(source=source, id=str(event.id), priority=event.priority, deadline_ms=event.deadline_s*1000)
            publisher.send(wire, offset+event.arrival)
            if plan['duplicate_every'] and (index+1) % plan['duplicate_every'] == 0:
                publisher.send(wire, offset+event.arrival)
        attempts = publisher.collect()
        if delivered is not None:
            wait_for(lambda: delivered(len(attempts)))
        return attempts
    finally:
        publisher.close()


def reconcile(events, source, receipts, completions, summary, policy):
    """Logical population uses first receiver receipt, including rejected attempts."""
    expected = {str(event.id): event for event in events}
    grouped = {key: [] for key in expected}
    for receipt in receipts:
        arrival = receipt['arrival_s']
        if isinstance(arrival, bool) or not isinstance(arrival, (int, float)) or not math.isfinite(arrival) or arrival < 0:
            raise ValueError('Invalid receipt time')
        if (receipt['status'], receipt['reason']) not in {('admitted', ''), ('duplicate', 'already_seen'), ('rejected', 'queue_full')}:
            raise ValueError('Unexpected receipt classification for controlled valid input')
        if receipt.get('source') != source or receipt.get('id') not in expected:
            raise ValueError('Unexpected receiver identity')
        event = expected[receipt['id']]
        if receipt['priority'] != event.priority or receipt['deadline_ms'] != event.deadline_s*1000:
            raise ValueError('Receiver metadata differs from planned input')
        grouped[receipt['id']].append(receipt)
    if any(not group for group in grouped.values()):
        raise ValueError('Logical events missing at receiver; do not claim complete loss accounting')
    completed = {}
    for row in completions:
        if row['source'] != source or row['id'] not in expected or row['id'] in completed:
            raise ValueError('Unexpected or duplicate completion')
        completed[row['id']] = row
    result_completions, drops = [], []
    for key, event in expected.items():
        group = grouped[key]
        first = min(r['arrival_s'] for r in group)
        admitted = [r for r in group if r['status'] == 'admitted']
        if len(admitted) > 1:
            raise ValueError('Logical event admitted more than once')
        local = Alert(event.id, first, event.priority, event.deadline_s)
        if key in completed:
            row = completed[key]
            if not admitted or float(row['arrival_s']) != admitted[0]['arrival_s']:
                raise ValueError('Completion has no matching admitted receipt')
            start, finish, arrival = float(row['start_s']), float(row['finish_s']), float(row['arrival_s'])
            if (not all(math.isfinite(t) for t in (start, finish, arrival)) or
                    not first <= arrival <= start <= finish or int(row['priority']) != event.priority
                    or float(row['deadline_ms']) != event.deadline_s*1000
                    or int(row['sequence']) != admitted[0]['sequence']):
                raise ValueError('Invalid completion metadata or timestamps')
            for field, expected_ms in (('wait_ms', (start-arrival)*1000), ('service_ms', (finish-start)*1000),
                                       ('local_latency_ms', (finish-arrival)*1000)):
                if not math.isclose(float(row[field]), expected_ms, rel_tol=1e-10, abs_tol=1e-8):
                    raise ValueError('Completion timing metric differs from raw timestamps')
            result_completions.append(Completion(local, start, finish, 0))
        else:
            if admitted or any(r['reason'] != 'queue_full' for r in group):
                raise ValueError('Admitted/invalid event missing completion')
            drops.append(Rejection(local, first))
    categories = Counter((r['status'], r['reason']) for r in receipts)
    if (summary['duplicate_messages'] != categories[('duplicate', 'already_seen')] or
            summary['rejected_queue_full'] != categories[('rejected', 'queue_full')] or
            summary['admitted'] != categories[('admitted', '')]):
        raise ValueError('Message attempt counters differ from receipt classifications')
    if (not summary['drained'] or summary['unfinished'] or summary['worker_errors'] or
            summary['completed'] != len(completed) or summary['admitted'] != len(completed) or
            summary['received_messages'] != len(receipts)):
        raise ValueError('Live summary is not a complete drained run')
    result_completions.sort(key=lambda c: c.finish_s)
    result = SimulationResult(policy, len(events), tuple(result_completions), tuple(drops), summary['max_waiting'])
    return summarize(result)


def completed_rows(receiver):
    with (receiver.output/'receiver/completed.csv').open(newline='') as stream:
        return list(csv.DictReader(stream))


def run_workload(plan, output, events, source, policy, *, capacity=None, service_ms=None):
    receiver = Receiver(plan, policy, output, capacity=capacity, service_ms=service_ms)
    try:
        receiver.ready()
        attempts = replay(plan, events, source, delivered=lambda n: len(receiver.receipts()) >= n,
                          journal=output/'publisher')
        write_json(output/'publisher.json', attempts)
        write_csv(output/'publisher.csv', attempts)
        wait_for(lambda: len(receiver.receipts()) >= len(attempts))
        time.sleep(.1)  # allow queued transport duplicates to surface before intake stops
    finally:
        receiver.stop(timeout=10+len(events)*(service_ms or plan['service_ms'])/500)
    summary = read_json(output/'receiver/summary.json')
    metrics = reconcile(events, source, receiver.receipts(), completed_rows(receiver), summary, policy)
    write_json(output/'logical_summary.json', metrics)
    write_csv(output/'logical_summary.csv', metrics)
    return metrics, summary


def reconnect_check(plan, output, broker):
    receiver = Receiver(plan, 'adaptive_guarded', output, capacity=10, service_ms=2)
    source = 'reconnect-check'
    attempts = []
    try:
        receiver.ready()
        publisher = Publisher(plan['port'], output/'publisher-before')
        try:
            for index in (0, 1):
                publisher.send(dict(source=source, id=str(index), priority=0, deadline_ms=100))
            attempts.extend(r | dict(phase='before_restart') for r in publisher.collect())
            wait_for(lambda: len(receiver.receipts()) >= 2)
        finally:
            publisher.close()
        wait_for(lambda: len(completed_rows(receiver)) == 2)
        broker.stop()
        wait_for(lambda: any(r['event'] == 'disconnected' for r in receiver.lifecycle()))
        broker.start()
        receiver.ready(count=2)
        publisher = Publisher(plan['port'], output/'publisher-after')
        try:
            for index in (0, 1, 2):
                publisher.send(dict(source=source, id=str(index), priority=0, deadline_ms=100))
            attempts.extend(r | dict(phase='after_restart') for r in publisher.collect())
            wait_for(lambda: len(receiver.receipts()) >= 5)
        finally:
            publisher.close()
        wait_for(lambda: len(receiver.receipts()) >= 5)
    finally:
        receiver.stop()
        write_json(output/'publisher.json', attempts)
    summary = read_json(output/'receiver/summary.json')
    if (summary['completed'] != 3 or summary['duplicate_messages'] != 2 or not summary['drained']
            or {r['id'] for r in completed_rows(receiver)} != {'0', '1', '2'}):
        raise AssertionError('Reconnect/resubscribe/dedup check failed')
    return dict(check='broker_restart_resubscribe_dedup', passed=True, summary=summary)


def execute(output):
    output = Path(output).resolve()
    plan, registration = load_plan(output, executing=True)
    if sys.platform == 'win32':
        raise ValueError('Controlled validation currently requires POSIX process signals')
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', plan['port']))  # refuse an occupied port; never control another broker
    directory = output/'runs'
    directory.mkdir(exist_ok=False)
    write_json(directory/'started.json', dict(plan_sha256=registration['plan_sha256'], provenance=provenance(),
        paho_mqtt=importlib.metadata.version('paho-mqtt'),
        broker_implementation=plan['broker'],
        broker_version=broker_description(plan),
        amqtt=importlib.metadata.version('amqtt') if plan['broker'] == 'amqtt' else None))
    broker = Broker(plan, directory)
    rows, checks, timing = [], [], []
    try:
        broker.start()
        for order in plan['execution_order']:
            name = f'traces/{order["scenario_id"]}-{order["seed"]}.csv'
            events = load_trace(output/name)
            for policy in order['policies']:
                relative = f'{order["scenario_id"]}/{order["seed"]}/{policy}'
                metrics, _ = run_workload(plan, directory/relative, events, relative.replace('/', '-'), policy)
                rows.extend(dict(scenario_id=order['scenario_id'], seed=order['seed'], run_path='runs/'+relative,
                                 workload_sha256=registration['traces'][name]['workload_sha256'], **row) for row in metrics)
                attempts = read_json(directory/relative/'publisher.json')
                timing.append(timing_summary(order['scenario_id'], order['seed'], policy, attempts))
                print(f'Live replay: {relative}', flush=True)
        stress = [Alert(i, 0, 0 if i % 10 == 0 else 2, .1 if i % 10 == 0 else 2.) for i in range(32)]
        for policy in ('priority', 'adaptive_guarded'):
            _, summary = run_workload(plan | dict(duplicate_every=0), directory/f'overload-{policy}',
                                      stress, f'overload-{policy}', policy, capacity=1, service_ms=50)
            passed = summary['rejected_queue_full'] > 0 and summary['max_waiting'] <= 1 and summary['drained']
            if not passed:
                raise AssertionError(f'Overload was not observed or admission was invalid: {policy}')
            checks.append(dict(check=f'overload_{policy}', passed=True, summary=summary))
        checks.append(reconnect_check(plan, directory/'reconnect', broker))
        write_csv(directory/'run_metrics.csv', rows)
        write_json(directory/'run_metrics.json', rows)
        write_json(directory/'checks.json', checks)
        write_csv(directory/'publisher_timing.csv', timing)
        write_json(directory/'publisher_timing.json', timing)
        write_report(directory, rows, checks)
    finally:
        broker.stop()
    seal(directory, dict(plan_sha256=registration['plan_sha256'], profile=plan['profile'],
                          workload_runs=len(rows)//4, checks=len(checks), evidence='engineering validation, descriptive only'))
    return checks


def broker_description(plan):
    if plan['broker'] == 'amqtt':
        return importlib.metadata.version('amqtt')
    result = subprocess.run([shutil.which('mosquitto') or 'mosquitto', '-h'], capture_output=True, text=True)
    text = (result.stdout+result.stderr).strip()
    if not text:
        raise ValueError('Broker version could not be captured')
    return text.splitlines()[0]


def timing_summary(scenario, seed, policy, attempts):
    drift = sorted(r['drift_ms'] for r in attempts)
    return dict(scenario_id=scenario, seed=seed, policy=policy, attempts=len(attempts),
                mean_drift_ms=statistics.fmean(drift), p95_drift_ms=drift[math.ceil(.95*len(drift))-1],
                max_drift_ms=drift[-1])


def write_report(directory, rows, checks):
    lines = ['# Controlled live validation', '',
        '**Descriptive engineering evidence; not a primary research result.**', '',
        'Logical metrics start at the first receiver callback per event, including rejected attempts. '
        'Publisher ACKs acknowledge transport; subscriber receipts are reconciled separately. '
        'Policies share the planned trace, while realized callback timings differ. No warm-up is '
        'removed and no statistical superiority is inferred.', '',
        '| Scenario | Seed | Policy | Generated | Completed | Dropped |',
        '| --- | --- | --- | --- | --- | --- |']
    for row in rows:
        if row['priority'] == 'all':
            lines.append(f'| {row["scenario_id"]} | {row["seed"]} | {row["policy"]} | '
                         f'{row["generated"]} | {row["completed"]} | {row["dropped"]} |')
    lines += ['', 'Functional checks: '+', '.join(r['check'] for r in checks)+'.', '',
        'See run_metrics.csv for per-class latency/waiting/deadline/loss and publisher_timing.csv '
        'for replay drift. Raw traces, publisher ACK timing, receipts, completions, receiver lifecycle '
        'logs and source hashes are retained. Reconnect retries are deliberate application publishes '
        'after resubscription, not forced MQTT retransmissions or offline delivery tests.', '']
    (directory/'report.md').write_text('\n'.join(lines))


def verify_publisher(attempts, receipts):
    intended = Counter((r['source'], r['id']) for r in attempts)
    delivered = Counter((r['source'], r['id']) for r in receipts)
    if any(delivered[key] < count for key, count in intended.items()) or set(delivered) != set(intended):
        raise ValueError('Publisher attempts do not match subscriber receipts')
    for row in attempts:
        times = [row[k] for k in ('planned_s', 'issued_s', 'publish_return_s', 'ack_s', 'drift_ms')]
        if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in times):
            raise ValueError('Publisher timing must be finite')
        if row['ack_s'] < row['issued_s'] or row['publish_return_s'] < row['issued_s']:
            raise ValueError('Publisher timestamps are not monotonic')
        if not math.isclose(row['drift_ms'], (row['issued_s']-row['planned_s'])*1000, rel_tol=1e-10, abs_tol=1e-8):
            raise ValueError('Publisher drift differs from timestamps')


def verify_journal(directory, attempts):
    issued = json_lines(directory/'attempts.jsonl')
    ack_rows = json_lines(directory/'acks.jsonl')
    acknowledgements = {r['mid']: r['ack_s'] for r in ack_rows}
    if (len(acknowledgements) != len(ack_rows) or len(issued) != len(attempts)
            or len(acknowledgements) != len(attempts) or len({r['mid'] for r in attempts}) != len(attempts)):
        raise ValueError('Publisher journal is incomplete or ambiguous')
    for record, row in zip(issued, attempts):
        expected = {k: v for k, v in row.items() if k not in ('ack_s', 'phase')}
        if record != expected or acknowledgements.get(row['mid']) != row['ack_s']:
            raise ValueError('Publisher aggregate differs from incremental journal')


def verify_planned_attempts(events, attempts, source, duplicate_every):
    expected = Counter({str(e.id): 1+int(bool(duplicate_every and (i+1) % duplicate_every == 0))
                        for i, e in enumerate(events)})
    if Counter(r['id'] for r in attempts) != expected or any(r['source'] != source for r in attempts):
        raise ValueError('Publisher attempts differ from registered duplicate pattern')
    by_id = {str(e.id): e for e in events}
    offset = attempts[0]['planned_s']-by_id[attempts[0]['id']].arrival
    for row in attempts:
        if not math.isclose(row['planned_s'], offset+by_id[row['id']].arrival, rel_tol=1e-10, abs_tol=1e-8):
            raise ValueError('Publisher schedule differs from registered trace')


def verify_functional_checks(output, plan, checks):
    by_name = {r['check']: r for r in checks}
    if len(by_name) != 3 or set(by_name) != set(plan['checks']) or not all(r['passed'] for r in checks):
        raise ValueError('Live checks incomplete')
    for policy in ('priority', 'adaptive_guarded'):
        path = output/'runs'/f'overload-{policy}'
        summary = read_json(path/'receiver/summary.json')
        receipts = json_lines(path/'receiver/receipts.jsonl')
        with (path/'receiver/completed.csv').open(newline='') as stream:
            completed = list(csv.DictReader(stream))
        events = [Alert(i, 0, 0 if i % 10 == 0 else 2, .1 if i % 10 == 0 else 2.) for i in range(32)]
        reconcile(events, f'overload-{policy}', receipts, completed, summary, policy)
        verify_publisher(read_json(path/'publisher.json'), receipts)
        verify_journal(path/'publisher', read_json(path/'publisher.json'))
        if (summary != by_name[f'overload_{policy}']['summary'] or summary['rejected_queue_full'] < 1
                or summary['max_waiting'] > 1):
            raise ValueError('Overload check differs from raw evidence')
    path = output/'runs/reconnect'
    lifecycle = json_lines(path/'receiver/lifecycle.jsonl')
    subscriptions = [i for i, r in enumerate(lifecycle) if r['event'] == 'subscribed' and r.get('success')]
    if len(subscriptions) < 2 or not any(r['event'] == 'disconnected' for r in lifecycle[subscriptions[0]+1:subscriptions[1]]):
        raise ValueError('Reconnect lifecycle lacks disconnect and resubscription')
    summary = read_json(path/'receiver/summary.json')
    receipts = json_lines(path/'receiver/receipts.jsonl')
    with (path/'receiver/completed.csv').open(newline='') as stream:
        completed = list(csv.DictReader(stream))
    events = [Alert(i, 0, 0, .1) for i in range(3)]
    reconcile(events, 'reconnect-check', receipts, completed, summary, 'adaptive_guarded')
    verify_publisher(read_json(path/'publisher.json'), receipts)
    attempts = read_json(path/'publisher.json')
    verify_journal(path/'publisher-before', [r for r in attempts if r['phase'] == 'before_restart'])
    verify_journal(path/'publisher-after', [r for r in attempts if r['phase'] == 'after_restart'])
    if (summary != by_name['broker_restart_resubscribe_dedup']['summary'] or summary['completed'] != 3
            or summary['duplicate_messages'] != 2):
        raise ValueError('Reconnect check differs from raw evidence')


def verify_receiver_config(path, plan, registration, policy, capacity, service_ms):
    config = read_json(path/'receiver/config.json')
    expected = {k: plan[k] for k in ('aging_ms', 'aging_min_ms', 'aging_max_ms', 'service_estimate_ms',
                                     'dedup_capacity', 'dedup_ttl_s', 'port')}
    expected.update(policy=policy, queue_capacity=capacity, service_ms=service_ms, host='127.0.0.1', qos=1)
    expected['source_sha256'] = {name: registration['provenance']['source']['files']['iot_alerts/'+name]
                               for name in ('live.py', 'mqtt_demo.py', 'simulator.py', 'scheduling.py')}
    if any(config.get(k) != v for k, v in expected.items()):
        raise ValueError('Receiver configuration differs from registered validation')
    if read_json(path/'receiver/summary.json')['max_waiting'] > capacity:
        raise ValueError('Live waiting capacity exceeded')


def verify_evidence(output):
    output = Path(output).resolve()
    plan, registration = load_plan(output)
    marker = verify(output/'runs')
    if marker['plan_sha256'] != registration['plan_sha256'] or marker['workload_runs'] != registration['workload_runs'] or marker['checks'] != 3:
        raise ValueError('Live completion inventory mismatch')
    rows = read_json(output/'runs/run_metrics.json')
    expected = {(o['scenario_id'], o['seed'], p, priority) for o in plan['execution_order']
                for p in o['policies'] for priority in ('all', 0, 1, 2)}
    indexed = {}
    for row in rows:
        key = row['scenario_id'], row['seed'], row['policy'], row['priority']
        if key not in expected or key in indexed:
            raise ValueError('Unexpected/duplicate live metric row')
        name = f'traces/{row["scenario_id"]}-{row["seed"]}.csv'
        if (row['workload_sha256'] != registration['traces'][name]['workload_sha256'] or
                row['run_path'] != f'runs/{row["scenario_id"]}/{row["seed"]}/{row["policy"]}'):
            raise ValueError('Live result does not reference its planned paired input')
        indexed[key] = row
    if set(indexed) != expected:
        raise ValueError('Missing live metric rows')
    expected_timing = []
    for order in plan['execution_order']:
        events = load_trace(output/f'traces/{order["scenario_id"]}-{order["seed"]}.csv')
        for policy in order['policies']:
            path = output/'runs'/order['scenario_id']/str(order['seed'])/policy
            receipts = json_lines(path/'receiver/receipts.jsonl')
            with (path/'receiver/completed.csv').open(newline='') as stream:
                completions = list(csv.DictReader(stream))
            source = f'{order["scenario_id"]}-{order["seed"]}-{policy}'
            verify_receiver_config(path, plan, registration, policy, plan['capacity'], plan['service_ms'])
            verify_publisher(read_json(path/'publisher.json'), receipts)
            verify_journal(path/'publisher', read_json(path/'publisher.json'))
            attempts = read_json(path/'publisher.json')
            verify_planned_attempts(events, attempts, source, plan['duplicate_every'])
            expected_timing.append(timing_summary(order['scenario_id'], order['seed'], policy, attempts))
            metrics = reconcile(events, source, receipts, completions, read_json(path/'receiver/summary.json'), policy)
            if metrics != read_json(path/'logical_summary.json'):
                raise ValueError('Per-run logical summary differs from raw evidence')
            for row in metrics:
                stored = indexed[(order['scenario_id'], order['seed'], policy, row['priority'])]
                if any(stored.get(k) != v for k, v in row.items()):
                    raise ValueError('Live metrics differ from raw evidence')
    if expected_timing != read_json(output/'runs/publisher_timing.json'):
        raise ValueError('Replay timing summary differs from publisher records')
    checks = read_json(output/'runs/checks.json')
    verify_functional_checks(output, plan, checks)
    for policy in ('priority', 'adaptive_guarded'):
        verify_receiver_config(output/'runs'/f'overload-{policy}', plan, registration, policy, 1, 50)
    verify_receiver_config(output/'runs/reconnect', plan, registration, 'adaptive_guarded', 10, 2)
    return marker


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=('plan', 'run', 'verify'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--profile', choices=('smoke', 'validation'), default='smoke')
    parser.add_argument('--broker', choices=('mosquitto', 'amqtt'), default='mosquitto')
    parser.add_argument('--port', type=int, default=18884)
    args = parser.parse_args()
    try:
        if args.stage == 'plan':
            plan = register(args.output, args.profile, args.broker, args.port)
            print(f'Registered {len(plan["execution_order"])*len(plan["policies"])} workload runs and 3 functional checks')
        elif args.stage == 'run':
            execute(args.output)
            print('Live validation complete; results are descriptive engineering evidence')
        else:
            verify_evidence(args.output)
            print('Live raw evidence, metrics and inventories verified')
    except (ValueError, OSError, KeyError, RuntimeError, ImportError) as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()
