import json
import re
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import build_dist

NOW = datetime(2026, 11, 22, 7, 30, tzinfo=timezone.utc)


def write(root, rel, content):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if not isinstance(content, str):
        content = json.dumps(content)
    path.write_text(content, encoding="utf-8")


def make_repo(root):
    write(root, "list.json", ["keep.example", "new.example", "readded.example"])
    write(root, "list.txt", "keep.example\nnew.example\nreadded.example\n")
    write(root, "dns/active_domains.json", ["keep.example"])
    write(root, "community/blocklist.json", ["c1.example"])
    write(root, "community/live_blocklist.json", [])
    write(root, "rootlist/formats/primary/hosts.txt", "0.0.0.0 keep.example\n")
    write(root, "rootlist/active_root_domains.json", {"domains": ["keep.example"]})
    write(root, "rootlist/arrays/part_000.json", ["keep.example"])
    write(root, "rootlist/2026/11/2026-11-22.json", {"scan": 1})
    write(root, "rootlist/README.md", "docs")
    write(root, "README.md", "readme")
    write(root, "archives/changes/2026-11/2026-11-21.json", {
        "date": "2026-11-21",
        "primary_added": ["new.example", "gone.example"],
        "primary_removed": ["readded.example"],
        "community_added": [],
        "community_removed": ["c2.example"],
    })
    write(root, "archives/changes/2026-11/2026-11-22.json", {
        "date": "2026-11-22",
        "primary_added": ["readded.example"],
        "primary_removed": ["gone.example"],
        "community_added": ["c1.example"],
        "community_removed": [],
    })


class BuildDistTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "repo"
        self.out = Path(self.tmp.name) / "dist"
        make_repo(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_collect_takes_feeds_and_leaves_history_on_main(self):
        files = {p.as_posix() for p in build_dist.collect(self.root)}
        self.assertIn("list.json", files)
        self.assertIn("rootlist/formats/primary/hosts.txt", files)
        self.assertIn("rootlist/active_root_domains.json", files)
        self.assertIn("rootlist/arrays/part_000.json", files)
        self.assertNotIn("rootlist/2026/11/2026-11-22.json", files)
        self.assertNotIn("archives/changes/2026-11/2026-11-22.json", files)
        self.assertNotIn("README.md", files)
        self.assertNotIn("rootlist/README.md", files)

    def test_hotlist_uses_current_lists_as_ground_truth(self):
        build_dist.build(self.out, "abc123", NOW, root=self.root)
        hot = json.loads((self.out / "hotlist.json").read_text(encoding="utf-8"))
        self.assertEqual(hot["journal_days"], ["2026-11-21", "2026-11-22"])
        self.assertEqual(hot["primary"]["added"], ["new.example", "readded.example"])
        self.assertEqual(hot["primary"]["removed"], ["gone.example"])
        self.assertEqual(hot["community"]["added"], ["c1.example"])
        self.assertEqual(hot["community"]["removed"], ["c2.example"])

    def test_meta_records_source_counts_and_checksums(self):
        meta = build_dist.build(self.out, "abc123", NOW, root=self.root)
        self.assertEqual(meta["source_commit"], "abc123")
        self.assertEqual(meta["counts"]["primary"], 3)
        self.assertEqual(meta["counts"]["primary_active"], 1)
        entry = meta["files"]["list.txt"]
        self.assertEqual(entry["size"], (self.root / "list.txt").stat().st_size)
        self.assertRegex(entry["sha256"], r"^[0-9a-f]{64}$")
        self.assertTrue((self.out / "README.md").is_file())

    def test_same_input_gives_identical_dist(self):
        build_dist.build(self.out, "abc123", NOW, root=self.root)
        first = {p.relative_to(self.out).as_posix(): p.read_bytes() for p in self.out.rglob("*") if p.is_file()}
        build_dist.build(self.out, "abc123", NOW, root=self.root)
        second = {p.relative_to(self.out).as_posix(): p.read_bytes() for p in self.out.rglob("*") if p.is_file()}
        self.assertEqual(first, second)

    def test_build_time_is_taken_in_utc(self):
        now = build_dist.parse_now("2026-11-21T23:30:00-08:00")
        self.assertEqual(now.isoformat(), "2026-11-22T07:30:00+00:00")
        build_dist.build(self.out, "abc123", now, root=self.root)
        hot = json.loads((self.out / "hotlist.json").read_text(encoding="utf-8"))
        self.assertEqual(hot["journal_days"], ["2026-11-21", "2026-11-22"])

    def test_files_over_github_limit_stop_the_build(self):
        with mock.patch.object(build_dist, "GITHUB_FILE_LIMIT", 10):
            with self.assertRaises(SystemExit):
                build_dist.build(self.out, "abc123", NOW, root=self.root)


class WorkflowSafetyTests(unittest.TestCase):
    def read(self, name):
        return (ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8")

    def test_no_workflow_force_pushes_main(self):
        for path in (ROOT / ".github" / "workflows").glob("*.yml"):
            if path.name == "history_maintenance.yml":
                continue
            text = path.read_text(encoding="utf-8")
            with self.subTest(workflow=path.name):
                self.assertNotRegex(text, r"push[^\n]*(--force|-f\b|\+)[^\n]*main")

    def test_dist_workflow_only_replaces_the_dist_branch(self):
        text = self.read("dist.yml")
        pushes = re.findall(r"git push[^\n]*", text)
        self.assertEqual(pushes, ['git push --force origin "$COMMIT:refs/heads/dist"'])
        self.assertIn("cancel-in-progress: true", text)
        self.assertIn("python scripts/build_dist.py", text)

    def test_routine_rebuild_keeps_dist_only_feeds_out_of_main(self):
        text = self.read("on_list_update.yml")
        stage = text[text.index("git add"):text.index("git diff --staged")]
        self.assertIn("rootlist/formats/primary_active/", stage)
        self.assertIn("rootlist/formats/community_active/", stage)
        self.assertIn("community/live_blocklist.txt", stage)
        self.assertIn("archives/changes/", stage)
        self.assertNotRegex(stage, r"rootlist/(\s|\\)")
        self.assertNotIn("community/blocklist.txt", stage)

    def test_scheduled_update_copies_all_feeds_once_a_day(self):
        text = self.read("rootlist.yml")
        daily = text[text.index('if [ "$DAILY_COPY" = true ]'):text.index("git add $ADD_PATHS")]
        self.assertIn("rootlist/", daily)
        self.assertIn("community/blocklist.txt", daily)
        self.assertIn("72000", text)

    def test_purge_still_commits_every_feed(self):
        text = self.read("purge.yml")
        self.assertIn("community/blocklist.txt", text)
        self.assertIn("dns rootlist", text)


if __name__ == "__main__":
    unittest.main()
