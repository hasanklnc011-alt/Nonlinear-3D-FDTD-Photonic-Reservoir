"""Monitor spectral sampling is independent of the source pulse.

Resolving a high-Q resonance needs a fine frequency comb on the monitors.
Narrowing the *excitation* instead would only lengthen the source pulse in time,
so the two must be separable. The plan schema already carries a per-monitor
``sampling`` block; these tests pin that it is honoured, and that a plan without
one keeps the previous whole-band behaviour.

Every test that actually builds a ``tidy3d.Simulation`` goes through the
subprocess driver, so this module never pulls ``tidy3d`` into the test process
(other tests assert that it stays out of ``sys.modules``).
"""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DRIVER = REPO_ROOT / "tests" / "fdtd" / "_linear_build_driver.py"
PLAN = REPO_ROOT / "manifests" / "fdtd" / "mrr-linear-001" / "mesh-rung-2.plan.json"

DENSE = {
    "center_wavelength_um": 1.54093,
    "bandwidth_wavelength_um": 0.003,
    "num_freqs": 1501,
}


def _plan() -> dict:
    return json.loads(PLAN.read_text(encoding="utf-8"))


def _drive(doc: dict):
    """Return (returncode, parsed stdout or None, stderr)."""
    proc = subprocess.run(
        [sys.executable, str(DRIVER), "--no-dry-run"],
        input=json.dumps(doc),
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    payload = json.loads(proc.stdout) if proc.returncode == 0 and proc.stdout.strip() else None
    return proc.returncode, payload, proc.stderr


def _built(doc: dict) -> dict:
    code, payload, err = _drive(doc)
    if code != 0:
        raise AssertionError(f"driver failed ({code}): {err}")
    return payload


class MonitorSamplingTests(unittest.TestCase):
    def test_plan_fixture_is_present_and_linear(self):
        doc = _plan()
        self.assertEqual(doc["linearity"], "linear")
        self.assertEqual(len(doc["monitors"]), 2)

    def test_absent_sampling_falls_back_to_the_excitation_comb(self):
        doc = _plan()
        for mon in doc["monitors"]:
            mon.pop("sampling", None)
        info = _built(doc)
        n = doc["inputs"]["excitation"]["num_freqs"]
        self.assertEqual([m[2] for m in info["monitors"]], [n, n])

    def test_per_monitor_sampling_sets_that_monitors_comb(self):
        doc = _plan()
        for mon in doc["monitors"]:
            mon["sampling"] = dict(DENSE)
        info = _built(doc)
        self.assertEqual([m[2] for m in info["monitors"]], [1501, 1501])

    def test_dense_monitor_does_not_touch_the_source_pulse(self):
        doc = _plan()
        wide = _built(doc)
        for mon in doc["monitors"]:
            mon["sampling"] = dict(DENSE)
        narrow = _built(doc)
        self.assertEqual(wide["source_freq0"], narrow["source_freq0"])
        self.assertEqual(wide["source_fwidth"], narrow["source_fwidth"])

    def test_monitors_may_carry_different_combs(self):
        doc = _plan()
        doc["monitors"][0]["sampling"] = {
            "center_wavelength_um": 1.55,
            "bandwidth_wavelength_um": 0.1,
            "num_freqs": 201,
        }
        doc["monitors"][1]["sampling"] = dict(DENSE)
        info = _built(doc)
        self.assertEqual([m[2] for m in info["monitors"]], [201, 1501])

    def test_comb_spans_the_requested_band(self):
        doc = _plan()
        for mon in doc["monitors"]:
            mon["sampling"] = dict(DENSE)
        lo, hi = _built(doc)["monitor_lambda_bounds_um"][0]
        centre, band = DENSE["center_wavelength_um"], DENSE["bandwidth_wavelength_um"]
        self.assertAlmostEqual(lo, centre - band / 2.0, places=9)
        self.assertAlmostEqual(hi, centre + band / 2.0, places=9)

    def test_changing_only_the_comb_changes_the_digest(self):
        base = _built(_plan())["digest"]
        doc = _plan()
        for mon in doc["monitors"]:
            mon["sampling"] = dict(DENSE)
        self.assertNotEqual(base, _built(doc)["digest"])

    def test_rejects_malformed_sampling(self):
        for bad in (
            {"center_wavelength_um": 0.0, "bandwidth_wavelength_um": 0.003, "num_freqs": 11},
            {"center_wavelength_um": 1.54, "bandwidth_wavelength_um": -1.0, "num_freqs": 11},
            {"center_wavelength_um": 1.54, "bandwidth_wavelength_um": 0.003, "num_freqs": 0},
            {"center_wavelength_um": 1.54, "bandwidth_wavelength_um": 0.003, "num_freqs": True},
            {"center_wavelength_um": 1.0, "bandwidth_wavelength_um": 4.0, "num_freqs": 11},
        ):
            with self.subTest(bad=bad):
                doc = _plan()
                doc["monitors"][0]["sampling"] = copy.deepcopy(bad)
                code, _, err = _drive(doc)
                self.assertNotEqual(code, 0)
                self.assertIn("LinearBuildError", err)


if __name__ == "__main__":
    unittest.main()
