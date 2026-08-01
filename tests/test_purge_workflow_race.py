import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def git(cwd, *args, check=True):
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def configure(repo):
    git(repo, "config", "user.email", "test@example.invalid")
    git(repo, "config", "user.name", "test")


def write_allowlist(repo, entries):
    path = repo / "allow" / "allowlist.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sorted(entries), indent=2) + "\n", encoding="utf-8")


class PurgeWorkflowRaceTests(unittest.TestCase):
    def test_every_cleaner_target_is_staged(self):
        workflow = (ROOT / ".github" / "workflows" / "purge.yml").read_text(
            encoding="utf-8"
        )
        cleaner = (ROOT / "scripts" / "validate_and_clean.py").read_text(
            encoding="utf-8"
        )
        targets_block = cleaner.split("TARGETS = [", 1)[1].split("]", 1)[0]
        expected = {
            "list.json",
            "community/blocklist.json",
            "community/live_blocklist.json",
            "community/content_live.json",
            "dns/active_domains.json",
            "dns/content_active.json",
        }
        for target in expected:
            self.assertIn(target.rsplit("/", 1)[-1], targets_block)
            if target.startswith("dns/"):
                self.assertIn("dns rootlist", workflow)
            else:
                self.assertIn(target, workflow)

    def test_workflow_rebuilds_in_retry_and_drops_stale_snapshot_replay(self):
        text = (ROOT / ".github" / "workflows" / "purge.yml").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("processed.tar", text)
        self.assertNotIn("tar -xf", text)
        loop = text.index("for i in {1..5}")
        fetch = text.index("git fetch origin main", loop)
        regenerate = text.index("python scripts/validate_and_clean.py", fetch)
        commit = text.index('git commit -m "$MSG"', regenerate)
        push = text.index("git push origin HEAD:main", commit)
        self.assertLess(loop, fetch)
        self.assertLess(fetch, regenerate)
        self.assertLess(regenerate, commit)
        self.assertLess(commit, push)

    def test_all_generated_list_writers_rebuild_fresh_and_stage_rootlist(self):
        for name, loop_text in (
            ("on_list_update.yml", "for i in {1..10}"),
            ("rootlist.yml", "for i in {1..5}"),
        ):
            with self.subTest(workflow=name):
                text = (ROOT / ".github" / "workflows" / name).read_text(
                    encoding="utf-8"
                )
                self.assertNotIn("processed.tar", text)
                self.assertNotIn("tar -xf", text)
                loop = text.index(loop_text)
                fetch = text.index("git fetch origin main", loop)
                rebuild = text.index("python scripts/validate_and_clean.py", fetch)
                stage = text.index("git add", rebuild)
                push = text.index("git push", stage)
                self.assertLess(fetch, rebuild)
                self.assertLess(rebuild, stage)
                self.assertLess(stage, push)
                self.assertIn("rootlist/", text[rebuild:push])

    def test_repo_write_lock_is_not_held_by_codeberg_mirror(self):
        for name, writer in (
            ("purge.yml", "purge"),
            ("on_list_update.yml", "process"),
        ):
            with self.subTest(workflow=name):
                text = (ROOT / ".github" / "workflows" / name).read_text(
                    encoding="utf-8"
                )
                writer_block, mirror_block = text.split("\n  mirror:\n", 1)
                self.assertIn(f"  {writer}:\n", writer_block)
                self.assertIn("group: repo-updates", writer_block)
                self.assertNotIn("group: codeberg-mirror", writer_block)
                self.assertIn("group: codeberg-mirror", mirror_block)
                self.assertIn("cancel-in-progress: false", mirror_block)
                self.assertIn("ref: main", mirror_block)

    def test_compare_and_swap_retry_preserves_external_pattern(self):
        with tempfile.TemporaryDirectory() as td:
            top = Path(td)
            remote = top / "remote.git"
            seed = top / "seed"
            action = top / "action"
            external = top / "external"
            verify = top / "verify"

            git(top, "init", "--bare", "--initial-branch=main", str(remote))
            git(top, "init", "--initial-branch=main", str(seed))
            configure(seed)
            write_allowlist(seed, ["base.example"])
            git(seed, "add", "allow/allowlist.json")
            git(seed, "commit", "-m", "seed")
            git(seed, "remote", "add", "origin", str(remote))
            git(seed, "push", "-u", "origin", "main")

            git(top, "clone", str(remote), str(action))
            git(top, "clone", str(remote), str(external))
            configure(action)
            configure(external)

            write_allowlist(action, ["base.example", "appeal.example"])
            git(action, "add", "allow/allowlist.json")
            git(action, "commit", "-m", "action attempt 1")

            write_allowlist(external, ["base.example", ".microsoft"])
            git(external, "add", "allow/allowlist.json")
            git(external, "commit", "-m", "external pattern")
            git(external, "push", "origin", "HEAD:main")

            rejected = git(action, "push", "origin", "HEAD:main", check=False)
            self.assertNotEqual(rejected.returncode, 0)

            git(action, "fetch", "origin", "main")
            git(action, "reset", "--hard", "origin/main")
            current = json.loads((action / "allow" / "allowlist.json").read_text())
            self.assertIn(".microsoft", current)
            current.append("appeal.example")
            write_allowlist(action, current)
            git(action, "add", "allow/allowlist.json")
            git(action, "commit", "-m", "action retry")
            git(action, "push", "origin", "HEAD:main")

            git(top, "clone", str(remote), str(verify))
            final = json.loads((verify / "allow" / "allowlist.json").read_text())
            self.assertEqual(
                final,
                [".microsoft", "appeal.example", "base.example"],
            )


if __name__ == "__main__":
    unittest.main()
