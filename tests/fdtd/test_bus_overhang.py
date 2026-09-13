"""The bus may be drawn past the domain edge so its facets sit in the PML.

A bus that terminates *inside* the domain forms a Fabry-Perot cavity between its
two end faces. `docs/decisions/2026-09-13-facet-fabry-perot.md` measures that
cavity in paid data: a 40% peak-to-peak ripple on the through baseline with a
17.96 nm period, matching the 2L = 32 um facet round trip and walking off the
ring comb. ``bus_overhang_um`` pushes the facets out of the domain.

Two properties matter as much as the fix itself:

* a zero overhang must reproduce schema /1 **byte-for-byte**, so the hash-locked
  linear convergence ladder under ``manifests/fdtd/mrr-linear-001/`` stays
  reproducible -- the literal digest is pinned below;
* the overhang must not enlarge the domain, or the fix would silently raise the
  cell count and the FlexCredit cost.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
INPUT = REPO_ROOT / "manifests" / "fdtd" / "mrr-linear-001" / "rung-0.input.json"

# The geometry digest every plan in the locked linear ladder records.
LADDER_GEOMETRY_DIGEST = "6844d49cf1585fc4df1c23ad8e60c2a9771f4a13d1df97e6408099ca0187147e"


def _params() -> dict:
    return json.loads(INPUT.read_text(encoding="utf-8"))["geometry"]


def _plans():
    """(path, document) for every plan manifest in the linear study."""
    out = []
    for path in sorted((REPO_ROOT / "manifests" / "fdtd" / "mrr-linear-001").glob("*.plan.json")):
        out.append((path, json.loads(path.read_text(encoding="utf-8"))))
    return out


def _plan_schema(entry) -> str:
    _, doc = entry
    return doc["inputs"]["geometry_document"]["schema"]


def _geom(**over):
    from fdtd.mrr.geometry import RingResonatorGeometry

    return RingResonatorGeometry(**{**_params(), **over})


class SchemaV1IsUnchangedTest(unittest.TestCase):
    """Regression guard: adding the field must not move the locked ladder hash."""

    def test_default_is_zero_overhang(self):
        self.assertEqual(_geom().bus_overhang_um, 0.0)

    def test_zero_overhang_declares_schema_v1(self):
        from fdtd.mrr.geometry import GEOMETRY_SCHEMA_ID

        self.assertEqual(_geom().schema_id, GEOMETRY_SCHEMA_ID)
        self.assertEqual(_geom().to_document()["schema"], GEOMETRY_SCHEMA_ID)

    def test_zero_overhang_reproduces_the_locked_ladder_digest(self):
        self.assertEqual(_geom().digest(), LADDER_GEOMETRY_DIGEST)

    def test_every_schema_v1_plan_still_records_that_digest(self):
        """Plans drawn without an overhang must all carry the locked digest.

        Scoped by the schema the plan itself declares, not by "every plan on
        disk": schema /2 plans (freq-rung-2 onwards) deliberately carry a
        different geometry, and asserting otherwise would be asserting something
        false. Their own invariant is checked in `SchemaV2PlansTest`.
        """
        v1 = [p for p in _plans() if _plan_schema(p) == "fdtd-mrr-geometry/1"]
        self.assertGreaterEqual(len(v1), 8)
        for plan, doc in v1:
            with self.subTest(plan=plan.name):
                self.assertEqual(doc["provenance"]["geometry_hash"], LADDER_GEOMETRY_DIGEST)

    def test_zero_overhang_omits_the_field_from_the_canonical_dict(self):
        self.assertNotIn("bus_overhang_um", _geom().to_canonical_dict())

    def test_zero_overhang_omits_the_derived_drawn_length(self):
        self.assertNotIn("bus_structure_length_um", _geom().to_document()["derived"])


class SchemaV2Test(unittest.TestCase):
    def test_non_zero_overhang_declares_schema_v2(self):
        from fdtd.mrr.geometry import GEOMETRY_SCHEMA_ID_V2

        g = _geom(bus_overhang_um=2.0)
        self.assertEqual(g.schema_id, GEOMETRY_SCHEMA_ID_V2)
        self.assertEqual(g.to_document()["schema"], GEOMETRY_SCHEMA_ID_V2)

    def test_non_zero_overhang_changes_the_digest(self):
        self.assertNotEqual(_geom(bus_overhang_um=2.0).digest(), LADDER_GEOMETRY_DIGEST)

    def test_drawn_length_adds_one_overhang_per_end(self):
        g = _geom(bus_overhang_um=2.0)
        self.assertEqual(g.bus_structure_length_um, g.bus_length_um + 4.0)

    def test_both_buses_use_the_drawn_length(self):
        g = _geom(bus_overhang_um=2.0)
        buses = [s for s in g.to_structures() if s["kind"] == "waveguide"]
        self.assertEqual(len(buses), 2)
        for bus in buses:
            self.assertEqual(bus["length_um"], g.bus_structure_length_um)

    def test_facets_land_outside_the_domain(self):
        g = _geom(bus_overhang_um=2.0)
        half_bus = g.bus_structure_length_um / 2.0
        half_domain = g.domain_size_um()[0] / 2.0
        self.assertGreater(half_bus, half_domain)

    def test_overhang_does_not_enlarge_the_domain(self):
        self.assertEqual(_geom().domain_size_um(), _geom(bus_overhang_um=2.0).domain_size_um())

    def test_derived_block_exposes_the_drawn_length(self):
        g = _geom(bus_overhang_um=2.0)
        self.assertEqual(
            g.to_document()["derived"]["bus_structure_length_um"], g.bus_structure_length_um
        )


class SchemaV2PlansTest(unittest.TestCase):
    """Plans that declare schema /2 must agree on a single, different geometry."""

    def test_v2_plans_exist_and_share_one_digest_that_is_not_the_locked_one(self):
        v2 = [p for p in _plans() if _plan_schema(p) == "fdtd-mrr-geometry/2"]
        self.assertGreaterEqual(len(v2), 1)
        digests = {doc["provenance"]["geometry_hash"] for _, doc in v2}
        self.assertEqual(len(digests), 1, f"schema /2 plans disagree on geometry: {digests}")
        self.assertNotIn(LADDER_GEOMETRY_DIGEST, digests)

    def test_v2_plan_digest_matches_this_class(self):
        v2 = [p for p in _plans() if _plan_schema(p) == "fdtd-mrr-geometry/2"]
        if not v2:
            self.skipTest("no schema /2 plan on disk")
        overhang = v2[0][1]["inputs"]["geometry_document"]["parameters"]["bus_overhang_um"]
        self.assertEqual(
            _geom(bus_overhang_um=overhang).digest(),
            v2[0][1]["provenance"]["geometry_hash"],
        )

    def test_every_plan_declares_a_known_schema(self):
        for entry in _plans():
            with self.subTest(plan=entry[0].name):
                self.assertIn(
                    _plan_schema(entry), {"fdtd-mrr-geometry/1", "fdtd-mrr-geometry/2"}
                )


class ValidationTest(unittest.TestCase):
    def test_negative_overhang_is_rejected(self):
        from fdtd.mrr.geometry import GeometryError

        with self.assertRaises(GeometryError):
            _geom(bus_overhang_um=-1.0).validate()

    def test_overhang_not_clearing_the_padding_is_rejected(self):
        """An overhang inside the padding leaves the facet in the domain."""
        from fdtd.mrr.geometry import GeometryError

        padding = _params()["domain_padding_um"]
        for ov in (padding / 2.0, padding):
            with self.subTest(overhang=ov):
                with self.assertRaises(GeometryError):
                    _geom(bus_overhang_um=ov).validate()

    def test_overhang_clearing_the_padding_is_accepted(self):
        padding = _params()["domain_padding_um"]
        _geom(bus_overhang_um=padding * 2.0).validate()

    def test_zero_overhang_is_still_accepted(self):
        _geom(bus_overhang_um=0.0).validate()


if __name__ == "__main__":
    unittest.main()
