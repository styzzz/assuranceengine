"""Tests for the InfoSec Navigator catalogue and build script.

Run from the repository root:
    python3 -m unittest discover -s infosec-navigator -v
"""
import copy
import json
import os
import unittest

import build

HERE = os.path.dirname(os.path.abspath(__file__))


def load_catalogue():
    with open(build.SOURCE, encoding="utf-8") as f:
        return json.load(f)


class CatalogueTests(unittest.TestCase):
    def setUp(self):
        self.data = load_catalogue()

    def test_real_catalogue_is_valid(self):
        self.assertEqual(build.validate(self.data), [])

    def test_generated_data_js_is_up_to_date(self):
        with open(build.OUTPUT, encoding="utf-8") as f:
            self.assertEqual(f.read(), build.render(self.data),
                             "data.js is stale; run python3 infosec-navigator/build.py")

    def test_every_control_has_evidence_test_and_abstention_rules(self):
        for c in self.data["controls"]:
            with self.subTest(control=c["id"]):
                self.assertTrue(c["evidence"])
                self.assertTrue(c["test"])
                self.assertTrue(c["abstain_when"])
                self.assertTrue(c["pass_criteria"].strip())

    def test_every_evidence_source_is_read_only(self):
        for c in self.data["controls"]:
            for item in c["evidence"]:
                with self.subTest(control=c["id"], source=item["source"]):
                    self.assertEqual(item["access"], "read-only")

    def test_ids_are_unique(self):
        ids = [c["id"] for c in self.data["controls"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_engine_states_match_the_assessment_schema(self):
        with open(os.path.join(HERE, "..", "spec", "finding.schema.json"), encoding="utf-8") as f:
            schema = json.load(f)
        schema_states = set(schema["properties"]["state"]["enum"])
        self.assertEqual(set(self.data["engine_states"]), schema_states)

    def test_risk_values_match_the_assessment_schema(self):
        with open(os.path.join(HERE, "..", "spec", "finding.schema.json"), encoding="utf-8") as f:
            schema = json.load(f)
        self.assertLessEqual({c["default_risk"] for c in self.data["controls"]},
                             set(schema["properties"]["risk"]["enum"]))


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.base = load_catalogue()

    def _control(self, data, cid):
        return next(c for c in data["controls"] if c["id"] == cid)

    def assertInvalid(self, data, fragment):
        errs = build.validate(data)
        self.assertTrue(any(fragment in e for e in errs),
                        f"expected a problem containing {fragment!r}, got {errs}")

    def test_unknown_framework_reference_is_rejected(self):
        d = copy.deepcopy(self.base)
        self._control(d, "ISN-ACC-02")["frameworks"]["iso27001_2022"] = ["9.9"]
        self.assertInvalid(d, "'9.9' is not in iso27001_2022")

    def test_unknown_framework_key_is_rejected(self):
        d = copy.deepcopy(self.base)
        self._control(d, "ISN-ACC-02")["frameworks"]["made_up"] = ["X"]
        self.assertInvalid(d, "unknown framework 'made_up'")

    def test_control_without_mapping_is_rejected(self):
        d = copy.deepcopy(self.base)
        self._control(d, "ISN-ACC-02")["frameworks"] = {}
        self.assertInvalid(d, "needs at least one framework mapping")

    def test_control_without_evidence_is_rejected(self):
        d = copy.deepcopy(self.base)
        self._control(d, "ISN-ACC-02")["evidence"] = []
        self.assertInvalid(d, "needs at least one evidence source")

    def test_write_access_is_rejected(self):
        d = copy.deepcopy(self.base)
        self._control(d, "ISN-ACC-02")["evidence"][0]["access"] = "read-write"
        self.assertInvalid(d, "evidence access must be 'read-only'")

    def test_duplicate_id_is_rejected(self):
        d = copy.deepcopy(self.base)
        d["controls"].append(copy.deepcopy(self._control(d, "ISN-ACC-02")))
        self.assertInvalid(d, "duplicate id")

    def test_id_must_match_domain_code(self):
        d = copy.deepcopy(self.base)
        self._control(d, "ISN-ACC-02")["domain"] = "tech"
        self.assertInvalid(d, "id code should be TEC")

    def test_malformed_id_is_rejected(self):
        d = copy.deepcopy(self.base)
        self._control(d, "ISN-ACC-02")["id"] = "ACC-02"
        self.assertInvalid(d, "id must look like ISN-ABC-01")

    def test_unknown_risk_is_rejected(self):
        d = copy.deepcopy(self.base)
        self._control(d, "ISN-ACC-02")["default_risk"] = "severe"
        self.assertInvalid(d, "default_risk must be one of")

    def test_empty_test_steps_are_rejected(self):
        d = copy.deepcopy(self.base)
        self._control(d, "ISN-ACC-02")["test"] = []
        self.assertInvalid(d, "ISN-ACC-02: test")

    def test_domain_without_controls_is_rejected(self):
        d = copy.deepcopy(self.base)
        d["domains"]["extra"] = {"name": "Empty", "code": "EXT"}
        self.assertInvalid(d, "domain extra has no controls")

    def test_unknown_component_is_rejected(self):
        d = copy.deepcopy(self.base)
        self._control(d, "ISN-ACC-02")["component"] = "marketing"
        self.assertInvalid(d, "unknown component 'marketing'")

    def test_component_without_controls_is_rejected(self):
        d = copy.deepcopy(self.base)
        d["components"]["empty"] = {"name": "Empty", "description": "No controls"}
        self.assertInvalid(d, "component empty has no controls")

    def test_companion_cannot_claim_to_be_built(self):
        d = copy.deepcopy(self.base)
        d["companions"][0]["status"] = "built"
        self.assertInvalid(d, "status must be 'specified' until built")

    def test_companion_needs_its_requirements_listed(self):
        d = copy.deepcopy(self.base)
        d["companions"][0]["requires"] = []
        self.assertInvalid(d, "requires must be a non-empty list")

    def test_every_companion_is_marked_specified(self):
        for comp in self.base["companions"]:
            with self.subTest(companion=comp["name"]):
                self.assertEqual(comp.get("status", "specified"), "specified")

    def test_incomplete_engine_states_are_rejected(self):
        d = copy.deepcopy(self.base)
        del d["engine_states"]["pending_review"]
        self.assertInvalid(d, "exactly the six assessment states")


if __name__ == "__main__":
    unittest.main()
