"""Local-only translation of a fully-evidenced MRR study input into a linear
Tidy3D ``Simulation`` **plan**.

This module answers exactly one question: *given a caller-supplied silicon
microring geometry, a discretisation-free study configuration, an explicit table
of linear material values, an excitation spec and a discretisation spec, what are
the keyword arguments of the linear (resonance / mesh / time / PML) Tidy3D
``Simulation`` that would be built?*

It produces a :class:`LinearSimulationPlan`: a deterministic, canonically
serialisable dictionary that maps 1:1 onto ``tidy3d.Simulation(...)`` for the
**linear** solve. It carries a SHA-256 digest of that document and a local
dry-run validator (:mod:`fdtd.mrr.linear_dryrun`).

Hard boundaries (mirrored by ``tests/fdtd/test_linear_sim.py``):

* **Linear only.** No nonlinear medium, ``KerrNonlinearity``,
  ``TwoPhotonAbsorption``, ``chi(3)`` or free-carrier term is ever emitted or
  accepted. A bundle carrying a ``nonlinear`` block is rejected.
* **No invented physics.** Every linear permittivity / conductivity and every
  geometry dimension must be supplied in the input. Nothing has a physical
  default; a missing or malformed value fails closed
  (:class:`MissingLinearEvidenceError`). No speed of light, no vacuum
  permittivity, no material constant is hard-coded — the plan stays in the
  caller's own unit system (micrometres, seconds, relative permittivity, S/m).
* **No cloud.** Nothing here imports ``tidy3d`` or any network module, opens a
  socket, or uploads / estimates / starts / monitors / downloads a task. The
  plan lists no task ids and no FlexCredit number.

Pure stdlib: ``dataclasses``, ``math`` (+ the project's ``fdtd.provenance`` hash
helper and ``fdtd.mrr`` geometry / config dataclasses).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, fields

from fdtd.provenance.schema import canonical_geometry_digest, looks_like_sha256

from .config import SimulationConfig
from .geometry import RingResonatorGeometry
from .study import StudyIdentity

LINEAR_INPUT_SCHEMA_ID = "fdtd-mrr-linear-input/1"
LINEAR_SIM_SCHEMA_ID = "fdtd-mrr-linear-simulation-plan/1"

# Only a non-dispersive isotropic linear medium is supported by this layer:
# it maps directly onto ``tidy3d.Medium(permittivity=eps_r, conductivity=sigma)``
# with values the caller supplies. Dispersive fits (PoleResidue / Sellmeier) are
# an Astra decision and are intentionally out of scope here.
LINEAR_MEDIUM_MODELS = ("non_dispersive",)

# config boundary *type* name  ->  plan boundary kind (a label, not a Tidy3D import)
BOUNDARY_PLAN_KIND = {
    "pml": "PML",
    "absorber": "Absorber",
    "periodic": "Periodic",
    "pec": "PECBoundary",
    "pmc": "PMCBoundary",
}
LAYERED_BOUNDARIES = ("pml", "absorber")

SOURCE_TOKEN_KINDS = ("mode",)
MONITOR_TOKEN_KINDS = ("flux", "field")

_BUNDLE_KEYS = (
    "schema",
    "identity",
    "geometry",
    "config",
    "materials",
    "background_medium_label",
    "discretization",
    "excitation",
)


class TranslationError(ValueError):
    """Raised when a study input cannot be translated into a linear plan."""


class MissingLinearEvidenceError(TranslationError):
    """Raised when a required linear value / dimension / evidence field is absent."""

    def __init__(self, problems: list[str]):
        self.problems = list(problems)
        super().__init__("; ".join(self.problems))


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _finite(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _finite_positive(value: object) -> bool:
    return _finite(value) and value > 0


def _finite_non_negative(value: object) -> bool:
    return _finite(value) and value >= 0


def _is_wavelength_range(value: object) -> bool:
    return (
        isinstance(value, (list, tuple))
        and len(value) == 2
        and all(_finite_positive(x) for x in value)
        and value[0] < value[1]
    )


def _covers(outer: object, inner: list[float]) -> bool:
    """True when the closed interval ``outer`` contains the closed interval ``inner``."""
    if not _is_wavelength_range(outer):
        return False
    return outer[0] <= inner[0] and inner[1] <= outer[1]


# --------------------------------------------------------------------------- #
# caller-supplied input records
# --------------------------------------------------------------------------- #
@dataclass
class LinearMediumValue:
    """One concrete linear medium, supplied by the caller.

    Unlike :class:`fdtd.provenance.schema.MaterialSource` (which stores *no*
    numbers), this record carries the actual linear values needed to build a
    Tidy3D ``Medium``. They must still be backed by external evidence: a
    SHA-256 ``evidence_digest`` of the artifact the numbers came from, a
    ``evidence_reference`` (DOI / library key) and the ``wavelength_range_um``
    over which the values are declared valid.
    """

    medium_label: str | None = None
    model: str | None = None                       # one of LINEAR_MEDIUM_MODELS
    relative_permittivity: float | None = None     # eps_r, > 0  (Tidy3D Medium.permittivity)
    conductivity: float | None = None              # S/m, >= 0   (Tidy3D Medium.conductivity)
    evidence_digest: str | None = None             # sha256 of the external value file
    evidence_reference: str | None = None          # DOI / datasheet id / library key
    wavelength_range_um: list[float] | None = None  # [lo, hi] validity window, caller-supplied

    def problems(self) -> list[str]:
        p: list[str] = []
        tag = self.medium_label if isinstance(self.medium_label, str) and self.medium_label.strip() else "<unlabelled>"
        if not isinstance(self.medium_label, str) or not self.medium_label.strip():
            p.append("medium_label is missing")
        if self.model not in LINEAR_MEDIUM_MODELS:
            p.append(f"{tag}: model {self.model!r} not in {list(LINEAR_MEDIUM_MODELS)}")
        if not _finite_positive(self.relative_permittivity):
            p.append(f"{tag}: relative_permittivity must be a finite number > 0, got {self.relative_permittivity!r}")
        if not _finite_non_negative(self.conductivity):
            p.append(f"{tag}: conductivity must be a finite number >= 0, got {self.conductivity!r}")
        if not looks_like_sha256(self.evidence_digest):
            p.append(f"{tag}: evidence_digest must be a sha256 hex digest of an external file")
        if not isinstance(self.evidence_reference, str) or not self.evidence_reference.strip():
            p.append(f"{tag}: evidence_reference is missing")
        if not _is_wavelength_range(self.wavelength_range_um):
            p.append(f"{tag}: wavelength_range_um must be [lo, hi] with 0 < lo < hi, got {self.wavelength_range_um!r}")
        return p

    def to_canonical_dict(self) -> dict:
        out = {}
        for f in fields(self):
            value = getattr(self, f.name)
            out[f.name] = list(value) if isinstance(value, tuple) else value
        return out

    def to_medium_document(self) -> dict:
        """The plan's medium object (maps onto ``tidy3d.Medium`` kwargs)."""
        return {
            "type": "Medium",
            "model": self.model,
            "permittivity": self.relative_permittivity,
            "conductivity": self.conductivity,
            "evidence": {
                "digest": self.evidence_digest,
                "reference": self.evidence_reference,
                "wavelength_range_um": list(self.wavelength_range_um)
                if isinstance(self.wavelength_range_um, (list, tuple))
                else self.wavelength_range_um,
            },
        }


@dataclass
class LinearMaterialTable:
    """The caller's table of concrete linear media, one entry per medium label."""

    entries: list[LinearMediumValue] = field(default_factory=list)

    def labels(self) -> list[str]:
        return [e.medium_label for e in self.entries if isinstance(e.medium_label, str)]

    def get(self, label: str) -> LinearMediumValue | None:
        for e in self.entries:
            if e.medium_label == label:
                return e
        return None

    def problems(self, required_labels: list[str]) -> list[str]:
        p: list[str] = []
        seen: set[str] = set()
        for e in self.entries:
            p.extend(f"material {q}" for q in e.problems())
            if isinstance(e.medium_label, str):
                if e.medium_label in seen:
                    p.append(f"material: duplicate entry for medium label {e.medium_label!r}")
                seen.add(e.medium_label)
        for label in required_labels:
            if self.get(label) is None:
                p.append(f"material: no linear value supplied for medium label {label!r}")
        return p


@dataclass
class ExcitationSpec:
    """Caller-supplied excitation band for the linear resonance sweep.

    Held in wavelength (micrometres). Conversion to a Tidy3D ``freq0`` /
    ``fwidth`` uses Tidy3D's own ``C_0`` and is left to the code that
    instantiates the real ``Simulation``; no speed of light is hard-coded here.
    """

    center_wavelength_um: float | None = None
    bandwidth_wavelength_um: float | None = None    # full spectral width, in wavelength
    num_freqs: int | None = None                    # monitor frequency samples across the band

    def band_um(self) -> list[float] | None:
        if not (_finite_positive(self.center_wavelength_um) and _finite_positive(self.bandwidth_wavelength_um)):
            return None
        half = self.bandwidth_wavelength_um / 2.0
        return [self.center_wavelength_um - half, self.center_wavelength_um + half]

    def problems(self) -> list[str]:
        p: list[str] = []
        if not _finite_positive(self.center_wavelength_um):
            p.append(f"excitation.center_wavelength_um must be a finite number > 0, got {self.center_wavelength_um!r}")
        if not _finite_positive(self.bandwidth_wavelength_um):
            p.append(
                f"excitation.bandwidth_wavelength_um must be a finite number > 0, got {self.bandwidth_wavelength_um!r}"
            )
        band = self.band_um()
        if band is not None and band[0] <= 0:
            p.append(
                f"excitation band {band!r} reaches non-positive wavelength; "
                "reduce bandwidth_wavelength_um or raise center_wavelength_um"
            )
        if not (isinstance(self.num_freqs, int) and not isinstance(self.num_freqs, bool) and self.num_freqs >= 1):
            p.append(f"excitation.num_freqs must be an integer >= 1, got {self.num_freqs!r}")
        return p

    def to_canonical_dict(self) -> dict:
        return {f.name: getattr(self, f.name) for f in fields(self)}


@dataclass
class DiscretizationSpec:
    """Caller-supplied discretisation for the linear plan.

    This layer does **not** choose a mesh, time step, PML depth, run time, or
    shutoff — those are Astra's convergence-ladder decisions. It only *accepts*
    an explicit set and fails closed when one is absent, so the emitted plan is
    a complete ``Simulation`` and not a half-form.
    """

    grid_min_steps_per_wavelength: float | None = None  # AutoGrid min_steps_per_wvl, > 0
    grid_wavelength_um: float | None = None             # the wavelength AutoGrid resolves against, > 0
    run_time_seconds: float | None = None              # Tidy3D run_time (seconds), > 0
    field_decay_shutoff: float | None = None           # Tidy3D shutoff, >= 0
    boundary_num_layers: int | None = None             # PML / Absorber layer count, >= 1

    def problems(self) -> list[str]:
        p: list[str] = []
        if not _finite_positive(self.grid_min_steps_per_wavelength):
            p.append(
                "discretization.grid_min_steps_per_wavelength must be a finite number > 0, "
                f"got {self.grid_min_steps_per_wavelength!r}"
            )
        if not _finite_positive(self.grid_wavelength_um):
            p.append(f"discretization.grid_wavelength_um must be a finite number > 0, got {self.grid_wavelength_um!r}")
        if not _finite_positive(self.run_time_seconds):
            p.append(f"discretization.run_time_seconds must be a finite number > 0, got {self.run_time_seconds!r}")
        if not _finite_non_negative(self.field_decay_shutoff):
            p.append(
                f"discretization.field_decay_shutoff must be a finite number >= 0, got {self.field_decay_shutoff!r}"
            )
        if not (
            isinstance(self.boundary_num_layers, int)
            and not isinstance(self.boundary_num_layers, bool)
            and self.boundary_num_layers >= 1
        ):
            p.append(f"discretization.boundary_num_layers must be an integer >= 1, got {self.boundary_num_layers!r}")
        return p

    def to_canonical_dict(self) -> dict:
        return {f.name: getattr(self, f.name) for f in fields(self)}


def _identity_problems(identity: StudyIdentity) -> list[str]:
    p: list[str] = []
    for name in ("study_id", "created_utc"):
        value = getattr(identity, name, None)
        if not isinstance(value, str) or not value.strip():
            p.append(f"identity.{name} is missing")
    return p


# --------------------------------------------------------------------------- #
# output plan
# --------------------------------------------------------------------------- #
@dataclass
class LinearSimulationPlan:
    """A deterministic, serialisable linear ``tidy3d.Simulation`` plan."""

    document: dict

    def to_document(self) -> dict:
        return self.document

    def digest(self) -> str:
        """SHA-256 of the canonical plan document."""
        return canonical_geometry_digest(self.document)

    def to_json(self) -> str:
        import json

        return json.dumps(self.document, indent=2, sort_keys=True) + "\n"

    def dry_run(self):
        from .linear_dryrun import dry_run

        return dry_run(self.document)


# --------------------------------------------------------------------------- #
# translator
# --------------------------------------------------------------------------- #
class LinearSimulationTranslator:
    """Turn a fully-evidenced MRR study input into a :class:`LinearSimulationPlan`."""

    def __init__(
        self,
        *,
        identity: StudyIdentity,
        geometry: RingResonatorGeometry,
        config: SimulationConfig,
        materials: LinearMaterialTable,
        background_medium_label: str,
        excitation: ExcitationSpec,
        discretization: DiscretizationSpec,
    ) -> None:
        self.identity = identity
        self.geometry = geometry
        self.config = config
        self.materials = materials
        self.background_medium_label = background_medium_label
        self.excitation = excitation
        self.discretization = discretization

    # -- construction from a single JSON-style bundle -------------------- #
    @classmethod
    def from_bundle(cls, data: dict) -> "LinearSimulationTranslator":
        if not isinstance(data, dict):
            raise TranslationError(f"bundle must be an object, got {type(data).__name__}")

        if any(k in data for k in ("nonlinear", "kerr", "tpa", "chi3", "free_carrier")):
            raise TranslationError(
                "this layer builds the LINEAR simulation only; a nonlinear block "
                "(nonlinear / kerr / tpa / chi3 / free_carrier) is out of scope and must not be passed here"
            )
        unknown = set(data) - set(_BUNDLE_KEYS)
        if unknown:
            raise TranslationError(f"bundle has unknown key(s): {sorted(unknown)}")
        if data.get("schema") not in (None, LINEAR_INPUT_SCHEMA_ID):
            raise TranslationError(
                f"bundle schema {data.get('schema')!r} != {LINEAR_INPUT_SCHEMA_ID!r}"
            )

        for required in ("geometry", "config", "materials", "background_medium_label",
                         "excitation", "discretization"):
            if required not in data:
                raise MissingLinearEvidenceError([f"bundle.{required} is missing"])

        try:
            geometry = RingResonatorGeometry(**data["geometry"])
        except TypeError as exc:
            raise TranslationError(f"bundle.geometry: {exc}") from exc
        try:
            config = SimulationConfig(**data["config"])
        except TypeError as exc:
            raise TranslationError(f"bundle.config: {exc}") from exc

        materials_raw = data["materials"]
        if not isinstance(materials_raw, list):
            raise TranslationError("bundle.materials must be a list of medium-value objects")
        entries: list[LinearMediumValue] = []
        for i, item in enumerate(materials_raw):
            if not isinstance(item, dict):
                raise TranslationError(f"bundle.materials[{i}] must be an object")
            try:
                entries.append(LinearMediumValue(**item))
            except TypeError as exc:
                raise TranslationError(f"bundle.materials[{i}]: {exc}") from exc

        try:
            excitation = ExcitationSpec(**data["excitation"])
        except TypeError as exc:
            raise TranslationError(f"bundle.excitation: {exc}") from exc
        try:
            discretization = DiscretizationSpec(**data["discretization"])
        except TypeError as exc:
            raise TranslationError(f"bundle.discretization: {exc}") from exc

        identity_raw = data.get("identity") or {}
        if not isinstance(identity_raw, dict):
            raise TranslationError("bundle.identity must be an object")
        try:
            identity = StudyIdentity(**identity_raw)
        except TypeError as exc:
            raise TranslationError(f"bundle.identity: {exc}") from exc

        bg = data["background_medium_label"]
        if not isinstance(bg, str) or not bg.strip():
            raise MissingLinearEvidenceError(["bundle.background_medium_label is missing"])

        return cls(
            identity=identity,
            geometry=geometry,
            config=config,
            materials=LinearMaterialTable(entries=entries),
            background_medium_label=bg,
            excitation=excitation,
            discretization=discretization,
        )

    # -- geometry-derived quantities --------------------------------- #
    def _stack_top_um(self) -> float:
        g = self.geometry
        return (
            g.substrate_thickness_um
            + g.box_thickness_um
            + g.waveguide_thickness_um
            + g.cladding_thickness_um
        )

    def _domain_center_um(self) -> list[float]:
        return [0.0, 0.0, self._stack_top_um() / 2.0]

    def _geometry_medium_labels(self) -> list[str]:
        g = self.geometry
        return [g.core_medium, g.cladding_medium, g.box_medium, g.substrate_medium]

    def required_medium_labels(self) -> list[str]:
        labels: list[str] = []
        for label in self._geometry_medium_labels() + [self.background_medium_label]:
            if isinstance(label, str) and label not in labels:
                labels.append(label)
        return labels

    def _waveguide_structure_names(self) -> list[str]:
        return [s["name"] for s in self.geometry.to_structures() if s["kind"] in ("waveguide", "ring")]

    def _port_structure_center_um(self, structure: str) -> list[float]:
        """Centre ``[x, y, z]`` of the ring / bus primitive a port token names.

        A port plane's coordinates *off* its injection axis are taken from
        here, so ``flux:bus_drop:out`` sits on the drop-bus centreline rather
        than on the domain axis. Only ``waveguide`` / ``ring`` primitives carry
        a centre; anything else fails closed (the token gate in
        :meth:`_port_problems` already rejects such tokens, so this is a
        defensive backstop, not a user-facing path).
        """
        for s in self.geometry.to_structures():
            if s.get("name") == structure and s.get("kind") in ("waveguide", "ring"):
                center = s.get("center_um")
                if isinstance(center, (list, tuple)) and len(center) == 3:
                    return [float(c) for c in center]
        raise TranslationError(
            f"port token references structure {structure!r}, which carries no "
            "centre to place the port plane on"
        )

    # -- fail-closed evidence gate --------------------------------- #
    def evidence_problems(self) -> list[str]:
        problems: list[str] = []
        problems.extend(_identity_problems(self.identity))
        problems.extend(f"geometry: {q}" for q in self.geometry.problems())
        problems.extend(f"config: {q}" for q in self.config.problems())
        problems.extend(self.discretization.problems())
        problems.extend(self.excitation.problems())

        if not isinstance(self.background_medium_label, str) or not self.background_medium_label.strip():
            problems.append("background_medium_label is missing")
        elif self.background_medium_label not in self._geometry_medium_labels():
            problems.append(
                f"background_medium_label {self.background_medium_label!r} is not one of the geometry "
                f"medium labels {self._geometry_medium_labels()!r}"
            )

        problems.extend(self.materials.problems(self.required_medium_labels()))

        # wavelength-band consistency (only when the pieces are individually sane)
        band = self.excitation.band_um()
        if band is not None and band[0] > 0:
            if not _covers(self.config.wavelength_range_um, band):
                problems.append(
                    f"excitation band {band!r} is not inside config.wavelength_range_um "
                    f"{self.config.wavelength_range_um!r}"
                )
            for label in self.required_medium_labels():
                mv = self.materials.get(label)
                if mv is not None and _is_wavelength_range(mv.wavelength_range_um) and not _covers(
                    mv.wavelength_range_um, band
                ):
                    problems.append(
                        f"excitation band {band!r} is outside the validity window of medium "
                        f"{label!r} ({mv.wavelength_range_um!r})"
                    )

        problems.extend(self._port_problems())
        return problems

    def _port_problems(self) -> list[str]:
        problems: list[str] = []
        wg_names = set(self._waveguide_structure_names())
        geom_ok = not self.geometry.problems()
        for label, seq, allowed in (
            ("sources", self.config.sources, SOURCE_TOKEN_KINDS),
            ("monitors", self.config.monitors, MONITOR_TOKEN_KINDS),
        ):
            if not isinstance(seq, (list, tuple)):
                continue
            for tok in seq:
                parsed = _parse_token(tok)
                if parsed is None:
                    problems.append(f"{label}: token {tok!r} is not '<kind>:<structure>:<port>'")
                    continue
                kind, structure, port = parsed
                token_ok = True
                if kind not in allowed:
                    problems.append(f"{label}: token {tok!r} kind {kind!r} not in {list(allowed)}")
                    token_ok = False
                if wg_names and structure not in wg_names:
                    problems.append(
                        f"{label}: token {tok!r} references structure {structure!r} "
                        f"not in {sorted(wg_names)}"
                    )
                    token_ok = False
                # The derived plane can only be checked once the token names a
                # real waveguide/ring and the geometry itself is well formed.
                if token_ok and wg_names and geom_ok:
                    try:
                        plane = self._port_plane(structure, port)
                    except TranslationError as exc:
                        problems.append(f"{label}: token {tok!r}: {exc}")
                        continue
                    problems.extend(self._port_plane_problems(structure, port, plane))
        return problems

    def require_evidence(self) -> None:
        problems = self.evidence_problems()
        if problems:
            raise MissingLinearEvidenceError(problems)

    # -- plan assembly -------------------------------------------- #
    def _structure_documents(self) -> list[dict]:
        out: list[dict] = []
        for s in self.geometry.to_structures():
            entry = dict(s)
            label = entry.pop("medium")
            mv = self.materials.get(label)
            entry["medium_label"] = label
            entry["medium"] = mv.to_medium_document() if mv is not None else None
            out.append(entry)
        return out

    def _port_plane(self, structure: str, port: str) -> dict:
        # The bus runs along x (the injection axis): the ``in`` / ``out`` faces
        # sit half a bus length either side of the structure centre. The two
        # transverse coordinates are taken from that same structure centre, so a
        # through-bus port and a drop-bus port land on their own centrelines
        # (different y) rather than both on the domain axis. x stays a padding
        # margin inside the domain edge, so the plane never falls in the PML.
        #
        # The transverse *size* is derived mechanically from the named bus
        # geometry, not from the whole domain: a full-domain cross section pulls
        # in every other guide's power and the substrate/cladding slabs, which
        # invalidated the linear resonance acceptance. The plane spans the bus
        # waveguide cross section plus one ``domain_padding_um`` margin on each
        # side. These lengths are geometry/padding values the caller already
        # supplied; nothing here is a physical constant or an invented inset.
        g = self.geometry
        center = self._port_structure_center_um(structure)
        half = g.bus_length_um / 2.0
        x = center[0] - half if port == "in" else center[0] + half
        pad2 = 2.0 * g.domain_padding_um
        return {
            "injection_axis": "x",
            "direction": "+" if port == "in" else "-",
            "plane_center_um": [x, center[1], center[2]],
            "plane_size_um": [
                0.0,
                g.bus_waveguide_width_um + pad2,
                g.waveguide_thickness_um + pad2,
            ],
        }

    def _port_plane_problems(self, structure: str, port: str, plane: dict) -> list[str]:
        """Fail-closed geometry check for one derived port plane.

        The plane must stay inside the simulation domain and keep its injection
        face out of the ``domain_padding_um`` boundary margin (where the PML /
        Absorber lives), otherwise the source launches / the monitor integrates
        inside the absorbing layer and the linear result is meaningless.
        """
        problems: list[str] = []
        size = self.geometry.domain_size_um()
        pad = self.geometry.domain_padding_um
        tag = f"port plane {structure}:{port}"
        tol = 1e-9

        cx, cy, cz = plane["plane_center_um"]
        sx, sy, sz = plane["plane_size_um"]

        if sx != 0.0:
            problems.append(f"{tag}: injection-axis extent must be 0, got {sx!r}")
        if not _finite_positive(sy) or not _finite_positive(sz):
            problems.append(
                f"{tag}: transverse extents must be finite and > 0, got y={sy!r}, z={sz!r}"
            )
        if problems:
            return problems

        # injection face: outside the boundary margin on x
        if abs(cx) > size[0] / 2.0 - pad + tol:
            problems.append(
                f"{tag}: injection face x={cx:g} um is inside the {pad:g} um boundary "
                f"margin (require |x| <= {size[0] / 2.0 - pad:g})"
            )
        # transverse plane: fully inside the domain box
        if abs(cy) + sy / 2.0 > size[1] / 2.0 + tol:
            problems.append(
                f"{tag}: transverse y span [{cy - sy / 2.0:g}, {cy + sy / 2.0:g}] um "
                f"leaves the domain (|y| <= {size[1] / 2.0:g})"
            )
        if cz - sz / 2.0 < -tol or cz + sz / 2.0 > size[2] + tol:
            problems.append(
                f"{tag}: vertical z span [{cz - sz / 2.0:g}, {cz + sz / 2.0:g}] um "
                f"leaves the domain [0, {size[2]:g}]"
            )
        return problems

    def _source_documents(self) -> list[dict]:
        docs: list[dict] = []
        for tok in self.config.sources:
            kind, structure, port = _parse_token(tok)
            plane = self._port_plane(structure, port)
            docs.append(
                {
                    "type": "ModeSource",
                    "token": tok,
                    "on_structure": structure,
                    "port": port,
                    **plane,
                    "pulse": {
                        "type": "GaussianPulse",
                        "center_wavelength_um": self.excitation.center_wavelength_um,
                        "bandwidth_wavelength_um": self.excitation.bandwidth_wavelength_um,
                    },
                }
            )
        return docs

    def _monitor_documents(self) -> list[dict]:
        docs: list[dict] = []
        for tok in self.config.monitors:
            kind, structure, port = _parse_token(tok)
            plane = self._port_plane(structure, port)
            docs.append(
                {
                    "type": "FluxMonitor" if kind == "flux" else "FieldMonitor",
                    "token": tok,
                    "on_structure": structure,
                    "port": port,
                    "injection_axis": plane["injection_axis"],
                    "plane_center_um": plane["plane_center_um"],
                    "plane_size_um": plane["plane_size_um"],
                    "sampling": {
                        "center_wavelength_um": self.excitation.center_wavelength_um,
                        "bandwidth_wavelength_um": self.excitation.bandwidth_wavelength_um,
                        "num_freqs": self.excitation.num_freqs,
                    },
                }
            )
        return docs

    def _boundary_spec(self) -> dict:
        out: dict = {}
        for axis, name in sorted(self.config.boundary_types.items()):
            out[axis] = {
                "config_type": name,
                "kind": BOUNDARY_PLAN_KIND.get(name),
                "num_layers": self.discretization.boundary_num_layers if name in LAYERED_BOUNDARIES else 0,
            }
        return out

    def _material_evidence(self) -> dict:
        out: dict = {}
        for label in self.required_medium_labels():
            mv = self.materials.get(label)
            if mv is None:
                continue
            out[label] = {
                "digest": mv.evidence_digest,
                "reference": mv.evidence_reference,
                "wavelength_range_um": list(mv.wavelength_range_um)
                if isinstance(mv.wavelength_range_um, (list, tuple))
                else mv.wavelength_range_um,
            }
        return out

    def build_document(self) -> dict:
        """Assemble the canonical plan document. Fails closed on missing evidence."""
        self.require_evidence()

        size = self.geometry.domain_size_um()
        bg = self.materials.get(self.background_medium_label)

        return {
            "schema": LINEAR_SIM_SCHEMA_ID,
            "tidy3d_target": "tidy3d.Simulation",
            "linearity": "linear",
            "units": {"length": "um", "time": "s"},
            "domain": {"size_um": size, "center_um": self._domain_center_um()},
            "grid_spec": {
                "type": "AutoGrid",
                "min_steps_per_wavelength": self.discretization.grid_min_steps_per_wavelength,
                "wavelength_um": self.discretization.grid_wavelength_um,
            },
            "run_time_s": self.discretization.run_time_seconds,
            "field_decay_shutoff": self.discretization.field_decay_shutoff,
            "boundary_spec": self._boundary_spec(),
            "symmetry": list(self.config.symmetry),
            "background_medium": bg.to_medium_document() if bg is not None else None,
            "structures": self._structure_documents(),
            "sources": self._source_documents(),
            "monitors": self._monitor_documents(),
            "inputs": {
                "identity": {
                    "study_id": self.identity.study_id,
                    "created_utc": self.identity.created_utc,
                    "notes": self.identity.notes,
                },
                "geometry_document": self.geometry.to_document(),
                "config": self.config.to_canonical_dict(),
                "discretization": self.discretization.to_canonical_dict(),
                "excitation": self.excitation.to_canonical_dict(),
                "materials": [mv.to_canonical_dict() for mv in self.materials.entries],
                "background_medium_label": self.background_medium_label,
            },
            "provenance": {
                "study_id": self.identity.study_id,
                "created_utc": self.identity.created_utc,
                "geometry_hash": self.geometry.digest(),
                "config_hash": self.config.digest(),
                "material_evidence": self._material_evidence(),
                "linear_only": True,
                "nonlinear": None,
                "cloud": {
                    "uploaded": False,
                    "estimated": False,
                    "started": False,
                    "monitored": False,
                    "downloaded": False,
                    "task_ids": [],
                    "flex_credit": None,
                },
            },
        }

    def translate(self) -> LinearSimulationPlan:
        return LinearSimulationPlan(document=self.build_document())


# --------------------------------------------------------------------------- #
# token helper
# --------------------------------------------------------------------------- #
def _parse_token(token: object) -> tuple[str, str, str] | None:
    if not isinstance(token, str):
        return None
    parts = token.split(":")
    if len(parts) != 3 or any(p.strip() == "" for p in parts):
        return None
    return parts[0], parts[1], parts[2]
