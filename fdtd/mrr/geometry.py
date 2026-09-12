"""Parameterised, hashable geometry of a 3D silicon microring add/drop resonator.

Every field here is a **geometric** quantity (a length in micrometres, a count,
or a topology flag) or a **medium label** (a name that points at an external
:class:`~fdtd.provenance.schema.MaterialSource`, never an optical constant).
There are no physical defaults: the caller must supply every dimension, so this
module cannot silently invent a device.

Serialisation is canonical (sorted keys, compact separators) so the SHA-256
:meth:`RingResonatorGeometry.digest` is insensitive to field ordering and
incidental whitespace but changes if any value changes.

Pure stdlib: ``dataclasses``, ``math`` (+ the project's ``fdtd.provenance``
hash helpers).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, fields

from fdtd.provenance.schema import canonical_geometry_digest

GEOMETRY_SCHEMA_ID = "fdtd-mrr-geometry/1"
# Schema /2 adds ``bus_overhang_um``: the bus waveguide is drawn longer than the
# port-to-port span so its end faces sit *outside* the simulation domain, inside
# the PML. A bus that terminates inside the domain forms a Fabry-Perot cavity
# between its two facets; `docs/decisions/2026-09-13-facet-fabry-perot.md`
# measures a 40% peak-to-peak baseline ripple from exactly that. Documents keep
# declaring /1 (and hash identically) whenever the overhang is zero, so the
# locked linear convergence ladder stays reproducible.
GEOMETRY_SCHEMA_ID_V2 = "fdtd-mrr-geometry/2"


class GeometryError(ValueError):
    """Raised when a geometry is dimensionally impossible or under-specified."""


def _finite_positive(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value > 0


def _finite_non_negative(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0


@dataclass
class RingResonatorGeometry:
    """A silicon-on-insulator microring add/drop filter, described geometrically.

    Length fields are micrometres. The ring is centred at the origin in the
    device plane; the bus waveguide(s) run along x. With ``add_drop`` true a
    second (drop) bus is placed symmetrically on the far side of the ring.
    """

    ring_outer_radius_um: float
    waveguide_width_um: float
    waveguide_thickness_um: float
    bus_waveguide_width_um: float
    coupling_gap_um: float
    bus_length_um: float
    cladding_thickness_um: float
    box_thickness_um: float
    substrate_thickness_um: float
    domain_padding_um: float
    add_drop: bool
    core_medium: str
    cladding_medium: str
    box_medium: str
    substrate_medium: str
    # Extra bus length beyond each port plane, so the guide's end faces land in
    # the PML instead of inside the domain. Zero reproduces schema /1 exactly,
    # hence the default and the trailing position.
    bus_overhang_um: float = 0.0

    # -- validation ------------------------------------------------------- #
    def validate(self) -> "RingResonatorGeometry":
        """Return self if the geometry is well formed, else raise GeometryError."""
        problems = self.problems()
        if problems:
            raise GeometryError("; ".join(problems))
        return self

    def problems(self) -> list[str]:
        p: list[str] = []
        positive = (
            "ring_outer_radius_um",
            "waveguide_width_um",
            "waveguide_thickness_um",
            "bus_waveguide_width_um",
            "bus_length_um",
            "cladding_thickness_um",
            "box_thickness_um",
            "substrate_thickness_um",
        )
        for name in positive:
            if not _finite_positive(getattr(self, name)):
                p.append(f"{name} must be a finite positive number, got {getattr(self, name)!r}")
        if not _finite_non_negative(self.coupling_gap_um):
            p.append(f"coupling_gap_um must be a finite number >= 0, got {self.coupling_gap_um!r}")
        if not _finite_non_negative(self.domain_padding_um):
            p.append(f"domain_padding_um must be a finite number >= 0, got {self.domain_padding_um!r}")
        if not _finite_non_negative(self.bus_overhang_um):
            p.append(f"bus_overhang_um must be a finite number >= 0, got {self.bus_overhang_um!r}")
        elif self.bus_overhang_um > 0.0 and _finite_non_negative(self.domain_padding_um):
            # An overhang that does not clear the padding leaves the facet inside
            # the domain, which is the defect this field exists to remove.
            if self.bus_overhang_um <= self.domain_padding_um:
                p.append(
                    "bus_overhang_um must exceed domain_padding_um "
                    f"({self.domain_padding_um}) so the bus end face leaves the domain, "
                    f"got {self.bus_overhang_um!r}"
                )
        if not isinstance(self.add_drop, bool):
            p.append(f"add_drop must be a bool, got {self.add_drop!r}")

        if _finite_positive(self.ring_outer_radius_um) and _finite_positive(self.waveguide_width_um):
            if self.waveguide_width_um >= self.ring_outer_radius_um:
                p.append(
                    "waveguide_width_um must be smaller than ring_outer_radius_um "
                    f"(inner radius would be {self.ring_inner_radius_um:g})"
                )
        for name in ("core_medium", "cladding_medium", "box_medium", "substrate_medium"):
            value = getattr(self, name)
            if not isinstance(value, str) or value.strip() == "":
                p.append(f"{name} must be a non-empty medium label, got {value!r}")
        return p

    # -- derived geometry ----------------------------------------------- #
    @property
    def ring_inner_radius_um(self) -> float:
        return self.ring_outer_radius_um - self.waveguide_width_um

    @property
    def bus_centre_offset_um(self) -> float:
        """Distance from the ring centre to a bus waveguide centreline."""
        return self.ring_outer_radius_um + self.coupling_gap_um + self.bus_waveguide_width_um / 2.0

    @property
    def bus_structure_length_um(self) -> float:
        """Drawn length of a bus waveguide.

        The *port-to-port* span stays ``bus_length_um`` -- that is what sets the
        domain extent and where the port planes sit. The drawn guide is longer by
        one overhang at each end so its end faces leave the domain and terminate
        inside the PML, removing the facet Fabry-Perot cavity.
        """
        return self.bus_length_um + 2.0 * self.bus_overhang_um

    def domain_size_um(self) -> list[float]:
        """[x, y, z] full extent of the simulation domain (geometry + padding).

        Deliberately keyed to ``bus_length_um``, not to the drawn bus length: the
        overhang exists to push the guide *through* the domain boundary, so it
        must not enlarge the domain (which would raise the cell count and cost).
        """
        x = self.bus_length_um + 2.0 * self.domain_padding_um
        y = 2.0 * self.bus_centre_offset_um + self.bus_waveguide_width_um + 2.0 * self.domain_padding_um
        z = (
            self.substrate_thickness_um
            + self.box_thickness_um
            + self.waveguide_thickness_um
            + self.cladding_thickness_um
            + 2.0 * self.domain_padding_um
        )
        return [x, y, z]

    # -- serialisation ------------------------------------------------- #
    @property
    def schema_id(self) -> str:
        """``/1`` while the bus has no overhang, ``/2`` once it does."""
        return GEOMETRY_SCHEMA_ID if self.bus_overhang_um == 0.0 else GEOMETRY_SCHEMA_ID_V2

    def to_canonical_dict(self) -> dict:
        """Plain dict of the declared parameters, in declaration order.

        ``bus_overhang_um`` is omitted while it is zero. That keeps a schema /1
        document -- and therefore its SHA-256 -- byte-identical to what this
        class produced before the field existed, so the hash-locked linear
        convergence ladder in ``manifests/fdtd/mrr-linear-001/`` stays valid.
        """
        out = {f.name: getattr(self, f.name) for f in fields(self)}
        if self.bus_overhang_um == 0.0:
            out.pop("bus_overhang_um", None)
        return out

    def to_structures(self) -> list[dict]:
        """Geometric primitives that make up the device.

        Each entry carries only extents and a ``medium`` *label*. No optical
        constants appear. The list order is fixed for digest stability.
        """
        z_wg_centre = self.substrate_thickness_um + self.box_thickness_um + self.waveguide_thickness_um / 2.0
        structures: list[dict] = [
            {
                "name": "ring_core",
                "kind": "ring",
                "medium": self.core_medium,
                "center_um": [0.0, 0.0, z_wg_centre],
                "outer_radius_um": self.ring_outer_radius_um,
                "inner_radius_um": self.ring_inner_radius_um,
                "thickness_um": self.waveguide_thickness_um,
            },
            {
                "name": "bus_through",
                "kind": "waveguide",
                "medium": self.core_medium,
                "axis": "x",
                "center_um": [0.0, -self.bus_centre_offset_um, z_wg_centre],
                "width_um": self.bus_waveguide_width_um,
                "length_um": self.bus_structure_length_um,
                "thickness_um": self.waveguide_thickness_um,
            },
        ]
        if self.add_drop:
            structures.append(
                {
                    "name": "bus_drop",
                    "kind": "waveguide",
                    "medium": self.core_medium,
                    "axis": "x",
                    "center_um": [0.0, self.bus_centre_offset_um, z_wg_centre],
                    "width_um": self.bus_waveguide_width_um,
                    "length_um": self.bus_structure_length_um,
                    "thickness_um": self.waveguide_thickness_um,
                }
            )

        # Planar stack, bottom to top. Extents in z only; x/y span the domain.
        z0 = 0.0
        for name, thickness, medium in (
            ("substrate", self.substrate_thickness_um, self.substrate_medium),
            ("buried_oxide", self.box_thickness_um, self.box_medium),
            ("cladding", self.waveguide_thickness_um + self.cladding_thickness_um, self.cladding_medium),
        ):
            structures.append(
                {
                    "name": name,
                    "kind": "slab",
                    "medium": medium,
                    "z_min_um": z0,
                    "z_max_um": z0 + thickness,
                }
            )
            z0 += thickness
        return structures

    def to_document(self) -> dict:
        """Full canonical geometry document (the object that gets hashed)."""
        return {
            "schema": self.schema_id,
            "units": "um",
            "parameters": self.to_canonical_dict(),
            "derived": {
                "ring_inner_radius_um": self.ring_inner_radius_um,
                "bus_centre_offset_um": self.bus_centre_offset_um,
                "domain_size_um": self.domain_size_um(),
                **(
                    {"bus_structure_length_um": self.bus_structure_length_um}
                    if self.bus_overhang_um != 0.0
                    else {}
                ),
            },
            "structures": self.to_structures(),
        }

    def digest(self) -> str:
        """Deterministic SHA-256 of the canonical geometry document."""
        return canonical_geometry_digest(self.to_document())
