"""Tests for :mod:`fdtd.tidy3d_build.linear_build` -- the local-only builder that turns a
validated :class:`~fdtd.mrr.linear_sim.LinearSimulationPlan` into a real
``tidy3d.Simulation`` and hashes it.

Every input here is synthetic and reuses the ``SYN_*`` bundle from
``tests/fdtd/test_linear_sim.py``: made-up permittivities, 64-hex placeholder
digests, a deliberately non-physical ~2 um band. No optical constant appears.

Two kinds of test:

* **guard tests** run in-process. They only exercise the fail-closed gate, which
  is pure and must reject a bad plan *before* ``tidy3d`` is imported -- so this
  test process stays free of ``tidy3d`` (mirroring
  ``test_linear_sim.NoCloudSourceTest``).
* **build tests** shell out to ``tests/fdtd/_linear_build_driver.py`` in a fresh
  subprocess, which is the only place ``tidy3d`` is ever imported.
"""

from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

from fdtd.mrr.linear_sim import LinearSimulationTranslator
from fdtd.tidy3d_build.linear_build import LinearBuildError, build_simulation

from tests.fdtd.test_linear_sim import (
    DISCRETIZATION,
    EXCITATION,
    GEO,
    make_bundle,
    make_translator,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
DRIVER = REPO_ROOT / "tests" / "fdtd" / "_linear_build_driver.py"
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _plan_doc(**over) -> dict:
    return LinearSimulationTranslator.from_bundle(make_bundle(**over)).translate().document


def _run_driver(doc: dict, *args: str) -> dict:
    proc = subprocess.run(
        [sys.executable, str(DRIVER), *args],
        input=json.dumps(doc),
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    if proc.returncode != 0:
        raise AssertionError(f"driver failed ({proc.returncode}):\nSTDOUT {proc.stdout}\nSTDERR {proc.stderr}")
    return json.loads(proc.stdout)


# --------------------------------------------------------------------------- #
# guard tests -- in-process, must never import tidy3d
# --------------------------------------------------------------------------- #
class GuardFailClosedTest(unittest.TestCase):
    def tearDown(self):
        self.assertNotIn("tidy3d", sys.modules, "a guard test imported tidy3d")

    def test_rejects_non_dict(self):
        with self.assertRaises(LinearBuildError):
            build_simulation(["not", "a", "doc"])

    def test_rejects_wrong_schema(self):
        doc = _plan_doc()
        doc["schema"] = "something-else/9"
        with self.assertRaises(LinearBuildError) as cm:
            build_simulation(doc)
        self.assertIn("schema", str(cm.exception))

    def test_rejects_non_linear_marker_even_without_dry_run(self):
        doc = _plan_doc()
        doc["structures"][0]["medium"]["kerr_nonlinearity"] = {"n2": 1.0}
        for kw in ({}, {"run_dry_run": False}):
            with self.assertRaises(LinearBuildError) as cm:
                build_simulation(copy.deepcopy(doc), **kw)
            self.assertIn("nonlinear", str(cm.exception).lower())

    def test_rejects_linearity_flipped(self):
        doc = _plan_doc()
        doc["linearity"] = "nonlinear"
        with self.assertRaises(LinearBuildError):
            build_simulation(doc)

    def test_rejects_cloud_task_ids(self):
        doc = _plan_doc()
        doc["provenance"]["cloud"]["task_ids"] = ["fdve-123"]
        with self.assertRaises(LinearBuildError) as cm:
            build_simulation(doc)
        self.assertIn("task_ids", str(cm.exception))

    def test_rejects_cloud_flex_credit(self):
        doc = _plan_doc()
        doc["provenance"]["cloud"]["flex_credit"] = 12.5
        with self.assertRaises(LinearBuildError):
            build_simulation(doc)

    def test_rejects_incomplete_plan_via_dry_run(self):
        doc = _plan_doc()
        doc["run_time_s"] = None
        with self.assertRaises(LinearBuildError) as cm:
            build_simulation(doc)
        self.assertIn("dry run failed", str(cm.exception))

    def test_rejects_structure_that_does_not_fit(self):
        doc = _plan_doc()
        doc["domain"]["size_um"] = [1.0, 1.0, 1.0]
        with self.assertRaises(LinearBuildError):
            build_simulation(doc)


class ModuleImportPurityTest(unittest.TestCase):
    def test_importing_linear_build_does_not_import_tidy3d(self):
        code = "import sys; import fdtd.tidy3d_build.linear_build; print('tidy3d' in sys.modules)"
        proc = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True, cwd=str(REPO_ROOT)
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout.strip(), "False")

    def test_source_has_no_network_imports(self):
        forbidden = re.compile(
            r"^\s*(?:import|from)\s+"
            r"(requests|httpx|urllib|http|socket|ssl|boto3|paramiko|websocket|aiohttp|tidy3d\.web)\b",
            re.MULTILINE,
        )
        text = (REPO_ROOT / "fdtd" / "tidy3d_build" / "linear_build.py").read_text(encoding="utf-8")
        self.assertEqual(forbidden.findall(text), [])
        # tidy3d itself is only referenced lazily, never at module import time
        self.assertNotRegex(text, r"(?m)^(?:import|from)\s+tidy3d\b")


# --------------------------------------------------------------------------- #
# build tests -- subprocess only
# --------------------------------------------------------------------------- #
class BuildRealSimulationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = _plan_doc()
        cls.info = _run_driver(cls.doc)

    def test_object_is_a_tidy3d_simulation(self):
        self.assertEqual(self.info["sim_type"], "Simulation")
        self.assertEqual(self.info["sim_module"], "tidy3d")

    def test_no_cloud_module_imported_during_build(self):
        self.assertFalse(self.info["web_imported"])
        self.assertFalse(self.info["import_pulled_tidy3d"])

    def test_domain_is_the_plan_domain(self):
        self.assertEqual(self.info["size"], list(self.doc["domain"]["size_um"]))
        self.assertEqual(self.info["center"], list(self.doc["domain"]["center_um"]))

    def test_run_time_and_shutoff_are_the_plan_values(self):
        self.assertEqual(self.info["run_time"], self.doc["run_time_s"])
        self.assertEqual(self.info["shutoff"], self.doc["field_decay_shutoff"])
        self.assertEqual(self.info["run_time"], DISCRETIZATION["run_time_seconds"])

    def test_background_medium_is_the_named_one(self):
        self.assertEqual(self.info["background_permittivity"], self.doc["background_medium"]["permittivity"])
        self.assertEqual(self.info["background_permittivity"], 2.1)
        self.assertEqual(self.info["background_conductivity"], 0.0)

    def test_every_structure_carries_a_concrete_medium(self):
        plan_media = {s["name"]: s["medium"]["permittivity"] for s in self.doc["structures"]}
        got = dict(zip(self.info["structure_names"], self.info["structure_permittivity"]))
        self.assertEqual(got, plan_media)
        for eps in self.info["structure_permittivity"]:
            self.assertGreater(eps, 0)

    def test_slabs_precede_device_structures(self):
        names = self.info["structure_names"]
        self.assertEqual(names[:3], ["substrate", "buried_oxide", "cladding"])
        self.assertEqual(set(names[3:]), {"ring_core", "bus_through", "bus_drop"})

    def test_ring_is_a_clip_operation_bus_and_slabs_are_boxes(self):
        geom = dict(zip(self.info["structure_names"], self.info["structure_geom"]))
        self.assertEqual(geom["ring_core"], "ClipOperation")
        self.assertEqual(geom["bus_through"], "Box")
        self.assertEqual(geom["substrate"], "Box")

    def test_pml_boundaries_carry_the_plan_layer_count(self):
        for axis in ("x", "y", "z"):
            kind, layers = self.info["boundary"][axis]
            self.assertEqual(kind, "PML")
            self.assertEqual(layers, self.doc["boundary_spec"][axis]["num_layers"])
            self.assertEqual(layers, DISCRETIZATION["boundary_num_layers"])

    def test_mode_source_and_pulse(self):
        self.assertEqual(self.info["sources"], [["ModeSource", "+", "mode:bus_through:in"]])
        (freq0,) = self.info["source_freq0"]
        # ~ C_0 / 2 um, i.e. around 1.5e14 Hz -- via Tidy3D's own C_0, not a hard-coded c
        self.assertGreater(freq0, 1.4e14)
        self.assertLess(freq0, 1.6e14)

    def test_flux_monitors_from_tokens_with_full_frequency_sweep(self):
        self.assertEqual(
            self.info["monitors"],
            [
                ["FluxMonitor", "flux:bus_through:out", EXCITATION["num_freqs"]],
                ["FluxMonitor", "flux:bus_drop:out", EXCITATION["num_freqs"]],
            ],
        )

    def test_grid_spec_is_autogrid(self):
        self.assertEqual(self.info["grid_type"], "AutoGrid")

    def test_symmetry_is_the_plan_symmetry(self):
        self.assertEqual(self.info["symmetry"], list(self.doc["symmetry"]))


class DigestTest(unittest.TestCase):
    def test_digest_is_hex64_and_deterministic(self):
        info = _run_driver(_plan_doc())
        self.assertRegex(info["digest"], _HEX64)
        self.assertEqual(info["digest"], info["digest_again"])
        self.assertEqual(info["digest"], info["digest_method"])

    def test_canonical_json_round_trips_back_to_the_same_digest(self):
        info = _run_driver(_plan_doc())
        self.assertEqual(info["reparse_digest"], info["digest"])

    def test_changing_a_material_value_changes_the_digest(self):
        base = _run_driver(_plan_doc())["digest"]
        bumped = _run_driver(_plan_doc(materials=_bumped_core_materials()))["digest"]
        self.assertNotEqual(bumped, base)

    def test_changing_geometry_changes_the_digest(self):
        base = _run_driver(_plan_doc())["digest"]
        moved = _run_driver(_plan_doc(geometry={**GEO, "ring_outer_radius_um": 7.5}))["digest"]
        self.assertNotEqual(moved, base)


class TopologyVariantTest(unittest.TestCase):
    def test_single_bus_topology_builds_without_the_drop(self):
        b = make_bundle()
        b["geometry"]["add_drop"] = False
        b["config"]["monitors"] = ["flux:bus_through:out"]
        doc = LinearSimulationTranslator.from_bundle(b).translate().document
        info = _run_driver(doc)
        self.assertNotIn("bus_drop", info["structure_names"])
        self.assertEqual(info["n_structures"], 5)
        self.assertEqual([m[1] for m in info["monitors"]], ["flux:bus_through:out"])

    def test_field_monitor_token_becomes_a_field_monitor(self):
        b = make_bundle()
        b["config"]["monitors"] = ["flux:bus_through:out", "field:bus_drop:out"]
        doc = LinearSimulationTranslator.from_bundle(b).translate().document
        info = _run_driver(doc)
        self.assertEqual(
            [m[0] for m in info["monitors"]], ["FluxMonitor", "FieldMonitor"]
        )


def _bumped_core_materials() -> list[dict]:
    mats = copy.deepcopy(make_bundle()["materials"])
    for m in mats:
        if m["medium_label"] == "SYN_CORE":
            m["relative_permittivity"] = 9.6
    return mats


if __name__ == "__main__":
    unittest.main()
