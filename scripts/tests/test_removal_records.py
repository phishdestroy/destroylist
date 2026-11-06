import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import utils
import smart_aggregator
from removal_records import removal_hosts
from generate_stix import build, make_indicator


def registry(host='example.com'):
    return {'version': 1, 'domains': {host: {
        'reason': 'appeal', 'reference': 'https://example.org/appeal/1',
        'removed_at': '2026-11-05T13:00:46Z',
    }}}


class RemovalTests(unittest.TestCase):
    def test_exact_scope_and_www_without_sibling_tenants(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'removals.json'
            p.write_text(json.dumps(registry('reviewed.pages.dev')))
            with patch.object(utils, 'REMOVALS_FILE', p), patch.object(utils, 'load_allowlist_split', return_value=(set(), set())):
                exact, patterns = utils.load_publication_exclusions()
        self.assertTrue(utils.is_allowed('www.reviewed.pages.dev', exact, patterns))
        self.assertTrue(utils.is_allowed('reviewed.pages.dev/path', exact, patterns))
        self.assertFalse(utils.is_allowed('other.pages.dev', exact, patterns))
        self.assertFalse(utils.is_allowed('child.reviewed.pages.dev', exact, patterns))

    def test_invalid_or_missing_registry_stops_publication(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'removals.json'
            with patch.object(utils, 'REMOVALS_FILE', p):
                with self.assertRaises(FileNotFoundError):
                    utils.load_publication_exclusions()
                p.write_text('{')
                with self.assertRaises(ValueError):
                    utils.load_publication_exclusions()
                p.write_text(json.dumps(registry('pages.dev')))
                with self.assertRaises(ValueError):
                    utils.load_publication_exclusions()

    def test_scope_and_provenance_validation(self):
        for host in ['.example.com', '*.example.com', 'example.com/path', 'EXAMPLE.com', '-bad.example']:
            with self.assertRaises(ValueError):
                removal_hosts(registry(host))
        for key in ['removed_at', 'reason', 'reference']:
            data = registry()
            del data['domains']['example.com'][key]
            with self.assertRaises(ValueError):
                removal_hosts(data)

    def test_stix_revokes_previously_published_removal(self):
        old = make_indicator('example.com', '2026-11-01T00:00:00.000Z')
        bundle, active, revoked = build(['example.com', 'other.test'], {'example.com': [old, []]}, removal_hosts(registry()), set(), '2026-11-06T00:00:00.000Z')
        self.assertEqual((active, revoked), (1, 1))
        retracted = next(o for o in bundle['objects'] if o['id'] == old['id'])
        self.assertTrue(retracted['revoked'])

    def test_unchanged_upstream_counts_cannot_skip_new_removal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / 'blocklist.json'
            output.write_text(json.dumps(['example.com', 'other.test']))
            state = root / 'state.json'
            state.write_text(json.dumps({'total_count': 2}))
            with patch.multiple(smart_aggregator, COMMUNITY_DIR=root, OUTPUT_FILE=output,
                                STATE_FILE=state, BADGE_FILE=root/'count.json',
                                COMMIT_MSG_FILE=root/'message.txt', LOCAL_FILES=[], SOURCES_CONFIG={}), \
                 patch.object(smart_aggregator, 'load_publication_exclusions', return_value=({'example.com'}, set())):
                smart_aggregator.main()
            self.assertEqual(json.loads(output.read_text()), ['other.test'])


if __name__ == '__main__':
    unittest.main()
