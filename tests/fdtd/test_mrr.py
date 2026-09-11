"""Tests for the fdtd.mrr silicon-microring study-builder scaffold.

Every value in this file is synthetic. Medium labels are obvious test strings
(``SYN_*``), digests are hashes of literal placeholder bytes, and the geometry
dimensions are round made-up numbers chosen only to be dimensionally valid. No
physical silicon / nonlinear constant appears anywhere.
"""

from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from fdtd.mrr import (
    ConfigError,
    GeometryError,
    MicroringStudyBuilder,
    MissingEvidenceError,
    RingResonatorGeometry,
    SimulationConfig,
    StudyIdentity,
)
from fdtd.mrr.config import CONFIG_SCHEMA_ID
from fdtd.mrr.geometry import GEOMETRY_SCHEMA_ID
from fdtd.provenance import schema
from fdtd.provenance.schema import (
    CandidateStudyManifest,
    FlexCreditBudget,
    MaterialSource,
    NonlinearModel,
    SCHEMA_ID,
)
from fdtd.provenance.validate import validate_study

MAT_DIGEST = schema.sha256_text("PLACEHOLDER-mrr-material-parameters")
NL_DIGEST = schema.sha256_text("PLACEHOLDER-mrr-nonlinear-parameters")


def make_geometry(**over) -> RingResonatorGeometry:
    base = dict(
        ring_outer_radius_um=7.0,
        waveguide_width_um=0.5,
        waveguide_thickness_um=0.3,
        bus_waveguide_width_um=0.45,
        coupling_gap_um=0.2,
        bus_length_um=20.0,
        cladding_thickness_um=2.0,
        box_thickness_um=3.0,
        substrate_thickness_um=4.0,
        domain_padding_um=1.5,
        add_drop=True,
        core_medium="SYN_CORE",
        cladding_medium="SYN_CLAD",
        box_medium="SYN_BOX",
        substrate_medium="SYN_SUB",
    )
    base.update(over)
    return RingResonatorGeometry(**base)


def make_config(**over) -> SimulationConfig:
    base = dict(
        wavelength_range_um=[1.5, 1.6],
        boundary_types={"x": "pml", "y": "pml", "z": "pml"},
        symmetry=[0, 0, 0],
        sources=["mode:bus_through:in"],
        monitors=["flux:bus_through:out", "flux:bus_drop:out"],
    )
    base.update(over)
    return SimulationConfig(**base)


def make_material(**over) -> MaterialSource:
    base = dict(
        name="SYN_CORE",
        dispersion_model="PoleResidue",
        source_kind="tidy3d_material_library",
        reference="syn/library#SYN_CORE",
        version="test-1",
        retrieved_utc="2026-09-10",
        parameter_digest=MAT_DIGEST,
        wavelength_range_um=[1.4, 1.7],
    )
    base.update(over)
    return MaterialSource(**base)


def make_nonlinear(**over) -> NonlinearModel:
    base = dict(
        model_type="KerrNonlinearity",
        source_kind="literature",
        reference="syn/doi",
        version="test-1",
        parameter_digest=NL_DIGEST,
        applies_to_medium="SYN_CORE",
    )
    base.update(over)
    return NonlinearModel(**base)


def make_builder(**over) -> MicroringStudyBuilder:
    kw = dict(
        identity=StudyIdentity(study_id="mrr-syn-001", created_utc="2026-09-10T00:00:00Z"),
        geometry=make_geometry(),
        config=make_config(),
        material=make_material(),
        nonlinear=make_nonlinear(),
    )
    kw.update(over)
    return MicroringStudyBuilder(**kw)


# --------------------------------------------------------------------------- #
class GeometryDeterminismTest(unittest.TestCase):
    def test_digest_is_hex64_and_reproducible(self):
        d1 = make_geometry().digest()
        d2 = make_geometry().digest()
        self.assertEqual(d1, d2)
        self.assertTrue(schema.looks_like_sha256(d1))

    def test_digest_independent_of_field_ordering(self):
        forward = dict(
            ring_outer_radius_um=7.0, waveguide_width_um=0.5, waveguide_thickness_um=0.3,
            bus_waveguide_width_um=0.45, coupling_gap_um=0.2, bus_length_um=20.0,
            cladding_thickness_um=2.0, box_thickness_um=3.0, substrate_thickness_um=4.0,
            domain_padding_um=1.5, add_drop=True, core_medium="SYN_CORE",
            cladding_medium="SYN_CLAD", box_medium="SYN_BOX", substrate_medium="SYN_SUB",
        )
        reordered = dict(reversed(list(forward.items())))
        self.assertEqual(
            RingResonatorGeometry(**forward).digest(),
            RingResonatorGeometry(**reordered).digest(),
        )

    def test_any_value_change_changes_digest(self):
        base = make_geometry().digest()
        for change in (
            dict(ring_outer_radius_um=7.5),
            dict(coupling_gap_um=0.21),
            dict(add_drop=False),
            dict(core_medium="SYN_CORE_2"),
            dict(domain_padding_um=1.6),
        ):
            self.assertNotEqual(make_geometry(**change).digest(), base, change)

    def test_structures_are_deterministic_and_topology_aware(self):
        g_add_drop = make_geometry(add_drop=True)
        self.assertEqual(g_add_drop.to_structures(), g_add_drop.to_structures())
        names_ad = [s["name"] for s in g_add_drop.to_structures()]
        names_single = [s["name"] for s in make_geometry(add_drop=False).to_structures()]
        self.assertIn("bus_drop", names_ad)
        self.assertNotIn("bus_drop", names_single)

    def test_document_shape(self):
        doc = make_geometry().to_document()
        self.assertEqual(doc["schema"], GEOMETRY_SCHEMA_ID)
        self.assertEqual(doc["units"], "um")
        self.assertEqual(len(doc["derived"]["domain_size_um"]), 3)
        self.assertTrue(all(x > 0 for x in doc["derived"]["domain_size_um"]))
        # no optical constants leaked into the structure medium fields
        for s in doc["structures"]:
            self.assertIsInstance(s["medium"], str)

    def test_validate_rejects_impossible_geometry(self):
        for bad in (
            dict(ring_outer_radius_um=0.0),
            dict(waveguide_thickness_um=-1.0),
            dict(coupling_gap_um=-0.1),
            dict(waveguide_width_um=9.0),          # width >= radius -> inner radius <= 0
            dict(core_medium="  "),
            dict(bus_length_um=float("inf")),
        ):
            with self.assertRaises(GeometryError, msg=bad):
                make_geometry(**bad).validate()

    def test_validate_returns_self_when_ok(self):
        g = make_geometry()
        self.assertIs(g.validate(), g)


class ConfigDeterminismTest(unittest.TestCase):
    def test_digest_reproducible_and_hex64(self):
        self.assertEqual(make_config().digest(), make_config().digest())
        self.assertTrue(schema.looks_like_sha256(make_config().digest()))

    def test_boundary_key_order_does_not_matter(self):
        a = make_config(boundary_types={"x": "pml", "y": "pml", "z": "absorber"})
        b = make_config(boundary_types={"z": "absorber", "y": "pml", "x": "pml"})
        self.assertEqual(a.digest(), b.digest())

    def test_any_value_change_changes_digest(self):
        base = make_config().digest()
        for change in (
            dict(wavelength_range_um=[1.5, 1.7]),
            dict(boundary_types={"x": "pml", "y": "pml", "z": "absorber"}),
            dict(symmetry=[0, -1, 0]),
            dict(monitors=["flux:bus_through:out"]),
            dict(sources=["mode:bus_through:in", "mode:bus_drop:in"]),
        ):
            self.assertNotEqual(make_config(**change).digest(), base, change)

    def test_document_declares_discretisation_deferred(self):
        doc = make_config().to_document()
        self.assertEqual(doc["schema"], CONFIG_SCHEMA_ID)
        self.assertEqual(doc["discretisation"], "deferred-to-convergence-ladders")
        self.assertTrue(make_config().mesh_is_deferred)
        self.assertTrue(make_config().run_time_is_deferred)

    def test_validate_rejects_bad_config(self):
        for bad in (
            dict(wavelength_range_um=[1.6, 1.5]),
            dict(wavelength_range_um=[0.0, 1.5]),
            dict(boundary_types={"x": "pml", "y": "pml"}),
            dict(boundary_types={"x": "pml", "y": "pml", "z": "mystery"}),
            dict(symmetry=[2, 0, 0]),
            dict(symmetry=[0, 0]),
            dict(sources=[]),
            dict(monitors=[""]),
        ):
            with self.assertRaises(ConfigError, msg=bad):
                make_config(**bad).validate()


class RequiredEvidenceFailClosedTest(unittest.TestCase):
    def test_blank_material_fails_closed(self):
        b = make_builder(material=MaterialSource())
        with self.assertRaises(MissingEvidenceError) as cm:
            b.require_evidence()
        problems = " ".join(cm.exception.problems)
        for fld in ("material.name", "material.parameter_digest", "material.source_kind"):
            self.assertIn(fld, problems)
        with self.assertRaises(MissingEvidenceError):
            b.build_manifest()

    def test_blank_nonlinear_fails_closed(self):
        b = make_builder(nonlinear=NonlinearModel())
        with self.assertRaises(MissingEvidenceError) as cm:
            b.build_manifest()
        problems = " ".join(cm.exception.problems)
        self.assertIn("nonlinear.model_type", problems)
        self.assertIn("nonlinear.parameter_digest", problems)

    def test_non_sha256_digest_rejected(self):
        b = make_builder(material=make_material(parameter_digest="not-a-real-hash"))
        self.assertTrue(any("not a sha256" in p for p in b.evidence_problems()))

    def test_source_kind_outside_vocabulary_rejected(self):
        b = make_builder(nonlinear=make_nonlinear(source_kind="guessed"))
        self.assertTrue(any("source_kind" in p for p in b.evidence_problems()))

    def test_geometry_core_medium_must_match_material_name(self):
        b = make_builder(geometry=make_geometry(core_medium="SOMETHING_ELSE"))
        self.assertTrue(any("core_medium" in p for p in b.evidence_problems()))

    def test_nonlinear_medium_must_match_material_name(self):
        b = make_builder(nonlinear=make_nonlinear(applies_to_medium="OTHER"))
        self.assertTrue(any("applies_to_medium" in p for p in b.evidence_problems()))

    def test_invalid_geometry_propagates_into_evidence_problems(self):
        b = make_builder(geometry=make_geometry(coupling_gap_um=-1.0))
        self.assertTrue(any(p.startswith("geometry:") for p in b.evidence_problems()))

    def test_invalid_config_propagates_into_evidence_problems(self):
        b = make_builder(config=make_config(symmetry=[9, 9, 9]))
        self.assertTrue(any(p.startswith("config:") for p in b.evidence_problems()))

    def test_complete_evidence_passes_the_gate(self):
        b = make_builder()
        self.assertEqual(b.evidence_problems(), [])
        self.assertIsNone(b.require_evidence())
        self.assertIsInstance(b.build_manifest(), CandidateStudyManifest)


class ManifestShapeTest(unittest.TestCase):
    def setUp(self):
        self.builder = make_builder()
        self.m = self.builder.build_manifest()

    def test_schema_and_identity(self):
        self.assertEqual(self.m.schema, SCHEMA_ID)
        self.assertEqual(self.m.study_id, "mrr-syn-001")
        self.assertEqual(self.m.created_utc, "2026-09-10T00:00:00Z")

    def test_candidate_family_left_for_astra(self):
        self.assertIsNone(self.m.candidate_family)

    def test_ladders_emitted_empty(self):
        self.assertEqual([l.dimension for l in self.m.ladders], ["mesh", "time", "pml"])
        for l in self.m.ladders:
            self.assertEqual(l.rungs, [])
            self.assertIsNone(l.tolerance_rel)

    def test_flex_credit_blank_and_no_tasks(self):
        self.assertEqual(self.m.flex_credit, FlexCreditBudget())
        self.assertEqual(self.m.task_ids, [])

    def test_geometry_hash_is_the_geometry_digest(self):
        self.assertEqual(self.m.geometry.geometry_hash, self.builder.geometry_digest())
        self.assertEqual(self.m.geometry.hash_algorithm, "sha256")
        self.assertEqual(self.m.geometry.units, "um")

    def test_supplied_evidence_is_carried_verbatim(self):
        self.assertIs(self.m.material, self.builder.material)
        self.assertIs(self.m.nonlinear, self.builder.nonlinear)

    def test_notes_record_both_digests_and_the_incompleteness(self):
        self.assertIn(self.builder.geometry_digest(), self.m.notes)
        self.assertIn(self.builder.config_digest(), self.m.notes)
        self.assertIn("INCOMPLETE BY DESIGN", self.m.notes)

    def test_manifest_round_trips_through_json(self):
        again = CandidateStudyManifest.from_json(self.m.to_json())
        self.assertEqual(again.to_dict(), self.m.to_dict())

    def test_manifest_is_incomplete_by_design(self):
        report = validate_study(self.m)
        self.assertFalse(report.ok)
        failed = {c.name for c in report.failed}
        for name in ("candidate_family", "convergence.mesh", "convergence.time",
                     "convergence.pml", "flex_credit", "identity"):
            self.assertIn(name, failed)

    def test_identity_tidy3d_version_flows_through_when_supplied(self):
        b = make_builder(identity=StudyIdentity(
            study_id="x", created_utc="2026-09-10T00:00:00Z", tidy3d_version="9.9.9-test"))
        self.assertEqual(b.build_manifest().tidy3d_version, "9.9.9-test")

    def test_evidence_paths_pass_through(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "si_params.json"
            p.write_text("PLACEHOLDER", encoding="utf-8")
            b = make_builder(evidence_paths=[str(p)])
            self.assertEqual(b.build_manifest().evidence_paths, [str(p)])


class NoCloudTest(unittest.TestCase):
    MRR_DIR = Path(__file__).resolve().parents[2] / "fdtd" / "mrr"
    FORBIDDEN_IMPORT = re.compile(
        r"^\s*(?:import|from)\s+"
        r"(tidy3d|requests|httpx|urllib|http|socket|ssl|boto3|paramiko|websocket|aiohttp)\b",
        re.MULTILINE,
    )

    def test_no_network_or_tidy3d_imports_in_source(self):
        files = sorted(self.MRR_DIR.glob("*.py"))
        self.assertTrue(files)
        for f in files:
            hits = self.FORBIDDEN_IMPORT.findall(f.read_text(encoding="utf-8"))
            self.assertEqual(hits, [], f"{f.name} imports {hits}")

    def test_importing_the_package_does_not_pull_in_tidy3d(self):
        import fdtd.mrr  # noqa: F401

        self.assertNotIn("tidy3d", sys.modules)

    def test_built_manifest_has_no_cloud_artifacts(self):
        m = make_builder().build_manifest()
        self.assertEqual(m.task_ids, [])
        self.assertTrue(all(l.rungs == [] for l in m.ladders))
        self.assertIsNone(m.flex_credit.actual_total)
        # no rung carries a task id or an actual cost
        self.assertEqual(
            [r for l in m.ladders for r in l.rungs], []
        )


if __name__ == "__main__":
    unittest.main()
