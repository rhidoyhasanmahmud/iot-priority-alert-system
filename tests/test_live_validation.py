import copy
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from iot_alerts import live_validation as live, study
from iot_alerts.simulator import Alert


def fixture():
    events = [Alert(0, 0, 0, .1), Alert(1, .01, 2, 2), Alert(2, .02, 2, 2)]
    def receipt(id, arrival, status, sequence=None):
        event = events[id]
        result = dict(source='test', id=str(id), priority=event.priority, deadline_ms=event.deadline_s*1000,
                      arrival_s=arrival, status=status,
                      reason={'admitted': '', 'duplicate': 'already_seen', 'rejected': 'queue_full'}[status])
        if sequence is not None:
            result['sequence'] = sequence
        return result
    receipts = [receipt(0, 1., 'admitted', 0), receipt(0, 1.01, 'duplicate'),
                receipt(1, 1.1, 'rejected'), receipt(1, 1.2, 'admitted', 1), receipt(2, 1.21, 'rejected')]
    def complete(event, arrival, start, finish, sequence):
        return dict(source='test', id=str(event.id), priority=str(event.priority), deadline_ms=str(event.deadline_s*1000),
                    sequence=str(sequence), arrival_s=str(arrival), start_s=str(start), finish_s=str(finish),
                    wait_ms=str((start-arrival)*1000), service_ms=str((finish-start)*1000),
                    local_latency_ms=str((finish-arrival)*1000))
    completed = [complete(events[0], 1., 1., 1.02, 0), complete(events[1], 1.2, 1.2, 1.3, 1)]
    summary = dict(drained=True, unfinished=0, worker_errors=[], admitted=2, completed=2,
                   duplicate_messages=1, rejected_queue_full=2, received_messages=5, max_waiting=1)
    return events, receipts, completed, summary


class ReconciliationTests(unittest.TestCase):
    def test_attempt_counts_and_logical_population_differ(self):
        events, receipts, completed, summary = fixture()
        rows = live.reconcile(events, 'test', receipts, completed, summary, 'priority')
        self.assertEqual(rows[0]['generated'], 3)
        self.assertEqual(rows[0]['completed'], 2)
        self.assertEqual(rows[0]['dropped'], 1)
        low = next(r for r in rows if r['priority'] == 2)
        self.assertEqual(low['deadline_failure_fraction'], .5)
        self.assertAlmostEqual(low['p95_wait_ms'], 100.)  # includes prior rejection, not just admission wait

    def test_retry_does_not_reset_logical_deadline(self):
        events, receipts, completed, summary = fixture()
        events[1] = Alert(1, .01, 2, .1)
        for row in receipts:
            if row['id'] == '1':
                row['deadline_ms'] = 100.
        completed[1].update(deadline_ms='100', finish_s='1.25', service_ms=str((1.25-1.2)*1000),
                             local_latency_ms=str((1.25-1.2)*1000))
        low = next(r for r in live.reconcile(events, 'test', receipts, completed, summary, 'priority') if r['priority'] == 2)
        self.assertEqual(low['deadline_missed_completed'], 1)
        self.assertEqual(low['deadline_failure_fraction'], 1)

    def test_missing_receipt_duplicate_completion_and_unfinished_rejected(self):
        events, receipts, completed, summary = fixture()
        cases = [(receipts[:-1], completed, summary), (receipts, completed+[completed[0]], summary),
                 (receipts, completed, summary | dict(unfinished=1)),
                 (receipts, completed, summary | dict(duplicate_messages=0))]
        for r, c, s in cases:
            with self.subTest(case=(len(r), len(c), s)), self.assertRaises(ValueError):
                live.reconcile(events, 'test', r, c, s, 'priority')

    def test_bad_identity_metadata_or_nonfinite_time_rejected(self):
        events, receipts, completed, summary = fixture()
        for change in ({'source': 'wrong'}, {'priority': 2}, {'arrival_s': math.nan}, {'status': 'unknown'}):
            altered = copy.deepcopy(receipts)
            altered[0].update(change)
            with self.assertRaises(ValueError):
                live.reconcile(events, 'test', altered, completed, summary, 'priority')
        for change in ({'start_s': '-1'}, {'finish_s': 'nan'}, {'sequence': '44'}, {'service_ms': '-1'}):
            altered = copy.deepcopy(completed)
            altered[0].update(change)
            with self.assertRaises(ValueError):
                live.reconcile(events, 'test', receipts, altered, summary, 'priority')

    def test_partial_json_line_waits_but_malformed_complete_line_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)/'rows.jsonl'
            path.write_text('{"a":1}\n{"a":')
            self.assertEqual(live.json_lines(path), [{'a': 1}])
            path.write_text('{bad}\n')
            with self.assertRaises(ValueError):
                live.json_lines(path)


class RegistrationTests(unittest.TestCase):
    def test_profile_counts_randomized_paired_order_and_seeds(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)/'study'
            plan = live.register(output, 'validation', 'amqtt')
            self.assertEqual(study.read_json(output/'registration.json')['workload_runs'], 160)
            self.assertEqual(plan['seeds'], list(range(6001, 6006)))
            self.assertEqual(len(plan['scenarios']), 4)
            self.assertTrue(all(set(o['policies']) == set(plan['policies']) for o in plan['execution_order']))
            self.assertTrue(any(o['policies'] != plan['policies'] for o in plan['execution_order']))
            self.assertFalse((output/'runs').exists())
            live.load_plan(output)
            with self.assertRaises(FileExistsError):
                live.register(output)

    def test_modified_trace_plan_and_source_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)/'study'
            live.register(output, broker='amqtt')
            original = study.source_identity()
            with patch.object(live, 'source_identity', return_value=original | dict(sha256='changed')):
                with self.assertRaisesRegex(ValueError, 'source/Python'):
                    live.load_plan(output, executing=True)
                live.load_plan(output)  # read-only verification can use later tooling
            trace = next((output/'traces').glob('*.csv'))
            trace.write_text(trace.read_text()+'\n')
            with self.assertRaisesRegex(ValueError, 'trace checksum'):
                live.load_plan(output)
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)/'study'
            live.register(output, broker='amqtt')
            plan = study.read_json(output/'plan.json')
            plan['count'] += 1
            study.write_json(output/'plan.json', plan)
            with self.assertRaisesRegex(ValueError, 'plan checksum'):
                live.load_plan(output)

    def test_no_verification_of_incomplete_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)/'study'
            live.register(output, broker='amqtt')
            with self.assertRaises(FileNotFoundError):
                live.verify_evidence(output)


class PublisherEvidenceTests(unittest.TestCase):
    def attempt(self):
        return dict(source='test', id='0', priority=0, deadline_ms=100, planned_s=0., issued_s=.01,
                    publish_return_s=.011, ack_s=.02, drift_ms=10., mid=1)

    def test_ack_delivery_and_drift_are_separate_checks(self):
        row = self.attempt()
        live.verify_publisher([row], [dict(source='test', id='0')])
        for changed, receipts in ((row | dict(ack_s=None), [dict(source='test', id='0')]),
                                  (row | dict(drift_ms=100), [dict(source='test', id='0')]),
                                  (row, [])):
            with self.assertRaises(ValueError):
                live.verify_publisher([changed], receipts)

    def test_incremental_journal_cross_links(self):
        row = self.attempt()
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)
            (path/'attempts.jsonl').write_text(json.dumps({k: v for k, v in row.items() if k != 'ack_s'})+'\n')
            (path/'acks.jsonl').write_text(json.dumps(dict(mid=1, ack_s=.02))+'\n')
            live.verify_journal(path, [row])
            (path/'acks.jsonl').write_text(json.dumps(dict(mid=1, ack_s=.03))+'\n')
            with self.assertRaisesRegex(ValueError, 'incremental journal'):
                live.verify_journal(path, [row])
            (path/'acks.jsonl').write_text('')
            with self.assertRaisesRegex(ValueError, 'incomplete'):
                live.verify_journal(path, [row])

    def test_schedule_and_duplicate_pattern_are_registered(self):
        events = [Alert(0, 0., 0, .1), Alert(1, .2, 2, 2)]
        attempts = [dict(source='test', id=id, planned_s=t) for id, t in [('0', .5), ('1', .7), ('1', .7)]]
        live.verify_planned_attempts(events, attempts, 'test', 2)
        with self.assertRaisesRegex(ValueError, 'duplicate pattern'):
            live.verify_planned_attempts(events, attempts[:-1], 'test', 2)
        attempts[-1]['planned_s'] = .8
        with self.assertRaisesRegex(ValueError, 'schedule'):
            live.verify_planned_attempts(events, attempts, 'test', 2)

    def test_timing_summary_nearest_rank(self):
        result = live.timing_summary('s000', 1, 'fifo', [dict(drift_ms=x) for x in (1., 2., 3., 4.)])
        self.assertEqual(result['mean_drift_ms'], 2.5)
        self.assertEqual(result['p95_drift_ms'], 4.)
        self.assertEqual(result['attempts'], 4)


class ArchivedEvidenceTests(unittest.TestCase):
    def test_checked_in_smoke_raw_evidence_recomputes(self):
        import tarfile
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            with tarfile.open(study.ROOT/'evidence/live-validation-smoke/artifacts.tar.gz') as archive:
                for member in archive.getmembers():
                    if not member.isfile():
                        continue
                    path = (target/member.name).resolve()
                    self.assertTrue(path.is_relative_to(target.resolve()))
                    path.parent.mkdir(parents=True, exist_ok=True)
                    with archive.extractfile(member) as stream:
                        path.write_bytes(stream.read())
            marker = live.verify_evidence(target/'live-validation-smoke')
            self.assertEqual(marker['workload_runs'], 8)
            self.assertEqual(marker['checks'], 3)
