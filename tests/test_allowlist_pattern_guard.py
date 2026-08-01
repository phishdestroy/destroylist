import importlib.util
import json
import subprocess
import tempfile
import unittest
from contextlib import chdir
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "allowlist_pattern_guard",
    ROOT / "scripts" / "allowlist_pattern_guard.py",
)
GUARD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GUARD)


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
    git(repo, "config", "user.email", "guard-test@example.invalid")
    git(repo, "config", "user.name", "guard-test")


def write_allowlist(repo, entries):
    path = repo / "allow" / "allowlist.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")


def commit_allowlist(repo, entries, message):
    write_allowlist(repo, entries)
    git(repo, "add", "allow/allowlist.json")
    git(repo, "commit", "-m", message)
    return git(repo, "rev-parse", "HEAD").stdout.strip()


class GuardLogicTests(unittest.TestCase):
    def test_detect_allows_additions_and_case_only_normalization(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            git(repo, "init", "--initial-branch=main")
            configure(repo)
            before = commit_allowlist(
                repo,
                ["base.example", ".microsoft", ".PayPal.COM"],
                "before",
            )
            after = commit_allowlist(
                repo,
                ["base.example", "new.example", ".paypal.com"],
                "after",
            )
            with chdir(repo):
                self.assertEqual(GUARD.detect_removed(before, after), [".microsoft"])

    def test_restore_is_append_only_and_idempotent(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "allowlist.json"
            path.write_text(
                json.dumps(["concurrent.example", ".paypal.com"], indent=2),
                encoding="utf-8",
            )
            restored = GUARD.restore_file(path, [".microsoft", ".PAYPAL.COM"])
            self.assertEqual(restored, [".microsoft"])
            final = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(
                final,
                [".microsoft", ".paypal.com", "concurrent.example"],
            )
            self.assertEqual(GUARD.restore_file(path, [".microsoft"]), [])

    def test_detect_rejects_unknown_pattern_in_either_revision(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            git(repo, "init", "--initial-branch=main")
            configure(repo)
            allowed_before = commit_allowlist(
                repo, ["base.example", ".microsoft"], "allowed before"
            )
            unknown = commit_allowlist(
                repo, ["base.example", ".com"], "unknown pattern"
            )
            allowed_after = commit_allowlist(
                repo, ["base.example", ".paypal.com"], "allowed after"
            )
            with chdir(repo):
                with self.assertRaisesRegex(ValueError, r"unapproved.*\.com"):
                    GUARD.detect_removed(allowed_before, unknown)
                with self.assertRaisesRegex(ValueError, r"unapproved.*\.com"):
                    GUARD.detect_removed(unknown, allowed_after)

    def test_restore_rejects_unknown_pattern_in_latest_or_removed_state(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "allowlist.json"
            path.write_text(
                json.dumps(["base.example", ".com"]), encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, r"unapproved.*\.com"):
                GUARD.restore_file(path, [".microsoft"])

            path.write_text(
                json.dumps(["base.example", ".microsoft"]), encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, r"unapproved.*\.com"):
                GUARD.restore_file(path, [".com"])

    def test_malformed_latest_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "allowlist.json"
            for payload in ({"domains": ["example.com"]}, ["example.com", 7]):
                with self.subTest(payload=payload):
                    path.write_text(json.dumps(payload), encoding="utf-8")
                    with self.assertRaises(ValueError):
                        GUARD.restore_file(path, [".microsoft"])


class GuardWorkflowTests(unittest.TestCase):
    def test_workflow_has_permissions_dispatch_and_natural_loop_stop(self):
        workflow = (
            ROOT / ".github" / "workflows" / "allowlist-pattern-guard.yml"
        ).read_text(encoding="utf-8")
        purge = (ROOT / ".github" / "workflows" / "purge.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn('paths:\n      - "allow/allowlist.json"', workflow)
        self.assertIn("contents: write", workflow)
        self.assertIn("actions: write", workflow)
        self.assertIn("for i in {1..5}", workflow)
        self.assertIn("git reset --hard origin/main", workflow)
        self.assertIn("git push origin HEAD:main", workflow)
        self.assertIn("actions/workflows/purge.yml/dispatches", workflow)
        self.assertNotIn("if: github.actor", workflow)
        self.assertIn("required: false", purge)
        self.assertIn('default: ""', purge)

    def test_cas_retry_preserves_concurrent_changes(self):
        with tempfile.TemporaryDirectory() as td:
            top = Path(td)
            remote = top / "remote.git"
            seed = top / "seed"
            guard = top / "guard"
            writer = top / "writer"
            verify = top / "verify"

            git(top, "init", "--bare", "--initial-branch=main", str(remote))
            git(top, "init", "--initial-branch=main", str(seed))
            configure(seed)
            before = commit_allowlist(
                seed,
                ["base.example", ".microsoft"],
                "seed with pattern",
            )
            git(seed, "remote", "add", "origin", str(remote))
            git(seed, "push", "-u", "origin", "main")

            after = commit_allowlist(seed, ["base.example"], "remove pattern")
            git(seed, "push", "origin", "HEAD:main")

            git(top, "clone", str(remote), str(guard))
            git(top, "clone", str(remote), str(writer))
            configure(guard)
            configure(writer)
            with chdir(guard):
                self.assertEqual(GUARD.detect_removed(before, after), [".microsoft"])

            GUARD.restore_file(guard / "allow" / "allowlist.json", [".microsoft"])
            git(guard, "add", "allow/allowlist.json")
            git(guard, "commit", "-m", "guard attempt 1")

            commit_allowlist(
                writer,
                ["base.example", "concurrent.example"],
                "concurrent addition",
            )
            git(writer, "push", "origin", "HEAD:main")
            rejected = git(guard, "push", "origin", "HEAD:main", check=False)
            self.assertNotEqual(rejected.returncode, 0)

            git(guard, "fetch", "origin", "main")
            git(guard, "reset", "--hard", "origin/main")
            self.assertEqual(
                GUARD.restore_file(guard / "allow" / "allowlist.json", [".microsoft"]),
                [".microsoft"],
            )
            git(guard, "add", "allow/allowlist.json")
            git(guard, "commit", "-m", "guard retry")
            git(guard, "push", "origin", "HEAD:main")

            git(top, "clone", str(remote), str(verify))
            final = json.loads((verify / "allow" / "allowlist.json").read_text())
            self.assertEqual(
                final,
                [".microsoft", "base.example", "concurrent.example"],
            )


if __name__ == "__main__":
    unittest.main()
