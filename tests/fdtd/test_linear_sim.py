"""Tests for the fdtd.mrr local linear-simulation translation layer.

Every value in this file is synthetic. Medium labels are obvious test strings
(``SYN_*``), permittivity / conductivity numbers are round made-up values chosen
only to be dimensionally valid, digests are 64-hex placeholders, and the
wavelengths are a synthetic band around 2 um that deliberately does not match any
real silicon telecom value. No physical constant appears anywhere.
"""

from __future__ import annotations

import copy
import json
import re
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from fdtd.mrr import (
    DiscretizationSpec,
    ExcitationSpec,
    LinearMaterialTable,
    LinearMediumValue,
    LinearSimulationPlan,
    LinearSimulationTranslator,
    MissingLinearEvidenceError,
    RingResonatorGeometry,
    SimulationConfig,
    TranslationError,
    dry_run,
)
from fdtd.mrr.linear_sim import LINEAR_INPUT_SCHEMA_ID, LINEAR_SIM_SCHEMA_ID, StudyIdentity
from fdtd.mrr.linear_dryrun import DryRunReport, LinearPlanIncomplete
from fdtd.provenance import schema


GEO = dict(
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

CONFIG = dict(
    wavelength_range_um=[1.8, 2.2],
    boundary_types={"x": "pml", "y": "pml", "z": "pml"},
    symmetry=[0, 0, 0],
    sources=["mode:bus_through:in"],
    monitors=["flux:bus_through:out", "flux:bus_drop:out"],
)

EXCITATION = dict(center_wavelength_um=2.0, bandwidth_wavelength_um=0.2, num_freqs=201)

DISCRETIZATION = dict(
    grid_min_steps_per_wavelength=20.0,
    grid_wavelength_um=2.0,
    run_time_seconds=2e-12,
    field_decay_shutoff=1e-5,
    boundary_num_layers=12,
)


def _material(label: str, eps: float, digest_seed: str) -> dict:
    return dict(
        medium_label=label,
        model="non_dispersive",
        relative_permittivity=eps,
        conductivity=0.0,
        evidence_digest=schema.sha256_text(f"PLACEHOLDER-{digest_seed}"),
        evidence_reference=f"syn/ref#{label}",
        wavelength_range_um=[1.7, 2.3],
    )


def make_bundle(**over) -> dict:
    bundle = {
        "schema": LINEAR_INPUT_SCHEMA_ID,
        "identity": {"study_id": "mrr-syn-lin-001", "created_utc": "2026-09-10T00:00:00Z"},
        "geometry": dict(GEO),
        "config": copy.deepcopy(CONFIG),
        "materials": [
            _material("SYN_CORE", 9.0, "core"),
            _material("SYN_CLAD", 2.1, "clad"),
            _material("SYN_BOX", 2.1, "box"),
            _material("SYN_SUB", 9.0, "sub"),
        ],
        "background_medium_label": "SYN_CLAD",
        "excitation": dict(EXCITATION),
        "discretization": dict(DISCRETIZATION),
    }
    bundle.update(copy.deepcopy(over))
    return bundle


def make_translator(**over) -> LinearSimulationTranslator:
    return LinearSimulationTranslator.from_bundle(make_bundle(**over))


# --------------------------------------------------------------------------- #
class TranslationHappyPathTest(unittest.TestCase):
    def setUp(self):
        self.plan = make_translator().translate()
        self.doc = self.plan.document

    def test_plan_schema_and_target(self):
        self.assertEqual(self.doc["schema"], LINEAR_SIM_SCHEMA_ID)
        self.assertEqual(self.doc["tidy3d_target"], "tidy3d.Simulation")
        self.assertEqual(self.doc["linearity"], "linear")

    def test_domain_matches_geometry(self):
        geom = RingResonatorGeometry(**GEO)
        self.assertEqual(self.doc["domain"]["size_um"], geom.domain_size_um())
        self.assertEqual(len(self.doc["domain"]["center_um"]), 3)

    def test_every_structure_medium_is_a_concrete_value_not_a_label(self):
        self.assertTrue(self.doc["structures"])
        for s in self.doc["structures"]:
            med = s["medium"]
            self.assertEqual(med["type"], "Medium")
            self.assertEqual(med["model"], "non_dispersive")
            self.assertGreater(med["permittivity"], 0)
            self.assertGreaterEqual(med["conductivity"], 0)
            self.assertTrue(schema.looks_like_sha256(med["evidence"]["digest"]))
            self.assertIsInstance(s["medium_label"], str)

    def test_core_structures_get_the_core_medium_value(self):
        core_eps = 9.0
        for s in self.doc["structures"]:
            if s["medium_label"] == "SYN_CORE":
                self.assertEqual(s["medium"]["permittivity"], core_eps)

    def test_background_medium_is_the_named_one(self):
        self.assertEqual(self.doc["background_medium"]["permittivity"], 2.1)

    def test_boundary_spec_maps_config_types(self):
        for axis in ("x", "y", "z"):
            entry = self.doc["boundary_spec"][axis]
            self.assertEqual(entry["config_type"], "pml")
            self.assertEqual(entry["kind"], "PML")
            self.assertEqual(entry["num_layers"], 12)

    def test_sources_and_monitors_are_parsed_from_tokens(self):
        self.assertEqual([s["token"] for s in self.doc["sources"]], ["mode:bus_through:in"])
        self.assertEqual(
            [m["token"] for m in self.doc["monitors"]],
            ["flux:bus_through:out", "flux:bus_drop:out"],
        )
        for port in self.doc["sources"] + self.doc["monitors"]:
            # a plane: exactly one zero extent
            self.assertEqual(sum(1 for v in port["plane_size_um"] if v == 0), 1)

    def test_grid_and_run_time_are_the_supplied_discretisation(self):
        self.assertEqual(self.doc["grid_spec"]["min_steps_per_wavelength"], 20.0)
        self.assertEqual(self.doc["run_time_s"], 2e-12)
        self.assertEqual(self.doc["field_decay_shutoff"], 1e-5)

    def test_provenance_carries_geometry_and_config_hashes(self):
        geom = RingResonatorGeometry(**GEO)
        cfg = SimulationConfig(**CONFIG)
        self.assertEqual(self.doc["provenance"]["geometry_hash"], geom.digest())
        self.assertEqual(self.doc["provenance"]["config_hash"], cfg.digest())

    def test_provenance_is_linear_and_cloud_free(self):
        prov = self.doc["provenance"]
        self.assertIs(prov["linear_only"], True)
        self.assertIsNone(prov["nonlinear"])
        self.assertEqual(prov["cloud"]["task_ids"], [])
        self.assertIsNone(prov["cloud"]["flex_credit"])
        for flag in ("uploaded", "estimated", "started", "monitored", "downloaded"):
            self.assertFalse(prov["cloud"][flag])

    def test_single_bus_topology_drops_the_drop_monitor_structure(self):
        b = make_bundle()
        b["geometry"]["add_drop"] = False
        b["config"]["monitors"] = ["flux:bus_through:out"]
        doc = LinearSimulationTranslator.from_bundle(b).translate().document
        names = {s["name"] for s in doc["structures"]}
        self.assertNotIn("bus_drop", names)


class PortPlaneGeometryTest(unittest.TestCase):
    """The port plane of a source / monitor must sit on the centreline of the
    ring / bus its token names, not on the domain axis.

    Cloud rung-0 evidence produced ``flux:bus_through:out`` and
    ``flux:bus_drop:out`` both at ``y = 0``; the drop bus never reaches the
    domain axis, so the linear result was rejected in physical acceptance. The
    off-injection-axis coordinates are now derived from the structure centre.
    """

    def setUp(self):
        self.geom = RingResonatorGeometry(**GEO)
        self.doc = make_translator().translate().document
        self.ports = {p["token"]: p for p in self.doc["sources"] + self.doc["monitors"]}
        # centre of the silicon core in z (substrate + BOX + half the film)
        self.z_core = (
            GEO["substrate_thickness_um"]
            + GEO["box_thickness_um"]
            + GEO["waveguide_thickness_um"] / 2.0
        )

    def _structure_center(self, name: str) -> list:
        for s in self.geom.to_structures():
            if s["name"] == name:
                return list(s["center_um"])
        raise AssertionError(name)

    def test_through_and_drop_monitor_y_coordinates_differ(self):
        through = self.ports["flux:bus_through:out"]["plane_center_um"]
        drop = self.ports["flux:bus_drop:out"]["plane_center_um"]
        # the regression: they must not collapse onto the same transverse line
        self.assertNotEqual(through[1], drop[1])
        # and specifically onto opposite sides of the ring
        self.assertLess(through[1], 0.0)
        self.assertGreater(drop[1], 0.0)
        self.assertAlmostEqual(through[1], -self.geom.bus_centre_offset_um)
        self.assertAlmostEqual(drop[1], self.geom.bus_centre_offset_um)

    def test_every_port_plane_is_centred_on_its_named_structure(self):
        for token, port in self.ports.items():
            _kind, structure, _p = token.split(":")
            cx, cy, cz = self._structure_center(structure)
            px, py, pz = port["plane_center_um"]
            # transverse coordinates come straight from the structure centre
            self.assertAlmostEqual(py, cy, msg=token)
            self.assertAlmostEqual(pz, cz, msg=token)
            self.assertAlmostEqual(pz, self.z_core, msg=token)
            # injection axis: half a bus length either side of the centre
            half = self.geom.bus_length_um / 2.0
            self.assertAlmostEqual(abs(px - cx), half, msg=token)

    def test_source_on_through_bus_is_on_the_through_centreline(self):
        src = self.ports["mode:bus_through:in"]
        self.assertAlmostEqual(src["plane_center_um"][1], -self.geom.bus_centre_offset_um)
        self.assertEqual(src["plane_center_um"][2], self.doc["monitors"][0]["plane_center_um"][2])

    def test_port_planes_stay_out_of_the_pml_region(self):
        # domain half-extents; a plane must be at least one padding margin inside
        size = self.geom.domain_size_um()
        pad = GEO["domain_padding_um"]
        for token, port in self.ports.items():
            px, py, pz = port["plane_center_um"]
            self.assertLessEqual(abs(px), size[0] / 2.0 - pad + 1e-9, token)
            self.assertLess(abs(py), size[1] / 2.0, token)
            self.assertGreater(pz, 0.0, token)
            self.assertLess(pz, size[2], token)

    def test_field_monitor_plane_also_follows_its_structure(self):
        b = make_bundle()
        b["config"]["monitors"] = ["field:bus_drop:out", "flux:bus_through:out"]
        doc = LinearSimulationTranslator.from_bundle(b).translate().document
        by_token = {m["token"]: m for m in doc["monitors"]}
        self.assertEqual(by_token["field:bus_drop:out"]["type"], "FieldMonitor")
        self.assertAlmostEqual(
            by_token["field:bus_drop:out"]["plane_center_um"][1],
            self.geom.bus_centre_offset_um,
        )
        self.assertNotEqual(
            by_token["field:bus_drop:out"]["plane_center_um"][1],
            by_token["flux:bus_through:out"]["plane_center_um"][1],
        )

    def test_port_planes_are_deterministic(self):
        a = make_translator().translate().document
        c = make_translator().translate().document
        self.assertEqual(
            [p["plane_center_um"] for p in a["sources"] + a["monitors"]],
            [p["plane_center_um"] for p in c["sources"] + c["monitors"]],
        )

    def test_single_bus_source_and_monitor_share_one_centreline(self):
        b = make_bundle()
        b["geometry"]["add_drop"] = False
        b["config"]["monitors"] = ["flux:bus_through:out"]
        doc = LinearSimulationTranslator.from_bundle(b).translate().document
        geom = RingResonatorGeometry(**{**GEO, "add_drop": False})
        for p in doc["sources"] + doc["monitors"]:
            self.assertAlmostEqual(p["plane_center_um"][1], -geom.bus_centre_offset_um)

    def test_dry_run_still_passes_with_structure_derived_planes(self):
        report = make_translator().translate().dry_run()
        self.assertTrue(report.ok, report.format_text())


class PortPlaneSizeTest(unittest.TestCase):
    """The port plane *extent* of a source / monitor must hug the named bus, not
    span the whole domain transverse cross section.

    Cloud rung-0b evidence: every ``ModeSource`` / ``FluxMonitor`` /
    ``FieldMonitor`` plane was sized ``[0, domain_y, domain_z]``, so it swept in
    the other guide's power and the substrate / cladding slabs and the linear
    resonance acceptance was rejected. The transverse size is now derived
    mechanically from ``bus_waveguide_width_um`` / ``waveguide_thickness_um``
    plus one ``domain_padding_um`` margin on each side.
    """

    def setUp(self):
        self.geom = RingResonatorGeometry(**GEO)
        b = make_bundle()
        b["config"]["monitors"] = [
            "flux:bus_through:out",
            "flux:bus_drop:out",
            "field:bus_drop:out",
        ]
        self.doc = LinearSimulationTranslator.from_bundle(b).translate().document
        self.ports = {p["token"]: p for p in self.doc["sources"] + self.doc["monitors"]}
        self.exp_y = GEO["bus_waveguide_width_um"] + 2.0 * GEO["domain_padding_um"]
        self.exp_z = GEO["waveguide_thickness_um"] + 2.0 * GEO["domain_padding_um"]

    def test_every_port_plane_size_is_derived_from_bus_geometry(self):
        for token, port in self.ports.items():
            sx, sy, sz = port["plane_size_um"]
            self.assertEqual(sx, 0.0, token)
            self.assertAlmostEqual(sy, self.exp_y, msg=token)
            self.assertAlmostEqual(sz, self.exp_z, msg=token)

    def test_mode_source_flux_and_field_monitors_all_use_the_same_rule(self):
        kinds = {p["type"] for p in self.doc["sources"] + self.doc["monitors"]}
        self.assertEqual(kinds, {"ModeSource", "FluxMonitor", "FieldMonitor"})
        sizes = {tuple(p["plane_size_um"]) for p in self.doc["sources"] + self.doc["monitors"]}
        self.assertEqual(sizes, {(0.0, self.exp_y, self.exp_z)})

    def test_plane_no_longer_spans_the_whole_domain_cross_section(self):
        size = self.geom.domain_size_um()
        for token, port in self.ports.items():
            _sx, sy, sz = port["plane_size_um"]
            self.assertLess(sy, size[1], token)
            self.assertLess(sz, size[2], token)

    def test_plane_size_tracks_only_the_geometry_it_is_derived_from(self):
        base = make_translator().translate().document["sources"][0]["plane_size_um"]
        # a param the size does NOT depend on: nothing changes
        wider_sub = make_translator(
            geometry={**GEO, "substrate_thickness_um": 9.0}
        ).translate().document["sources"][0]["plane_size_um"]
        self.assertEqual(base, wider_sub)
        # params the size DOES depend on: it moves by exactly the right amount
        wider_bus = make_translator(
            geometry={**GEO, "bus_waveguide_width_um": GEO["bus_waveguide_width_um"] + 0.1}
        ).translate().document["sources"][0]["plane_size_um"]
        self.assertAlmostEqual(wider_bus[1], base[1] + 0.1)
        self.assertAlmostEqual(wider_bus[2], base[2])
        more_pad = make_translator(
            geometry={**GEO, "domain_padding_um": GEO["domain_padding_um"] + 0.25}
        ).translate().document["sources"][0]["plane_size_um"]
        self.assertAlmostEqual(more_pad[1], base[1] + 0.5)
        self.assertAlmostEqual(more_pad[2], base[2] + 0.5)

    def test_derived_plane_stays_inside_the_domain(self):
        size = self.geom.domain_size_um()
        for token, port in self.ports.items():
            _cx, cy, cz = port["plane_center_um"]
            _sx, sy, sz = port["plane_size_um"]
            self.assertLessEqual(abs(cy) + sy / 2.0, size[1] / 2.0 + 1e-9, token)
            self.assertGreaterEqual(cz - sz / 2.0, -1e-9, token)
            self.assertLessEqual(cz + sz / 2.0, size[2] + 1e-9, token)

    def test_plane_leaving_the_domain_fails_closed(self):
        # padding larger than substrate + BOX pushes the vertical plane span
        # below z = 0, i.e. out of the domain: translation must refuse.
        over = {"geometry": {**GEO, "domain_padding_um": 8.0}}
        with self.assertRaises(MissingLinearEvidenceError) as cm:
            make_translator(**over).translate()
        self.assertTrue(
            any("leaves the domain" in p for p in cm.exception.problems),
            cm.exception.problems,
        )

    def test_validator_rejects_a_plane_whose_face_is_in_the_boundary_margin(self):
        # unit-test the fail-closed guard directly: a physically-derived plane
        # always lands its face at the geometry edge, but the guard must still
        # reject an injection face that has been pushed into the PML margin.
        tr = make_translator()
        size = self.geom.domain_size_um()
        bad = {
            "plane_center_um": [size[0] / 2.0 - 0.1, -self.geom.bus_centre_offset_um, self.geom.domain_size_um()[2] / 2.0],
            "plane_size_um": [0.0, self.exp_y, self.exp_z],
        }
        problems = tr._port_plane_problems("bus_through", "out", bad)
        self.assertTrue(any("boundary margin" in p for p in problems), problems)

    def test_derived_plane_size_is_deterministic(self):
        a = make_translator().translate().document
        c = make_translator().translate().document
        self.assertEqual(
            [p["plane_size_um"] for p in a["sources"] + a["monitors"]],
            [p["plane_size_um"] for p in c["sources"] + c["monitors"]],
        )

    def test_dry_run_still_passes_with_bus_sized_planes(self):
        b = make_bundle()
        b["config"]["monitors"] = ["flux:bus_through:out", "field:bus_drop:out"]
        report = LinearSimulationTranslator.from_bundle(b).translate().dry_run()
        self.assertTrue(report.ok, report.format_text())


class DeterminismTest(unittest.TestCase):
    def test_digest_is_hex64_and_reproducible(self):
        d1 = make_translator().translate().digest()
        d2 = make_translator().translate().digest()
        self.assertEqual(d1, d2)
        self.assertTrue(schema.looks_like_sha256(d1))

    def test_digest_independent_of_bundle_key_ordering(self):
        forward = make_bundle()
        reordered = {k: forward[k] for k in reversed(list(forward))}
        reordered["geometry"] = {k: forward["geometry"][k] for k in reversed(list(forward["geometry"]))}
        self.assertEqual(
            LinearSimulationTranslator.from_bundle(forward).translate().digest(),
            LinearSimulationTranslator.from_bundle(reordered).translate().digest(),
        )

    def test_any_material_value_change_changes_the_digest(self):
        base = make_translator().translate().digest()
        b = make_bundle()
        b["materials"][0]["relative_permittivity"] = 9.5
        self.assertNotEqual(LinearSimulationTranslator.from_bundle(b).translate().digest(), base)

    def test_any_geometry_or_discretisation_change_changes_the_digest(self):
        base = make_translator().translate().digest()
        for over in (
            {"geometry": {**GEO, "ring_outer_radius_um": 7.5}},
            {"discretization": {**DISCRETIZATION, "run_time_seconds": 3e-12}},
            {"excitation": {**EXCITATION, "center_wavelength_um": 2.01}},
            {"background_medium_label": "SYN_SUB"},
        ):
            self.assertNotEqual(make_translator(**over).translate().digest(), base, over)

    def test_plan_round_trips_through_json(self):
        plan = make_translator().translate()
        again = json.loads(plan.to_json())
        self.assertEqual(again, plan.document)
        self.assertEqual(dry_run(again).ok, dry_run(plan.document).ok)


class RequiredEvidenceFailClosedTest(unittest.TestCase):
    def test_missing_material_entry_fails_closed(self):
        b = make_bundle()
        b["materials"] = b["materials"][:3]  # drop SYN_SUB
        with self.assertRaises(MissingLinearEvidenceError) as cm:
            LinearSimulationTranslator.from_bundle(b).translate()
        self.assertTrue(any("SYN_SUB" in p for p in cm.exception.problems))

    def test_blank_permittivity_fails_closed(self):
        b = make_bundle()
        b["materials"][0]["relative_permittivity"] = None
        with self.assertRaises(MissingLinearEvidenceError) as cm:
            LinearSimulationTranslator.from_bundle(b).translate()
        self.assertTrue(any("relative_permittivity" in p for p in cm.exception.problems))

    def test_negative_conductivity_fails_closed(self):
        b = make_bundle()
        b["materials"][1]["conductivity"] = -1.0
        with self.assertRaises(MissingLinearEvidenceError):
            LinearSimulationTranslator.from_bundle(b).translate()

    def test_non_sha256_evidence_digest_rejected(self):
        b = make_bundle()
        b["materials"][0]["evidence_digest"] = "not-a-real-hash"
        problems = make_translator().evidence_problems()  # sanity: happy path is clean
        self.assertEqual(problems, [])
        with self.assertRaises(MissingLinearEvidenceError) as cm:
            LinearSimulationTranslator.from_bundle(b).translate()
        self.assertTrue(any("evidence_digest" in p for p in cm.exception.problems))

    def test_missing_evidence_reference_rejected(self):
        b = make_bundle()
        b["materials"][0]["evidence_reference"] = "  "
        with self.assertRaises(MissingLinearEvidenceError):
            LinearSimulationTranslator.from_bundle(b).translate()

    def test_missing_discretisation_fails_closed(self):
        b = make_bundle()
        b["discretization"]["run_time_seconds"] = None
        with self.assertRaises(MissingLinearEvidenceError) as cm:
            LinearSimulationTranslator.from_bundle(b).translate()
        self.assertTrue(any("run_time_seconds" in p for p in cm.exception.problems))

    def test_absent_discretisation_block_fails_closed(self):
        b = make_bundle()
        del b["discretization"]
        with self.assertRaises(MissingLinearEvidenceError):
            LinearSimulationTranslator.from_bundle(b)

    def test_missing_excitation_fails_closed(self):
        b = make_bundle()
        b["excitation"]["num_freqs"] = None
        with self.assertRaises(MissingLinearEvidenceError) as cm:
            LinearSimulationTranslator.from_bundle(b).translate()
        self.assertTrue(any("num_freqs" in p for p in cm.exception.problems))

    def test_impossible_geometry_propagates(self):
        b = make_bundle()
        b["geometry"]["coupling_gap_um"] = -1.0
        with self.assertRaises(MissingLinearEvidenceError) as cm:
            LinearSimulationTranslator.from_bundle(b).translate()
        self.assertTrue(any(p.startswith("geometry:") for p in cm.exception.problems))

    def test_bad_config_propagates(self):
        b = make_bundle()
        b["config"]["symmetry"] = [9, 9, 9]
        with self.assertRaises(MissingLinearEvidenceError) as cm:
            LinearSimulationTranslator.from_bundle(b).translate()
        self.assertTrue(any(p.startswith("config:") for p in cm.exception.problems))

    def test_background_label_must_be_a_geometry_medium(self):
        b = make_bundle()
        b["background_medium_label"] = "SOMETHING_ELSE"
        with self.assertRaises(MissingLinearEvidenceError) as cm:
            LinearSimulationTranslator.from_bundle(b).translate()
        self.assertTrue(any("background_medium_label" in p for p in cm.exception.problems))

    def test_excitation_band_must_fit_material_windows(self):
        b = make_bundle()
        b["materials"][0]["wavelength_range_um"] = [1.95, 2.3]  # excludes 1.9
        with self.assertRaises(MissingLinearEvidenceError) as cm:
            LinearSimulationTranslator.from_bundle(b).translate()
        self.assertTrue(any("validity window" in p for p in cm.exception.problems))

    def test_excitation_band_must_fit_config_range(self):
        b = make_bundle()
        b["config"]["wavelength_range_um"] = [1.95, 2.05]  # excludes the 1.9..2.1 band
        with self.assertRaises(MissingLinearEvidenceError) as cm:
            LinearSimulationTranslator.from_bundle(b).translate()
        self.assertTrue(any("config.wavelength_range_um" in p for p in cm.exception.problems))

    def test_source_token_referencing_unknown_structure_rejected(self):
        b = make_bundle()
        b["config"]["sources"] = ["mode:not_a_bus:in"]
        with self.assertRaises(MissingLinearEvidenceError) as cm:
            LinearSimulationTranslator.from_bundle(b).translate()
        self.assertTrue(any("not_a_bus" in p for p in cm.exception.problems))

    def test_monitor_token_with_wrong_kind_rejected(self):
        b = make_bundle()
        b["config"]["monitors"] = ["mode:bus_through:out"]
        with self.assertRaises(MissingLinearEvidenceError) as cm:
            LinearSimulationTranslator.from_bundle(b).translate()
        self.assertTrue(any("kind" in p for p in cm.exception.problems))


class NoNonlinearNoInventionTest(unittest.TestCase):
    def test_bundle_with_nonlinear_block_is_rejected(self):
        for key in ("nonlinear", "kerr", "tpa", "chi3", "free_carrier"):
            b = make_bundle()
            b[key] = {"anything": 1}
            with self.assertRaises(TranslationError) as cm:
                LinearSimulationTranslator.from_bundle(b)
            self.assertIn("LINEAR", str(cm.exception))

    def test_unknown_bundle_key_is_rejected(self):
        b = make_bundle()
        b["mystery"] = 1
        with self.assertRaises(TranslationError):
            LinearSimulationTranslator.from_bundle(b)

    def test_no_physical_constant_is_emitted(self):
        doc = make_translator().translate().document
        blob = json.dumps(doc)
        # the plan stays in the caller's units; no hard-coded c / eps0 / mu0
        self.assertNotIn("299792458", blob)
        self.assertNotIn("8.854", blob)
        self.assertEqual(doc["units"], {"length": "um", "time": "s"})

    def test_source_values_are_exactly_the_caller_inputs(self):
        doc = make_translator().translate().document
        pulse = doc["sources"][0]["pulse"]
        self.assertEqual(pulse["center_wavelength_um"], EXCITATION["center_wavelength_um"])
        self.assertEqual(pulse["bandwidth_wavelength_um"], EXCITATION["bandwidth_wavelength_um"])
        self.assertEqual(doc["monitors"][0]["sampling"]["num_freqs"], EXCITATION["num_freqs"])


class DryRunTest(unittest.TestCase):
    def test_complete_bundle_passes_dry_run(self):
        report = make_translator().translate().dry_run()
        self.assertIsInstance(report, DryRunReport)
        self.assertTrue(report.ok, report.format_text())
        report.require_ok()  # does not raise

    def test_dry_run_is_deterministic_text(self):
        a = make_translator().translate().dry_run().format_text()
        b = make_translator().translate().dry_run().format_text()
        self.assertEqual(a, b)

    def test_dry_run_flags_injected_nonlinear_content(self):
        plan = make_translator().translate()
        doc = copy.deepcopy(plan.document)
        doc["structures"][0]["medium"]["kerr_nonlinearity"] = {"n2": 1.0}
        report = dry_run(doc)
        self.assertFalse(report.ok)
        self.assertIn("linear_only", {c.name for c in report.failed})

    def test_dry_run_flags_cloud_task_ids(self):
        doc = copy.deepcopy(make_translator().translate().document)
        doc["provenance"]["cloud"]["task_ids"] = ["fdve-123"]
        report = dry_run(doc)
        self.assertFalse(report.ok)
        self.assertIn("no_cloud", {c.name for c in report.failed})

    def test_dry_run_flags_structure_that_does_not_fit(self):
        doc = copy.deepcopy(make_translator().translate().document)
        doc["domain"]["size_um"] = [1.0, 1.0, 1.0]
        report = dry_run(doc)
        self.assertFalse(report.ok)
        self.assertIn("structures_fit", {c.name for c in report.failed})

    def test_dry_run_flags_wavelength_mismatch(self):
        doc = copy.deepcopy(make_translator().translate().document)
        doc["provenance"]["material_evidence"]["SYN_CORE"]["wavelength_range_um"] = [2.05, 2.3]
        report = dry_run(doc)
        self.assertFalse(report.ok)
        self.assertIn("wavelength_consistency", {c.name for c in report.failed})

    def test_dry_run_flags_missing_medium_evidence(self):
        doc = copy.deepcopy(make_translator().translate().document)
        doc["structures"][0]["medium"]["evidence"]["digest"] = "short"
        report = dry_run(doc)
        self.assertFalse(report.ok)
        self.assertIn("media", {c.name for c in report.failed})

    def test_require_ok_raises_on_failure(self):
        doc = copy.deepcopy(make_translator().translate().document)
        doc["schema"] = "wrong"
        with self.assertRaises(LinearPlanIncomplete):
            dry_run(doc).require_ok()

    def test_report_to_dict_is_json_serialisable(self):
        d = make_translator().translate().dry_run().to_dict()
        json.dumps(d)
        self.assertIn("checks", d)
        self.assertEqual(d["n_failed"], 0)


class DirectApiTest(unittest.TestCase):
    def test_translator_constructor_matches_from_bundle(self):
        b = make_bundle()
        from_bundle = LinearSimulationTranslator.from_bundle(b).translate().digest()
        direct = LinearSimulationTranslator(
            identity=StudyIdentity(study_id="mrr-syn-lin-001", created_utc="2026-09-10T00:00:00Z"),
            geometry=RingResonatorGeometry(**GEO),
            config=SimulationConfig(**CONFIG),
            materials=LinearMaterialTable(entries=[LinearMediumValue(**m) for m in b["materials"]]),
            background_medium_label="SYN_CLAD",
            excitation=ExcitationSpec(**EXCITATION),
            discretization=DiscretizationSpec(**DISCRETIZATION),
        ).translate().digest()
        self.assertEqual(from_bundle, direct)

    def test_medium_value_problems_lists_every_missing_field(self):
        problems = LinearMediumValue().problems()
        joined = " ".join(problems)
        for token in ("medium_label", "model", "relative_permittivity", "conductivity", "evidence_digest"):
            self.assertIn(token, joined)


class NoCloudSourceTest(unittest.TestCase):
    MRR_DIR = Path(__file__).resolve().parents[2] / "fdtd" / "mrr"
    FORBIDDEN_IMPORT = re.compile(
        r"^\s*(?:import|from)\s+"
        r"(tidy3d|requests|httpx|urllib|http|socket|ssl|boto3|paramiko|websocket|aiohttp)\b",
        re.MULTILINE,
    )

    def test_new_modules_have_no_network_or_tidy3d_imports(self):
        for name in ("linear_sim.py", "linear_dryrun.py", "__main__.py"):
            f = self.MRR_DIR / name
            hits = self.FORBIDDEN_IMPORT.findall(f.read_text(encoding="utf-8"))
            self.assertEqual(hits, [], f"{name} imports {hits}")

    def test_importing_does_not_pull_in_tidy3d(self):
        import fdtd.mrr.linear_sim  # noqa: F401
        import fdtd.mrr.linear_dryrun  # noqa: F401

        self.assertNotIn("tidy3d", sys.modules)

    def test_plan_has_no_cloud_artifacts(self):
        doc = make_translator().translate().document
        self.assertEqual(doc["provenance"]["cloud"]["task_ids"], [])
        self.assertIsNone(doc["provenance"]["cloud"]["flex_credit"])


class CliTest(unittest.TestCase):
    def _bundle_file(self, d: Path, **over) -> Path:
        p = d / "bundle.json"
        p.write_text(json.dumps(make_bundle(**over)), encoding="utf-8")
        return p

    def test_plan_then_dryrun_via_cli(self):
        from fdtd.mrr.__main__ import main

        with TemporaryDirectory() as d:
            d = Path(d)
            bundle = self._bundle_file(d)
            plan_path = d / "plan.json"
            self.assertEqual(main(["plan", "--input", str(bundle), "--out", str(plan_path)]), 0)
            self.assertTrue(plan_path.exists())
            self.assertEqual(main(["dryrun", "--plan", str(plan_path)]), 0)
            self.assertEqual(main(["dryrun", "--input", str(bundle), "--json"]), 0)

    def test_cli_dryrun_nonzero_on_incomplete_bundle(self):
        from fdtd.mrr.__main__ import main

        with TemporaryDirectory() as d:
            d = Path(d)
            bundle = self._bundle_file(d, discretization={**DISCRETIZATION, "run_time_seconds": None})
            self.assertEqual(main(["plan", "--input", str(bundle)]), 2)
            self.assertEqual(main(["dryrun", "--input", str(bundle)]), 2)


if __name__ == "__main__":
    unittest.main()
