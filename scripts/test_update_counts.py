#!/usr/bin/env python3
"""Regression tests for public counter semantics and the metrics manifest."""
import importlib.util
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path


FAKE_ROOT = Path("/tmp/destroylist-counter-test-root")
sys.modules["utils"] = types.SimpleNamespace(
    PROJECT_ROOT=FAKE_ROOT,
    make_badge=lambda label, message, color: {
        "schemaVersion": 1,
        "label": label,
        "message": str(message),
        "color": color,
    },
    save_json=lambda *_args, **_kwargs: None,
    log=lambda *_args, **_kwargs: None,
)
spec = importlib.util.spec_from_file_location(
    "update_counts",
    Path(__file__).with_name("update_counts.py"),
)
update_counts = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(update_counts)


class UpdateCountsTest(unittest.TestCase):
    def test_primary_badge_does_not_claim_liveness(self):
        self.assertEqual(update_counts.SOURCES["primary"]["label"], "Primary Entries")
        self.assertNotIn("Active", update_counts.SOURCES["primary"]["label"])

    def test_count_domains_supports_both_feed_shapes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            flat = root / "flat.json"
            wrapped = root / "wrapped.json"
            flat.write_text(json.dumps(["a.test", "b.test"]), encoding="utf-8")
            wrapped.write_text(json.dumps({"domains": ["a.test"]}), encoding="utf-8")
            self.assertEqual(update_counts.count_domains(flat), 2)
            self.assertEqual(update_counts.count_domains(wrapped), 1)

    def test_manifest_declares_entry_count_semantics(self):
        counts = {name: index + 1 for index, name in enumerate(update_counts.SOURCES)}
        manifest = update_counts.build_metrics(counts, "2026-08-06T00:00:00Z")
        self.assertEqual(manifest["countType"], "feed_entries")
        self.assertEqual(manifest["generatedAt"], "2026-08-06T00:00:00Z")
        self.assertEqual(manifest["counts"]["primary"]["source"], "list.json")
        self.assertIn("not a liveness count", manifest["counts"]["primary"]["definition"])


if __name__ == "__main__":
    unittest.main()
