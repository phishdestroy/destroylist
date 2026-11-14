import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from smart_aggregator import parse_text_lines, parse_urls_list
from json_to_txt import load_domains, load_plain_entries
from build_rootlist import process_items
import smart_aggregator


class URLScopeTests(unittest.TestCase):
    def test_url_feeds_preserve_case_query_and_fragment(self):
        result = parse_urls_list('https://LINE.me/Profile/AbC?Token=XyZ#View\nhttps://dribbble.com/\n')
        self.assertEqual(result, {'line.me/Profile/AbC?Token=XyZ#View', 'dribbble.com/'})

    def test_text_url_query_is_not_misread_as_adblock_options(self):
        self.assertEqual(parse_text_lines('https://line.me/AbC?price=$10^2'), {'line.me/AbC?price=$10^2'})

    def test_mixed_feed_keeps_domain_rules_and_scoped_urls(self):
        result = parse_text_lines('0.0.0.0 bad.example\n||scam.example^\nwww.bad.example\nhttps://line.me/AbC\napi.npoint.io/AbC\n')
        self.assertEqual(result, {'bad.example', 'scam.example', 'www.bad.example', 'line.me/AbC', 'api.npoint.io/AbC'})

    def test_bad_urls_never_fall_back_to_domain_extraction(self):
        result = parse_urls_list('javascript://safe.example/x\nhttps://host.example:BAD/x\nhttps://host.example:8443/x\nhttps://127.0.0.1/x\n')
        self.assertEqual(result, set())

    def test_url_evidence_survives_plain_feed_without_dns_or_root_block(self):
        entries = parse_urls_list('https://line.me/Profile/AbC\nhttps://tenant.pages.dev/OnlyThisPage\n') | {'malicious-example.com'}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'list.json'
            path.write_text(json.dumps(sorted(entries)))
            self.assertEqual(set(load_plain_entries(path)), entries)
            self.assertEqual(load_domains(path, set()), ['malicious-example.com'])
        roots, providers, hosts, services = process_items(list(entries))
        self.assertNotIn('line.me', roots | hosts | services)
        self.assertNotIn('tenant.pages.dev', roots | hosts | services)
        self.assertEqual(hosts, {'malicious-example.com'})

    def test_reviewed_apex_is_not_recreated_by_child_domain(self):
        roots, _, hosts, services = process_items(['line.me', 'bad.line.me'], {'line.me'})
        self.assertNotIn('line.me', roots | hosts | services)
        self.assertEqual(services, {'bad.line.me'})

    def test_scoped_evidence_survives_next_aggregation_without_upstream(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / 'blocklist.json'
            output.write_text(json.dumps(['line.me/Profile/AbC']))
            with patch.multiple(smart_aggregator, COMMUNITY_DIR=root, OUTPUT_FILE=output,
                    STATE_FILE=root/'state.json', BADGE_FILE=root/'count.json',
                    COMMIT_MSG_FILE=root/'message.txt', LOCAL_FILES=[], SOURCES_CONFIG={}), \
                    patch.object(smart_aggregator, 'load_publication_exclusions', return_value=(set(),set())):
                smart_aggregator.main()
            self.assertEqual(json.loads(output.read_text()), ['line.me/Profile/AbC'])


if __name__ == '__main__':
    unittest.main()
