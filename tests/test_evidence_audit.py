import io
import json
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from iot_alerts import evidence_audit as audit


class EvidenceAuditTests(unittest.TestCase):
    def test_checked_in_evidence_reproduces(self):
        with tempfile.TemporaryDirectory() as directory:
            report = audit.run(Path(directory)/'audit')
            self.assertTrue(report['engineering_checks_passed'])
            self.assertEqual(report['checks']['baseline_pilot']['policy_runs'], 90)
            self.assertEqual(report['checks']['live_smoke']['workload_runs'], 8)
            self.assertEqual(report['research_readiness'], 'not established by this audit')
            self.assertEqual(json.loads((Path(directory)/'audit/audit.json').read_text()), report)
            with self.assertRaises(FileExistsError):
                audit.run(Path(directory)/'audit')

    def test_failure_remains_visible_and_other_check_runs(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(audit, 'audit_pilot', side_effect=ValueError('changed results')), \
                    patch.object(audit, 'audit_live', return_value={'status': 'verified'}) as live:
                report = audit.run(Path(directory)/'audit')
            self.assertFalse(report['engineering_checks_passed'])
            self.assertIn('changed results', report['checks']['baseline_pilot']['error'])
            live.assert_called_once()

    def test_archive_rejects_escape_links_and_duplicate_members(self):
        for names, link in [(['live-validation-smoke/../../escape'], False),
                            (['/absolute'], False), (['live-validation-smoke/link'], True),
                            (['live-validation-smoke/a']*2, False)]:
            with self.subTest(names=names), tempfile.TemporaryDirectory() as directory:
                archive = Path(directory)/'bad.tar.gz'
                with tarfile.open(archive, 'w:gz') as stream:
                    for name in names:
                        item = tarfile.TarInfo(name)
                        if link:
                            item.type = tarfile.SYMTYPE
                            item.linkname = '/tmp/escape'
                            stream.addfile(item)
                        else:
                            item.size = 1
                            stream.addfile(item, io.BytesIO(b'x'))
                with self.assertRaises(ValueError):
                    audit.restore_archive(archive, Path(directory)/'restored')

    def test_changed_archive_or_public_summary_is_rejected(self):
        import shutil
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            folder = root/'evidence/live-validation-smoke'
            shutil.copytree(audit.ROOT/'evidence/live-validation-smoke', folder)
            summary = json.loads((folder/'summary.json').read_text())
            summary['workload_runs'][0]['completed'] += 1
            (folder/'summary.json').write_text(json.dumps(summary))
            with self.assertRaisesRegex(ValueError, 'public summary'):
                audit.audit_live(root, root/'restore')
            (folder/'artifacts.tar.gz').write_bytes(b'altered')
            with self.assertRaisesRegex(ValueError, 'digest'):
                audit.audit_live(root, root/'restore-again')

    def test_output_cannot_be_written_into_evidence(self):
        with self.assertRaises(ValueError):
            audit.run(audit.ROOT/'evidence/should-not-exist')
