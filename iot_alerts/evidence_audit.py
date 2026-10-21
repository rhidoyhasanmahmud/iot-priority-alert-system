"""Reproduce checked-in engineering evidence; never infer research readiness."""
import argparse
import csv
import gzip
import hashlib
import json
import random
import statistics
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def restore_archive(archive, destination):
    """Restore only bounded regular files/directories beneath the expected root."""
    with tarfile.open(archive, 'r:gz') as stream:
        members = stream.getmembers()
        if len(members) > 10000 or sum(m.size for m in members) > 100_000_000:
            raise ValueError('Archive exceeds audit limits')
        seen = set()
        for member in members:
            parts = Path(member.name).parts
            if (not parts or parts[0] != 'live-validation-smoke' or
                    '..' in parts or member.name in seen or
                    not (member.isdir() or member.isfile())):
                raise ValueError('Unsafe or duplicate archive member')
            seen.add(member.name)
            target = destination.joinpath(*parts)
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with stream.extractfile(member) as source:
                    target.write_bytes(source.read())
    return destination/'live-validation-smoke'


def audit_pilot(root, temporary):
    subprocess.run([sys.executable, '-m', 'iot_alerts.pilot', '--output', str(temporary)],
                   cwd=root, check=True, capture_output=True, text=True)
    evidence = root/'evidence/pilot'
    for name in ('run_metrics.csv', 'aggregate.csv'):
        if (temporary/name).read_bytes() != (evidence/name).read_bytes():
            raise ValueError(f'Pilot reproduction differs: {name}')
    name = 'example-rate120-seed1-priority.csv.gz'
    if gzip.decompress((temporary/name).read_bytes()) != gzip.decompress((evidence/name).read_bytes()):
        raise ValueError('Pilot raw example differs')
    with (evidence/'run_metrics.csv').open(newline='') as stream:
        rows = list(csv.DictReader(stream))
    with (evidence/'paired_intervals.csv').open(newline='') as stream:
        stored = list(csv.DictReader(stream))
    expected = []
    for priority, label in ((0, 'High p95 latency'), (2, 'Low p95 latency')):
        values = {(int(r['seed']), r['policy']): float(r['p95_latency_ms'])
                  for r in rows if int(r['rate']) == 90 and int(r['priority']) == priority}
        differences = [values[s, 'aging'] - values[s, 'priority'] for s in range(1, 11)]
        rng = random.Random(2026)
        means = sorted(statistics.mean(rng.choices(differences, k=10)) for _ in range(10000))
        expected.append(dict(outcome=label, mean_difference_ms=statistics.mean(differences),
                             lower_ms=means[249], upper_ms=means[9749]))
    if len(stored) != len(expected) or any(
            actual['outcome'] != wanted['outcome'] or any(float(actual[k]) != wanted[k]
            for k in ('mean_difference_ms', 'lower_ms', 'upper_ms'))
            for actual, wanted in zip(stored, expected)):
        raise ValueError('Pilot paired intervals differ')
    return {'status': 'verified', 'policy_runs': 90, 'scope': 'historical baseline pilot only'}


def audit_live(root, temporary):
    from .live_validation import verify_evidence
    folder = root/'evidence/live-validation-smoke'
    summary = json.loads((folder/'summary.json').read_text())
    if digest(folder/'artifacts.tar.gz') != summary['archive_sha256']:
        raise ValueError('Live archive digest differs')
    restored = restore_archive(folder/'artifacts.tar.gz', temporary)
    marker = verify_evidence(restored)
    registration = json.loads((restored/'registration.json').read_text())
    plan = json.loads((restored/'plan.json').read_text())
    rows = json.loads((restored/'runs/run_metrics.json').read_text())
    observed = [{k: row[k] for k in ('scenario_id', 'seed', 'policy', 'generated', 'completed', 'dropped')}
                for row in rows if row['priority'] == 'all']
    checks = json.loads((restored/'runs/checks.json').read_text())
    if (plan['profile'] != summary['profile'] or summary['profile'] != 'smoke' or
            registration['plan_sha256'] != summary['plan_sha256'] or
            registration['provenance']['source']['sha256'] != summary['source_sha256'] or
            observed != summary['workload_runs'] or checks != summary['checks']):
        raise ValueError('Live public summary differs from verified raw evidence')
    return {'status': 'verified', 'workload_runs': marker['workload_runs'],
            'scope': 'archived local smoke; no performance superiority claim'}


def run(output, root=ROOT):
    output = Path(output).resolve()
    root = Path(root).resolve()
    if output == root or (root in output.parents and output.relative_to(root).parts[0] != 'results'):
        raise ValueError('Audit output must not modify source or evidence directories')
    output.mkdir(parents=True, exist_ok=False)
    checks = {}
    with tempfile.TemporaryDirectory(prefix='iot-evidence-audit-') as temporary:
        for name, function in (('baseline_pilot', audit_pilot), ('live_smoke', audit_live)):
            try:
                checks[name] = function(root, Path(temporary)/name)
            except Exception as error:
                checks[name] = {'status': 'failed', 'error': f'{type(error).__name__}: {error}'}
    report = {'schema_version': 1, 'scope': 'checked-in evidence only; external results are not inspected',
              'engineering_checks_passed': all(c['status'] == 'verified' for c in checks.values()),
              'research_readiness': 'not established by this audit', 'checks': checks,
              'pending': ['Primary tuning and held-out evaluation', 'Primary statistical analysis and robustness',
                          'Full controlled live validation', 'Closest-method full-text comparison and defensible contribution'],
              'inputs_sha256': {str(p.relative_to(root)): digest(p) for p in sorted((root/'evidence').rglob('*')) if p.is_file()},
              'audit_source_sha256': digest(Path(__file__)), 'python': sys.version}
    (output/'audit.json').write_text(json.dumps(report, indent=2)+'\n')
    lines = ['# Checked-in evidence audit', '', report['scope'], '', '| Check | Status |', '| --- | --- |']
    lines += [f'| {name} | {value["status"]} |' for name, value in checks.items()]
    lines += ['', 'Research readiness is not established. A passing audit verifies the checked-in pilot and local smoke evidence only.', '',
              '## Remaining research work', ''] + [f'- {item}' for item in report['pending']]
    lines += ['', 'See audit.json for errors, input hashes and audit identity. Hashes detect changes; they do not establish novelty or authenticate an independent replication.']
    (output/'report.md').write_text('\n'.join(lines)+'\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = run(args.output)
    print(f'Evidence audit: {args.output}; passed={report["engineering_checks_passed"]}')
    return 0 if report['engineering_checks_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
