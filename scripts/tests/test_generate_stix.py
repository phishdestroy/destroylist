import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location(
    "generate_stix",
    ROOT / "scripts" / "generate_stix.py",
)
STIX = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(STIX)

OLD = "2026-01-01T00:00:00.000Z"
NOW = "2026-10-19T00:00:00.000Z"


def previous_of(*objects):
    previous = {}
    for obj in objects:
        domain = STIX.PATTERN.fullmatch(obj["pattern"]).group(1)
        entry = previous.setdefault(domain, [None, []])
        if obj.get("revoked"):
            entry[1].append(obj)
        else:
            entry[0] = obj
    return previous


def indicators(bundle):
    return {STIX.PATTERN.fullmatch(o["pattern"]).group(1): o
            for o in bundle["objects"] if o["type"] == "indicator"}


class GenerateStixTests(unittest.TestCase):
    def test_bundle_has_no_spec_version(self):
        bundle, _, _ = STIX.build(["a.com"], {}, set(), set(), NOW)
        self.assertNotIn("spec_version", bundle)
        self.assertEqual(bundle["objects"][0]["type"], "identity")

    def test_unchanged_domain_keeps_its_object(self):
        old = STIX.make_indicator("a.com", OLD)
        bundle, active, revoked = STIX.build(["a.com", "b.com"], previous_of(old), set(), set(), NOW)
        found = indicators(bundle)
        self.assertEqual(found["a.com"], old)
        self.assertEqual(found["b.com"]["created"], NOW)
        self.assertEqual((active, revoked), (2, 0))

    def test_allowlisted_domain_is_revoked_not_dropped(self):
        old = STIX.make_indicator("fp.com", OLD)
        bundle, active, revoked = STIX.build(["fp.com"], previous_of(old), {"fp.com"}, set(), NOW)
        found = indicators(bundle)["fp.com"]
        self.assertTrue(found["revoked"])
        self.assertEqual((found["id"], found["created"], found["modified"]), (old["id"], OLD, NOW))
        self.assertEqual((active, revoked), (0, 1))

        # The revocation stays published unchanged on later builds.
        again, _, _ = STIX.build([], previous_of(found), {"fp.com"}, set(), "2026-10-20T00:00:00.000Z")
        self.assertEqual(indicators(again)["fp.com"], found)

    def test_suffix_pattern_applies(self):
        bundle, active, _ = STIX.build(["x.example.org", "bad.com"], {}, set(), {".example.org"}, NOW)
        self.assertEqual(set(indicators(bundle)), {"bad.com"})
        self.assertEqual(active, 1)

    def test_relisted_domain_gets_new_id(self):
        old = STIX.make_indicator("a.com", OLD)
        dead = dict(old, modified=NOW, revoked=True)
        bundle, _, _ = STIX.build(["a.com"], previous_of(dead), set(), set(), NOW)
        found = indicators(bundle)["a.com"]
        self.assertNotEqual(found["id"], old["id"])
        self.assertNotIn("revoked", found)

    def test_dead_domain_is_left_out(self):
        old = STIX.make_indicator("gone.com", OLD)
        bundle, _, _ = STIX.build([], previous_of(old), set(), set(), NOW)
        self.assertEqual(indicators(bundle), {})


if __name__ == "__main__":
    unittest.main()
