import unittest
from tempfile import TemporaryDirectory
from pathlib import Path

from fdtd.provenance import schema
from fdtd.provenance.schema import (
    CandidateStudyManifest,
    ConvergenceLadder,
    ConvergenceRung,
    FlexCreditBudget,
    SCHEMA_ID,
    blank_manifest,
    canonical_geometry_digest,
    looks_like_sha256,
    sha256_bytes,
    sha256_text,
)
from tests.fdtd._fixtures import complete_manifest


class HashHelpersTest(unittest.TestCase):
    def test_sha256_helpers_agree_and_are_hex64(self):
        self.assertEqual(sha256_text("abc"), sha256_bytes(b"abc"))
        self.assertTrue(looks_like_sha256(sha256_text("abc")))

    def test_looks_like_sha256_rejects_non_digests(self):
        for bad in (None, "", "xyz", "A" * 64, sha256_text("a") + "0", 123):
            self.assertFalse(looks_like_sha256(bad), bad)

    def test_canonical_geometry_digest_is_key_order_insensitive(self):
        a = canonical_geometry_digest({"x": 1, "y": [2, 3]})
        b = canonical_geometry_digest({"y": [2, 3], "x": 1})
        self.assertEqual(a, b)
        self.assertNotEqual(a, canonical_geometry_digest({"x": 1, "y": [2, 4]}))

    def test_sha256_file(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "f.txt"
            p.write_bytes(b"payload")
            self.assertEqual(schema.sha256_file(p), sha256_bytes(b"payload"))


class RoundTripTest(unittest.TestCase):
    def test_blank_manifest_round_trips(self):
        m = blank_manifest()
        again = CandidateStudyManifest.from_json(m.to_json())
        self.assertEqual(again.to_dict(), m.to_dict())
        self.assertEqual(again.schema, SCHEMA_ID)
        self.assertEqual(len(again.ladders), 3)
        self.assertIsNotNone(again.material)

    def test_complete_manifest_round_trips(self):
        with TemporaryDirectory() as d:
            m = complete_manifest(Path(d))
            again = CandidateStudyManifest.from_json(m.to_json())
            self.assertEqual(again.to_dict(), m.to_dict())
            self.assertEqual(again.nonlinear.applies_to_medium, "SYN_MAT")
            self.assertEqual(again.ladders[0].rungs[-1].task_id, "task-mesh-2")

    def test_from_dict_rejects_unknown_fields(self):
        with self.assertRaises(ValueError):
            CandidateStudyManifest.from_dict({"schema": SCHEMA_ID, "bogus": 1})

    def test_from_dict_rejects_non_object_leaf(self):
        with self.assertRaises(TypeError):
            CandidateStudyManifest.from_dict({"material": "not-an-object"})


class LadderLogicTest(unittest.TestCase):
    def _ladder(self, dim, refine, obs, tol):
        field = {"mesh": "grid_cells_per_wavelength",
                 "time": "steps_per_period", "pml": "pml_layers"}[dim]
        rungs = [ConvergenceRung(**{field: rp}, observable="o", observable_value=ov)
                 for rp, ov in zip(refine, obs)]
        return ConvergenceLadder(dimension=dim, tolerance_rel=tol, rungs=rungs)

    def test_converged_true_when_change_within_tolerance(self):
        lad = self._ladder("mesh", [10, 20, 40], [1.0, 1.05, 1.051], 0.01)
        self.assertTrue(lad.refinement_is_monotonic())
        self.assertLess(lad.last_relative_change(), 0.01)
        self.assertTrue(lad.converged())

    def test_not_converged_when_change_exceeds_tolerance(self):
        lad = self._ladder("mesh", [10, 20, 40], [1.0, 1.2, 1.5], 0.01)
        self.assertFalse(lad.converged())

    def test_not_converged_when_refinement_not_monotonic(self):
        lad = self._ladder("time", [40, 20, 80], [0.5, 0.5, 0.5], 0.01)
        self.assertFalse(lad.refinement_is_monotonic())
        self.assertFalse(lad.converged())

    def test_not_converged_with_single_rung_or_bad_tolerance(self):
        one = self._ladder("mesh", [10], [1.0], 0.01)
        self.assertIsNone(one.last_relative_change())
        self.assertFalse(one.converged())
        bad = self._ladder("mesh", [10, 20], [1.0, 1.0], 0.0)
        self.assertFalse(bad.converged())

    def test_refinement_parameter_dispatch(self):
        r = ConvergenceRung(grid_cells_per_wavelength=12.0, steps_per_period=30.0, pml_layers=8)
        self.assertEqual(r.refinement_parameter("mesh"), 12.0)
        self.assertEqual(r.refinement_parameter("time"), 30.0)
        self.assertEqual(r.refinement_parameter("pml"), 8.0)


class FlexCreditLogicTest(unittest.TestCase):
    def test_within_ceiling_prefers_actual_then_estimate(self):
        self.assertTrue(FlexCreditBudget(estimated_total=5, actual_total=9, approved_ceiling=10).within_ceiling())
        self.assertFalse(FlexCreditBudget(estimated_total=5, actual_total=11, approved_ceiling=10).within_ceiling())
        self.assertTrue(FlexCreditBudget(estimated_total=5, approved_ceiling=10).within_ceiling())

    def test_within_ceiling_none_when_unknown(self):
        self.assertIsNone(FlexCreditBudget(estimated_total=5).within_ceiling())
        self.assertIsNone(FlexCreditBudget(approved_ceiling=10).within_ceiling())


if __name__ == "__main__":
    unittest.main()
