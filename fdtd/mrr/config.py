"""Parameterised, hashable *non-mesh* simulation configuration for an MRR study.

This object deliberately carries **no discretisation choice**: no grid / cells
per wavelength, no steps per period, no PML layer count, no run time, no
tolerance. Those belong to the convergence ladders that Astra defines. What it
does hold is the caller-supplied problem setup: the wavelength band of interest,
boundary *type names*, symmetry flags, and the names of the sources / monitors
the study will use.

The wavelength band is a **design target supplied by the caller**, not a
material constant; nothing here is a refractive index, loss, or nonlinear
coefficient.

Serialisation is canonical so the SHA-256 :meth:`SimulationConfig.digest` is
stable under field ordering.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, fields

from fdtd.provenance.schema import canonical_geometry_digest

CONFIG_SCHEMA_ID = "fdtd-mrr-sim-config/1"

# Boundary *type* names only - a label, not a layer count (which is a ladder rung).
BOUNDARY_TYPES = ("pml", "absorber", "periodic", "pec", "pmc")


class ConfigError(ValueError):
    """Raised when the configuration is inconsistent or under-specified."""


def _finite(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


@dataclass
class SimulationConfig:
    """Caller-supplied, discretisation-free setup for a candidate MRR study."""

    wavelength_range_um: list[float]           # [lo, hi], design band of interest
    boundary_types: dict                        # {"x": name, "y": name, "z": name} from BOUNDARY_TYPES
    symmetry: list[int]                         # [sx, sy, sz], each -1 / 0 / +1
    sources: list[str] = field(default_factory=list)   # e.g. ["mode:bus_through:in"]
    monitors: list[str] = field(default_factory=list)  # e.g. ["flux:bus_through:out", "flux:bus_drop:out"]

    # -- validation ------------------------------------------------------- #
    def validate(self) -> "SimulationConfig":
        problems = self.problems()
        if problems:
            raise ConfigError("; ".join(problems))
        return self

    def problems(self) -> list[str]:
        p: list[str] = []

        wr = self.wavelength_range_um
        if (
            not isinstance(wr, (list, tuple))
            or len(wr) != 2
            or not all(_finite(x) and x > 0 for x in wr)
            or wr[0] >= wr[1]
        ):
            p.append(f"wavelength_range_um must be [lo, hi] with 0 < lo < hi, got {wr!r}")

        if not isinstance(self.boundary_types, dict) or set(self.boundary_types) != {"x", "y", "z"}:
            p.append(f"boundary_types must have exactly keys x, y, z; got {self.boundary_types!r}")
        else:
            for axis, name in self.boundary_types.items():
                if name not in BOUNDARY_TYPES:
                    p.append(f"boundary_types[{axis!r}] {name!r} not in {list(BOUNDARY_TYPES)}")

        if not isinstance(self.symmetry, (list, tuple)) or len(self.symmetry) != 3 or any(
            s not in (-1, 0, 1) for s in self.symmetry
        ):
            p.append(f"symmetry must be three values each in (-1, 0, 1), got {self.symmetry!r}")

        for label, seq in (("sources", self.sources), ("monitors", self.monitors)):
            if not isinstance(seq, (list, tuple)) or any(not isinstance(s, str) or s.strip() == "" for s in seq):
                p.append(f"{label} must be a list of non-empty strings, got {seq!r}")
        if isinstance(self.sources, (list, tuple)) and len(self.sources) == 0:
            p.append("sources must name at least one excitation")
        if isinstance(self.monitors, (list, tuple)) and len(self.monitors) == 0:
            p.append("monitors must name at least one observation")
        return p

    # -- explicit "not chosen here" markers --------------------------- #
    @property
    def mesh_is_deferred(self) -> bool:
        """Always True: grid resolution is a convergence-ladder decision."""
        return True

    @property
    def run_time_is_deferred(self) -> bool:
        """Always True: run time / shutoff is a convergence-ladder decision."""
        return True

    # -- serialisation ------------------------------------------------- #
    def to_canonical_dict(self) -> dict:
        out = {}
        for f in fields(self):
            value = getattr(self, f.name)
            if isinstance(value, dict):
                value = dict(sorted(value.items()))
            elif isinstance(value, tuple):
                value = list(value)
            out[f.name] = value
        return out

    def to_document(self) -> dict:
        return {
            "schema": CONFIG_SCHEMA_ID,
            "units": "um",
            "discretisation": "deferred-to-convergence-ladders",
            "parameters": self.to_canonical_dict(),
        }

    def digest(self) -> str:
        """Deterministic SHA-256 of the canonical configuration document."""
        return canonical_geometry_digest(self.to_document())
