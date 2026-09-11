"""Typed schema for a Tidy3D candidate-study provenance record.

Every dataclass here is a *description of evidence*, never the evidence itself.
Physical quantities (refractive index / dispersion poles, chi(3), n2, ...) are
**not** stored in these objects and have no defaults — they live in external
artifact files that are referenced only by SHA-256 digest
(``*_parameter_digest`` fields) plus a local ``evidence_paths`` entry.

Missing / blank is represented by ``None`` (or an empty list). The validator in
:mod:`fdtd.provenance.validate` is fail-closed: absence of a required field is a
validation failure, not a silently-tolerated default.

Pure stdlib: ``dataclasses``, ``hashlib``, ``json``, ``math``.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass, field, fields, is_dataclass
from pathlib import Path
from typing import Any

SCHEMA_ID = "fdtd-candidate-study-provenance/1"

# Controlled vocabulary for where an externally-supplied parameter set came from.
SOURCE_KINDS = (
    "tidy3d_material_library",
    "literature",
    "vendor_datasheet",
    "measured",
)

# The convergence study must sweep each of these axes independently.
LADDER_DIMENSIONS = ("mesh", "time", "pml")

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def sha256_bytes(data: bytes) -> str:
    """Hex SHA-256 of raw bytes."""
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    """Hex SHA-256 of text, UTF-8 encoded (newline-sensitive)."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: str | Path) -> str:
    """Hex SHA-256 of a file's bytes."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_geometry_digest(structures: Any) -> str:
    """Deterministic digest of a JSON-serialisable geometry description.

    The structure list is dumped with sorted keys and compact separators so the
    digest is insensitive to key ordering and incidental whitespace but
    sensitive to any value change.
    """
    payload = json.dumps(structures, sort_keys=True, separators=(",", ":"))
    return sha256_text(payload)


def looks_like_sha256(value: Any) -> bool:
    return isinstance(value, str) and bool(_SHA256_RE.match(value))


def _blank(value: Any) -> bool:
    """True when a field carries no information."""
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    if isinstance(value, (list, tuple, dict)) and len(value) == 0:
        return True
    return False


def is_finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


# --------------------------------------------------------------------------- #
# Leaf records
# --------------------------------------------------------------------------- #
@dataclass
class MaterialSource:
    """Provenance of the linear (dispersive) material model.

    ``parameter_digest`` is the SHA-256 of the external artifact holding the
    actual dispersion parameters; this object never stores those numbers.
    """

    name: str | None = None
    dispersion_model: str | None = None            # e.g. "PoleResidue", "Sellmeier" (name only)
    source_kind: str | None = None                 # one of SOURCE_KINDS
    reference: str | None = None                   # library key / DOI / datasheet id
    version: str | None = None                     # library or dataset version tag
    retrieved_utc: str | None = None               # ISO 8601 date the data was pulled
    parameter_digest: str | None = None            # sha256 of the external parameter file
    wavelength_range_um: list[float] | None = None  # [lo, hi] validity window, caller-supplied


@dataclass
class NonlinearModel:
    """Provenance of the nonlinear response model (Kerr / chi(3) / TPA / ...).

    Like :class:`MaterialSource`, the physical coefficients are external; only
    their digest and source are recorded here.
    """

    model_type: str | None = None                  # e.g. "KerrNonlinearity", "chi3" (name only)
    source_kind: str | None = None                 # one of SOURCE_KINDS
    reference: str | None = None
    version: str | None = None
    parameter_digest: str | None = None            # sha256 of the external parameter file
    applies_to_medium: str | None = None           # MaterialSource.name it modifies
    notes: str | None = None


@dataclass
class GeometryProvenance:
    """Hash + source of the simulated geometry."""

    geometry_hash: str | None = None               # sha256 of the canonical geometry description
    hash_algorithm: str = "sha256"
    source_artifact: str | None = None             # file that was hashed (GDS / structure JSON)
    units: str | None = None                       # e.g. "um"
    description: str | None = None


@dataclass
class ConvergenceRung:
    """One step of a convergence ladder.

    Only the field relevant to the ladder's ``dimension`` has to be populated
    (``grid_cells_per_wavelength`` for mesh, ``steps_per_period`` for time,
    ``pml_layers`` for pml); the others may stay ``None``.
    """

    label: str | None = None
    grid_cells_per_wavelength: float | None = None
    steps_per_period: float | None = None
    pml_layers: int | None = None
    run_time_ps: float | None = None
    field_decay_shutoff: float | None = None
    observable: str | None = None                  # what is compared across rungs
    observable_value: float | None = None
    task_id: str | None = None                     # Tidy3D task id, absent until the rung is run
    flex_credit_estimated: float | None = None
    flex_credit_actual: float | None = None

    def refinement_parameter(self, dimension: str) -> float | None:
        return {
            "mesh": self.grid_cells_per_wavelength,
            "time": self.steps_per_period,
            "pml": None if self.pml_layers is None else float(self.pml_layers),
        }.get(dimension)


@dataclass
class ConvergenceLadder:
    """An ordered sweep of one discretisation axis, coarse rung first."""

    dimension: str | None = None                   # one of LADDER_DIMENSIONS
    tolerance_rel: float | None = None             # target |Δobservable| / |observable| between last two rungs
    rungs: list[ConvergenceRung] = field(default_factory=list)

    def last_relative_change(self) -> float | None:
        """Relative change in the observable between the final two rungs."""
        vals = [r.observable_value for r in self.rungs if is_finite_number(r.observable_value)]
        if len(vals) < 2:
            return None
        prev, last = vals[-2], vals[-1]
        denom = max(abs(prev), abs(last))
        if denom == 0:
            return 0.0
        return abs(last - prev) / denom

    def refinement_is_monotonic(self) -> bool:
        """True when the refinement parameter strictly increases down the ladder."""
        if self.dimension is None:
            return False
        seq = [r.refinement_parameter(self.dimension) for r in self.rungs]
        if any(v is None or not is_finite_number(v) for v in seq):
            return False
        return all(b > a for a, b in zip(seq, seq[1:])) and len(seq) >= 2

    def converged(self) -> bool:
        if not is_finite_number(self.tolerance_rel) or self.tolerance_rel <= 0:
            return False
        if not self.refinement_is_monotonic():
            return False
        change = self.last_relative_change()
        return change is not None and change <= self.tolerance_rel


@dataclass
class FlexCreditBudget:
    """Estimated vs actual FlexCredit and the approved ceiling for this study."""

    estimated_total: float | None = None
    actual_total: float | None = None
    estimate_source: str | None = None             # e.g. "tidy3d.web.estimate_cost", "manual"
    estimate_task_ids: list[str] = field(default_factory=list)
    approved_ceiling: float | None = None           # cost gate; set by Astra, not Claude

    def within_ceiling(self) -> bool | None:
        if not is_finite_number(self.approved_ceiling):
            return None
        cost = self.actual_total if is_finite_number(self.actual_total) else self.estimated_total
        if not is_finite_number(cost):
            return None
        return cost <= self.approved_ceiling


# --------------------------------------------------------------------------- #
# Top-level manifest
# --------------------------------------------------------------------------- #
@dataclass
class CandidateStudyManifest:
    """The full provenance record for one candidate-study convergence campaign."""

    schema: str = SCHEMA_ID
    study_id: str | None = None
    created_utc: str | None = None
    candidate_family: str | None = None            # left None by Claude; Astra decides the family
    tidy3d_version: str | None = None
    notes: str | None = None
    material: MaterialSource | None = None
    nonlinear: NonlinearModel | None = None
    geometry: GeometryProvenance | None = None
    ladders: list[ConvergenceLadder] = field(default_factory=list)
    flex_credit: FlexCreditBudget | None = None
    task_ids: list[str] = field(default_factory=list)   # every Tidy3D task id this study relies on
    evidence_paths: list[str] = field(default_factory=list)  # local files backing the digests

    # -- serialisation ----------------------------------------------------- #
    def to_dict(self) -> dict:
        return _to_jsonable(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n"

    @classmethod
    def from_dict(cls, data: dict) -> "CandidateStudyManifest":
        return _from_dict(cls, data)

    @classmethod
    def from_json(cls, text: str) -> "CandidateStudyManifest":
        return cls.from_dict(json.loads(text))


# --------------------------------------------------------------------------- #
# Generic (de)serialisation for the nested dataclasses
# --------------------------------------------------------------------------- #
def _to_jsonable(obj: Any) -> Any:
    if is_dataclass(obj) and not isinstance(obj, type):
        return {f.name: _to_jsonable(getattr(obj, f.name)) for f in fields(obj)}
    if isinstance(obj, (list, tuple)):
        return [_to_jsonable(v) for v in obj]
    if isinstance(obj, dict):
        return {k: _to_jsonable(v) for k, v in obj.items()}
    return obj


_LEAF_TYPES = {
    "material": MaterialSource,
    "nonlinear": NonlinearModel,
    "geometry": GeometryProvenance,
    "flex_credit": FlexCreditBudget,
}


def _from_dict(cls: type, data: dict) -> Any:
    if not isinstance(data, dict):
        raise TypeError(f"expected an object for {cls.__name__}, got {type(data).__name__}")
    known = {f.name for f in fields(cls)}
    unknown = set(data) - known
    if unknown:
        raise ValueError(f"{cls.__name__}: unknown field(s) {sorted(unknown)}")

    kwargs: dict[str, Any] = {}
    for f in fields(cls):
        if f.name not in data:
            continue
        raw = data[f.name]
        if f.name in _LEAF_TYPES and raw is not None:
            kwargs[f.name] = _from_dict(_LEAF_TYPES[f.name], raw)
        elif f.name == "ladders" and raw is not None:
            kwargs[f.name] = [_ladder_from_dict(item) for item in raw]
        else:
            kwargs[f.name] = raw
    return cls(**kwargs)


def _ladder_from_dict(data: dict) -> ConvergenceLadder:
    ladder = _from_dict(ConvergenceLadder, {k: v for k, v in data.items() if k != "rungs"})
    for rung in data.get("rungs", []) or []:
        ladder.rungs.append(_from_dict(ConvergenceRung, rung))
    return ladder


# --------------------------------------------------------------------------- #
# Blank template
# --------------------------------------------------------------------------- #
def blank_manifest() -> CandidateStudyManifest:
    """A structurally-complete but empty manifest.

    Every evidence field is ``None`` / empty and ``candidate_family`` is left
    unset, so :func:`fdtd.provenance.validate.validate_study` fails on it by
    design. It is a form for Astra to fill, not a usable study.
    """
    return CandidateStudyManifest(
        material=MaterialSource(),
        nonlinear=NonlinearModel(),
        geometry=GeometryProvenance(),
        flex_credit=FlexCreditBudget(),
        ladders=[ConvergenceLadder(dimension=d, rungs=[ConvergenceRung(), ConvergenceRung()])
                 for d in LADDER_DIMENSIONS],
    )
