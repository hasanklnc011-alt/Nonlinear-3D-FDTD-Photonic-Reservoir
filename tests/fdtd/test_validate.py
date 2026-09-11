import contextlib
import copy
import io
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from fdtd.provenance import cli, schema
from fdtd.provenance.schema import CandidateStudyManifest, blank_manifest
from fdtd.provenance.validate import (
    STATUS_FAIL,
    STATUS_INFO,
    STATUS_PASS,
    StudyProvenanceIncomplete,
    validate_study,
)
from tests.fdtd._fixtures import complete_manifest

CHECK_ORDER = (
    "schema",
    "identity",
    "candidate_family",
    "material.source",
    "nonlinear.model",
    "geometry.hash",
    "convergence.mesh",
    "convergence.time",
    "convergence.pml",
    "flex_credit",
    "task_ids",
    "evidence",
)


class _Tmp(unittest.TestCase):
    def setUp(self):
        self._d = TemporaryDirectory()
        self.tmp = Path(self._d.name)
        self.addCleanup(self._d.cleanup)


class CompleteManifestTest(_Tmp):
    def setUp(self):
        super().setUp()
        self.m = complete_manifest(self.tmp)
        self.report = validate_study(self.m)
        self.by_name = {c.name: c for c in self.report.checks}

    def test_ok(self):
        self.assertTrue(self.report.ok, self.report.format_text())
        self.assertEqual(self.report.failed, [])

    def test_check_order(self):
        self.assertEqual(tuple(c.name for c in self.report.checks), CHECK_ORDER)

    def test_require_complete_does_not_raise(self):
        self.report.require_complete()

    def test_ladders_pass(self):
        for dim in ("mesh", "time", "pml"):
            self.assertEqual(self.by_name[f"convergence.{dim}"].status, STATUS_PASS)

    def test_flex_credit_pass_with_actual(self):
        self.assertEqual(self.by_name["flex_credit"].status, STATUS_PASS)

    def test_deterministic(self):
        self.assertEqual(validate_study(self.m).to_dict(), validate_study(self.m).to_dict())

    def test_to_dict_shape(self):
        d = self.report.to_dict()
        self.assertTrue(d["ok"])
        self.assertEqual(d["n_checks"], len(CHECK_ORDER))
        self.assertEqual(d["n_failed"], 0)


class BlankManifestFailsClosedTest(unittest.TestCase):
    def setUp(self):
        self.report = validate_study(blank_manifest())
        self.by_name = {c.name: c for c in self.report.checks}

    def test_not_ok(self):
        self.assertFalse(self.report.ok)

    def test_require_complete_raises(self):
        with self.assertRaises(StudyProvenanceIncomplete):
            self.report.require_complete()

    def test_required_evidence_checks_fail_closed(self):
        # schema is the one thing a blank template gets right.
        self.assertEqual(self.by_name["schema"].status, STATUS_PASS)
        must_fail = (
            "identity", "candidate_family", "material.source", "nonlinear.model",
            "geometry.hash", "convergence.mesh", "convergence.time",
            "convergence.pml", "flex_credit",
        )
        for name in must_fail:
            self.assertEqual(self.by_name[name].status, STATUS_FAIL, name)
        # nothing is referenced yet, so these two have nothing to check but the
        # report is still not ok because of the failures above.
        self.assertEqual(self.by_name["task_ids"].status, STATUS_INFO)
        self.assertEqual(self.by_name["evidence"].status, STATUS_INFO)

    def test_candidate_family_check_notes_astra_owns_it(self):
        c = self.by_name["candidate_family"]
        self.assertEqual(c.status, STATUS_FAIL)
        self.assertIn("Astra", " ".join(c.details))


class SingleFieldRemovalTest(_Tmp):
    """Knocking out any one required piece must flip the report to not-ok."""

    def _run(self, mutate):
        m = complete_manifest(self.tmp)
        mutate(m)
        return validate_study(m)

    def test_removing_each_piece_breaks_validation(self):
        mutations = {
            "study_id": lambda m: setattr(m, "study_id", None),
            "tidy3d_version": lambda m: setattr(m, "tidy3d_version", "  "),
            "candidate_family": lambda m: setattr(m, "candidate_family", None),
            "material": lambda m: setattr(m, "material", None),
            "material.reference": lambda m: setattr(m.material, "reference", None),
            "nonlinear": lambda m: setattr(m, "nonlinear", None),
            "geometry.geometry_hash": lambda m: setattr(m.geometry, "geometry_hash", None),
            "flex_credit": lambda m: setattr(m, "flex_credit", None),
            "mesh ladder": lambda m: m.ladders.pop(0),
            "evidence_paths": lambda m: setattr(m, "evidence_paths", []),
        }
        for label, mutate in mutations.items():
            report = self._run(mutate)
            self.assertFalse(report.ok, f"{label!r} should have broken validation")

    def test_bad_source_kind_fails_material(self):
        r = self._run(lambda m: setattr(m.material, "source_kind", "guess"))
        c = {x.name: x for x in r.checks}["material.source"]
        self.assertEqual(c.status, STATUS_FAIL)
        self.assertIn("source_kind", c.summary)

    def test_bad_digest_format_fails(self):
        r = self._run(lambda m: setattr(m.material, "parameter_digest", "not-a-hash"))
        self.assertEqual({x.name: x for x in r.checks}["material.source"].status, STATUS_FAIL)

    def test_nonlinear_medium_mismatch_fails(self):
        r = self._run(lambda m: setattr(m.nonlinear, "applies_to_medium", "OTHER"))
        c = {x.name: x for x in r.checks}["nonlinear.model"]
        self.assertEqual(c.status, STATUS_FAIL)
        self.assertIn("applies_to_medium", c.summary)

    def test_non_monotonic_ladder_fails(self):
        def mutate(m):
            m.ladders[0].rungs[1].grid_cells_per_wavelength = 5.0  # 10 -> 5 -> 30
        c = {x.name: x for x in self._run(mutate).checks}["convergence.mesh"]
        self.assertEqual(c.status, STATUS_FAIL)

    def test_unconverged_ladder_fails(self):
        def mutate(m):
            m.ladders[1].rungs[-1].observable_value = 5.0
        c = {x.name: x for x in self._run(mutate).checks}["convergence.time"]
        self.assertEqual(c.status, STATUS_FAIL)
        self.assertIn("not converged", c.summary)

    def test_cost_over_ceiling_fails(self):
        def mutate(m):
            m.flex_credit.approved_ceiling = 1.0  # actual_total is 3.3
        c = {x.name: x for x in self._run(mutate).checks}["flex_credit"]
        self.assertEqual(c.status, STATUS_FAIL)
        self.assertIn("exceeds approved ceiling", c.summary)

    def test_missing_ceiling_fails(self):
        c = {x.name: x for x in self._run(lambda m: setattr(m.flex_credit, "approved_ceiling", None)).checks}["flex_credit"]
        self.assertEqual(c.status, STATUS_FAIL)

    def test_orphan_task_id_fails(self):
        def mutate(m):
            m.task_ids = ["task-estimate-0"]  # drop the rung task ids
        c = {x.name: x for x in self._run(mutate).checks}["task_ids"]
        self.assertEqual(c.status, STATUS_FAIL)
        self.assertIn("not listed", c.summary)

    def test_actual_without_task_id_fails_ladder(self):
        def mutate(m):
            m.ladders[0].rungs[-1].task_id = None  # keeps flex_credit_actual
        c = {x.name: x for x in self._run(mutate).checks}["convergence.mesh"]
        self.assertEqual(c.status, STATUS_FAIL)
        self.assertIn("no task_id", c.summary)

    def test_digests_without_evidence_paths_fails_evidence(self):
        c = {x.name: x for x in self._run(lambda m: setattr(m, "evidence_paths", [])).checks}["evidence"]
        self.assertEqual(c.status, STATUS_FAIL)

    def test_evidence_path_not_on_disk_fails(self):
        def mutate(m):
            m.evidence_paths = [str(self.tmp / "does-not-exist.json")]
        c = {x.name: x for x in self._run(mutate).checks}["evidence"]
        self.assertEqual(c.status, STATUS_FAIL)
        self.assertIn("not found", c.summary)

    def test_extra_ladder_dimension_flagged(self):
        def mutate(m):
            extra = copy.deepcopy(m.ladders[0])
            extra.dimension = "frequency"
            m.ladders.append(extra)
        r = self._run(mutate)
        self.assertIn("convergence.extra", {c.name for c in r.checks})
        self.assertFalse(r.ok)


class PreSubmissionStateTest(_Tmp):
    """Before anything is submitted: no task ids, no actuals -> INFO, still not ok."""

    def test_pre_submission_task_ids_info_but_ladders_still_required(self):
        m = complete_manifest(self.tmp)
        for lad in m.ladders:
            for r in lad.rungs:
                r.task_id = None
                r.flex_credit_actual = None
        m.flex_credit.actual_total = None
        m.flex_credit.estimate_task_ids = []
        m.task_ids = []
        report = validate_study(m)
        by = {c.name: c for c in report.checks}
        self.assertEqual(by["task_ids"].status, STATUS_INFO)
        self.assertEqual(by["flex_credit"].status, STATUS_INFO)
        # ladders still converge on the made-up observable values -> overall ok
        self.assertTrue(report.ok, report.format_text())


class CliTest(_Tmp):
    def _capture(self, argv):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = cli.main(argv)
        return code, buf.getvalue()

    def test_template_then_validate_is_fail_closed(self):
        out = self.tmp / "study.json"
        code, _ = self._capture(["template", "--out", str(out)])
        self.assertEqual(code, 0)
        self.assertTrue(out.exists())
        code, text = self._capture(["validate", "--manifest", str(out)])
        self.assertEqual(code, 1)
        self.assertIn("INCOMPLETE", text)

    def test_validate_complete_manifest_exit_zero(self):
        path = self.tmp / "complete.json"
        path.write_text(complete_manifest(self.tmp).to_json(), encoding="utf-8")
        code, text = self._capture(["validate", "--manifest", str(path)])
        self.assertEqual(code, 0, text)
        self.assertIn("OK", text)

    def test_validate_json_output(self):
        path = self.tmp / "complete.json"
        path.write_text(complete_manifest(self.tmp).to_json(), encoding="utf-8")
        code, text = self._capture(["validate", "--manifest", str(path), "--json"])
        self.assertEqual(code, 0)
        payload = json.loads(text)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["n_checks"], len(CHECK_ORDER))

    def test_validate_missing_file_exit_two(self):
        code, _ = self._capture(["validate", "--manifest", str(self.tmp / "nope.json")])
        self.assertEqual(code, 2)

    def test_validate_unreadable_manifest_exit_two(self):
        bad = self.tmp / "bad.json"
        bad.write_text('{"schema": "x", "unknown_field": 1}', encoding="utf-8")
        code, _ = self._capture(["validate", "--manifest", str(bad)])
        self.assertEqual(code, 2)

    def test_digest_matches_hashlib(self):
        f = self.tmp / "art.json"
        f.write_bytes(b"content-here")
        code, text = self._capture(["digest", str(f)])
        self.assertEqual(code, 0)
        self.assertIn(schema.sha256_bytes(b"content-here"), text)

    def test_parser_registers_subcommands(self):
        for name, func in (("template", cli.cmd_template),
                           ("validate", cli.cmd_validate),
                           ("digest", cli.cmd_digest)):
            args = cli.build_parser().parse_args(
                [name] + (["--manifest", "x"] if name == "validate" else
                          ["p"] if name == "digest" else [])
            )
            self.assertIs(args.func, func)


if __name__ == "__main__":
    unittest.main()
