"""Exercise badge periods and real Git additions independently of live feeds."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import calculate_stats as stats


class StatisticsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.override = patch.object(stats, "PROJECT_ROOT", self.root)
        self.override.start()
        self.git("init", "-q")
        self.git("config", "user.name", "Stats test")
        self.git("config", "user.email", "test@example.invalid")

    def tearDown(self):
        self.override.stop()
        self.tmp.cleanup()

    def git(self, *args, env=None):
        return subprocess.check_output(["git", *args], cwd=self.root, env=env, text=True)

    def commit(self, domains, at):
        (self.root / "list.json").write_text(json.dumps(domains))
        self.git("add", "list.json")
        env = dict(os.environ, GIT_AUTHOR_DATE=at, GIT_COMMITTER_DATE=at)
        self.git("commit", "-qm", "fixture", env=env)

    def test_additions_are_not_cancelled_by_removals(self):
        self.commit(["a.invalid", "b.invalid", "c.invalid"], "2026-11-05T23:59:00Z")
        self.commit(["b.invalid", "c.invalid", "d.invalid"], "2026-11-06T01:00:00Z")
        self.assertEqual(stats.get_domains_added_since("list.json", "2026-11-06T00:00:00Z"), 1)

    def test_today_excludes_previous_calendar_day(self):
        self.commit(["a.invalid", "b.invalid"], "2026-11-05T01:00:00Z")
        self.commit(["a.invalid", "b.invalid", "c.invalid"], "2026-11-05T23:59:00Z")
        self.assertEqual(stats.get_domains_added_since("list.json", "2026-11-06T00:00:00Z"), 0)

    def test_missing_history_is_not_a_measured_zero(self):
        self.commit(["a.invalid", "b.invalid"], "2026-11-06T01:00:00Z")
        self.assertIsNone(stats.get_domains_added_since("list.json", "2026-11-06T00:00:00Z"))

    def test_zero_does_not_fall_back_to_old_snapshot(self):
        self.assertEqual(stats.pick_count(0, 42), 0)
        self.assertEqual(stats.pick_count(None, 42), 42)
        self.assertEqual(stats.format_count(None), "unavailable")

    def test_snapshot_must_match_current_period(self):
        with patch.object(stats, "load_snapshot", return_value={
            "today_date": "2026-11-05", "today_primary": 90, "today_community": 180
        }):
            self.assertEqual(stats.get_delta_from_snapshot(
                "today_primary", "today_community", 100, 200,
                "today_date", "2026-11-06"), (None, None))

    def test_calendar_boundaries_use_utc(self):
        now = datetime.fromisoformat("2026-11-07T00:30:00+01:00")
        self.assertEqual(stats.calendar_windows(now), {
            "today": "2026-11-06T00:00:00+00:00",
            "week": "2026-11-02T00:00:00+00:00",
            "month": "2026-11-01T00:00:00+00:00",
        })

    def test_counters_only_leaves_archives_untouched(self):
        with patch.object(stats, "DNS_DIR", self.root), \
             patch.object(stats, "load_current_domains", return_value={"a.invalid"}), \
             patch.object(stats, "get_domains_added_since", return_value=0), \
             patch.object(stats, "get_delta_from_snapshot", return_value=(None, None)), \
             patch.object(stats, "save_json") as save, \
             patch.object(stats, "save_snapshot"), \
             patch.object(stats, "save_daily_diff") as daily, \
             patch.object(stats, "save_archive") as archive:
            stats.main(counters_only=True)
        daily.assert_not_called()
        archive.assert_not_called()
        self.assertEqual(save.call_count, 6)
        self.assertTrue(all(c.args[1]["message"] == "+0" for c in save.call_args_list))


if __name__ == "__main__":
    unittest.main()
