import json
import re
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from validate_and_clean import TARGETS, filter_domains  # noqa: E402
import utils  # noqa: E402


MICROSOFT_DOMAINS = {
    "365.microsoft",
    "about.microsoft",
    "account.microsoft",
    "azure.microsoft",
    "band.microsoft",
    "bing.microsoft",
    "cloud.microsoft",
    "com.microsoft",
    "corp.microsoft",
    "data.microsoft",
    "download.microsoft",
    "dynamics.microsoft",
    "edge.microsoft",
    "empowering.microsoft",
    "forms.cloud.microsoft",
    "gamestack.microsoft",
    "go.microsoft",
    "groove.microsoft",
    "hackingstem.microsoft",
    "hololens.microsoft",
    "home.microsoft",
    "ieonline.microsoft",
    "integrity.microsoft",
    "ipv6.microsoft",
    "login.microsoft",
    "lumia.microsoft",
    "m365.microsoft",
    "manufacturing.microsoft",
    "microsoft365.microsoft",
    "my.microsoft",
    "net.microsoft",
    "ntservicepack.microsoft",
    "office.microsoft",
    "org.microsoft",
    "portal.microsoft",
    "productivity.microsoft",
    "remix3d.microsoft",
    "search.microsoft",
    "support.microsoft",
    "surface.microsoft",
    "tcp.microsoft",
    "udp.microsoft",
}

HISTORICAL_ARTIFACTS = (
    "archives/monthly/2026-08.json",
    "archives/weekly/2026-W25.json",
    "archives/weekly/2026-W30.json",
    "archives/weekly/2026-W31.json",
    "changes/2026-07/2026-07-26.json",
    "changes/2026-08/2026-08-01.json",
    "rootlist/2026/06/2026-06-threats.json",
)

EXPECTED_ARCHIVE_COUNTS = {
    "archives/monthly/2026-08.json": (207643, 1027698),
    "archives/weekly/2026-W25.json": (162801, 945701),
    "archives/weekly/2026-W30.json": (188673, 993073),
    "archives/weekly/2026-W31.json": (204015, 1011638),
}

DOMAIN_TOKEN = re.compile(
    r"(?<![a-z0-9-])(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
    r"[a-z]{2,63}(?![a-z0-9-])",
    re.IGNORECASE,
)


def iter_json_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from iter_json_strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from iter_json_strings(item)


def is_protected_domain(value):
    domain = value.strip().lower()
    return (
        domain == "ms.get"
        or domain == "paypal.com"
        or domain.endswith(".paypal.com")
        or domain.endswith(".microsoft")
    )


class FalsePositiveCleanupTests(unittest.TestCase):
    def test_allowlist_has_pattern_and_exact_regressions(self):
        allowlist = set(
            json.loads((PROJECT_ROOT / "allow" / "allowlist.json").read_text())
        )

        self.assertEqual(len(MICROSOFT_DOMAINS), 42)
        self.assertTrue(MICROSOFT_DOMAINS.issubset(allowlist))
        self.assertTrue(
            {".microsoft", ".paypal.com", "ms.get", "paypal.com"}.issubset(
                allowlist
            )
        )

    def test_filter_removes_suffixes_without_touching_lookalikes(self):
        entries = [
            "ms.get",
            "login.microsoft",
            "deep.login.microsoft",
            "paypal.com",
            "www.paypal.com",
            "microsoft.example",
            "paypal.com.example",
            "evil-microsoft.com",
        ]

        filtered, removed = filter_domains(
            entries,
            exact={"ms.get", "paypal.com"},
            patterns={".microsoft", ".paypal.com"},
        )

        self.assertEqual(removed, 5)
        self.assertEqual(
            filtered,
            ["microsoft.example", "paypal.com.example", "evil-microsoft.com"],
        )

    def test_dead_lists_are_cleaning_targets(self):
        relative_targets = {path.relative_to(PROJECT_ROOT).as_posix() for path in TARGETS}
        self.assertIn("community/dead_blocklist.json", relative_targets)
        self.assertIn("dns/dead_domains.json", relative_targets)

    def test_cleanup_workflows_commit_the_cleaned_dead_list(self):
        for relative_path in (
            ".github/workflows/purge.yml",
            ".github/workflows/on_list_update.yml",
        ):
            with self.subTest(workflow=relative_path):
                workflow = (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")
                self.assertIn("community/dead_blocklist.json", workflow)

    def test_allowlist_patterns_are_explicitly_approved(self):
        self.assertEqual(
            utils.APPROVED_ALLOWLIST_PATTERNS, {".microsoft", ".paypal.com"}
        )
        with patch.object(
            utils,
            "load_allowlist",
            return_value={"safe.example", ".microsoft", ".com"},
        ):
            with self.assertRaisesRegex(ValueError, r"unapproved.*\.com"):
                utils.load_allowlist_split()

    def test_historical_data_has_no_protected_domain_values(self):
        findings = []
        for relative_path in HISTORICAL_ARTIFACTS:
            path = PROJECT_ROOT / relative_path
            text = path.read_text(encoding="utf-8-sig")
            try:
                values = iter_json_strings(json.loads(text))
            except json.JSONDecodeError:
                values = DOMAIN_TOKEN.findall(text)
            for value in values:
                if is_protected_domain(value):
                    findings.append(f"{path.relative_to(PROJECT_ROOT)}: {value}")

        self.assertEqual(findings, [])

    def test_historical_aggregate_counts_were_adjusted(self):
        for relative_path, expected in EXPECTED_ARCHIVE_COUNTS.items():
            data = json.loads((PROJECT_ROOT / relative_path).read_text())
            self.assertEqual(
                (data["primary_count"], data["community_count"]), expected
            )

        july_changes = json.loads(
            (PROJECT_ROOT / "changes/2026-07/2026-07-26.json").read_text()
        )
        self.assertEqual(
            (july_changes["primary_count"], july_changes["community_count"]),
            (196172, 1003908),
        )

        august_changes = json.loads(
            (PROJECT_ROOT / "changes/2026-08/2026-08-01.json").read_text()
        )
        self.assertEqual(
            (august_changes["primary_count"], august_changes["community_count"]),
            (207644, 1027699),
        )

        threats = json.loads(
            (PROJECT_ROOT / "rootlist/2026/06/2026-06-threats.json").read_text()
        )
        blank_country = next(
            item for item in threats["top"]["countries"] if item["country"] == ""
        )
        self.assertEqual(threats["meta"]["total"], 8101)
        self.assertEqual(len(threats["threats"]), 8101)
        self.assertEqual(threats["stats"]["enriched"], 8004)
        self.assertEqual(threats["stats"]["vt_rate"], 94.5)
        self.assertEqual(blank_country["count"], 7375)
        self.assertEqual(threats["daily"]["2026-06-14"], 331)


if __name__ == "__main__":
    unittest.main()
